from config import TILE_SIZE, VELOCIDADE, PRETO
from mapa import Mapa
from collections import deque  # Necessario para o BFS
import pygame
import random


# TAD para representar as entidades do jogo
class Entidade:
    # Construtor da entidade
    def __init__(self, x: int, y: int) -> None:
        self.xGrid = x  # Posição na grade (Coluna)
        self.yGrid = y  # Posição na grade (Linha)
        # Posição fixa para resetar caso morra
        self.xInicio = x
        self.yInicio = y

        # Posicão em pixels para renderização
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        self.direcao = (0, 0)  # Vetor que aponta o movimento (1,0) é direita
        self.speed = VELOCIDADE

        # Atributos visuais
        self.imagem = None
        self.corFallback = (255, 0, 0)  # Cor vermelha como fallback

    # Reorna a posição atual na grade baseada no centro do rect
    def getPosGrad(self) -> int:
        cx = self.rect.centerx // TILE_SIZE
        cy = self.rect.centery // TILE_SIZE
        return cx, cy

    # Verifica se a entidade está perfeitamente centralizada no tile
    def esta_centralizado(self) -> bool:
        return (self.rect.x % TILE_SIZE == 0) and (self.rect.y % TILE_SIZE == 0)

    # Metodo para verificar se a entidade pode se mover para a posição (x, y)
    def podeMover(self, mapa: Mapa, x: int, y: int) -> bool:
        if x < 0 or x >= mapa.col or y < 0 or y >= mapa.lin:
            return False  # Fora dos limites do mapa
        if mapa.matriz[y][x] == "#":
            return False  # Paredes bloqueiam o movimento
        return True

    # Movimento básico contínuo
    def mover_fisica(self) -> None:
        self.rect.x += self.direcao[0] * self.speed
        self.rect.y += self.direcao[1] * self.speed

        # Atualiza a referência da grade para lógica do jogo
        self.xGrid, self.yGrid = self.getPosGrad()

    # Recorta e retorna uma sprite da folha de sprites.
    def getSprite(self, sheet, x, y, w=16, h=16):
        if sheet is None:
            return None
        sprite = pygame.Surface((w, h))
        sprite.blit(sheet, (0, 0), (x, y, w, h))
        sprite.set_colorkey(PRETO)  # Define o preto como transparente
        return pygame.transform.scale(sprite, (TILE_SIZE, TILE_SIZE))


# Subclasse específica para o Pacman
class Pacman(Entidade):
    def __init__(self, x: int, y: int, sheet=None) -> None:
        super().__init__(x, y)
        self.tempoInvencivel = 0  # 0 indica que está vulnerável
        self.vidas = 3
        self.pontos = 0
        self.proximaDirecao = (0, 0)  # Direção que o jogador quer ir
        self.corFallback = (255, 255, 0)  # Cor amarela como fallback

        # Carrega a sprite do Pacman
        self.spriteOriginal = self.getSprite(sheet, 16, 0)
        self.imagem = self.spriteOriginal  # TO-DO: Animação futura

    # Chamado pelo evento de teclado para definir a direção desejada
    def processarEvento(self, key):
        if key == pygame.K_UP:
            self.proximaDirecao = (0, -1)
        elif key == pygame.K_DOWN:
            self.proximaDirecao = (0, 1)
        elif key == pygame.K_LEFT:
            self.proximaDirecao = (-1, 0)
        elif key == pygame.K_RIGHT:
            self.proximaDirecao = (1, 0)

    # Lógica principal de movimento do Pacman (chamada a cada frame)
    def update(self, mapa: Mapa) -> None:
        # Verifica se está centralizado para mudar de direção
        if self.esta_centralizado():
            xGrid, yGrid = self.getPosGrad()

            # Tenta mudar para a próxima direção desejada
            novaX = xGrid + self.proximaDirecao[0]
            novaY = yGrid + self.proximaDirecao[1]
            if self.podeMover(mapa, novaX, novaY):
                self.direcao = self.proximaDirecao

            # Verifica se pode continuar na direção atual
            novaX = xGrid + self.direcao[0]
            novaY = yGrid + self.direcao[1]
            if not self.podeMover(mapa, novaX, novaY):
                self.direcao = (0, 0)  # Para se não puder continuar

        # Move o Pacman fisicamente
        self.mover_fisica()

        # Atualiza a rotação da sprite baseada na direção
        if self.spriteOriginal:
            angulo = 0
            if self.direcao == (-1, 0):
                angulo = 180  # Esquerda
            elif self.direcao == (0, -1):
                angulo = 90  # Cima
            elif self.direcao == (0, 1):
                angulo = 270  # Baixo
            self.imagem = pygame.transform.rotate(
                self.spriteOriginal, angulo
            )  # Gira a partir da original conforme o angulo


# Subclasse específica para os Fantasmas
class Fantasma(Entidade):
    # Construtor do objeto Fantasma
    def __init__(self, x: int, y: int, sheet=None) -> None:
        super().__init__(x, y)
        self.tempoPreso = 300  # 300 frames preso na casa dos fantasmas
        self.assustado = False  # Flag para estado assustado
        self.tempoAssustado = 0  # 0 indica que está normal
        self.speed = VELOCIDADE - 1  # Fantasmas são um pouco mais lentos que o Pacman

        # Carrega as sprites específicas dos fantasmas
        self.spriteNormal = self.getSprite(sheet, 0, 64)  # Vermelho
        self.spriteAssustado = self.getSprite(sheet, 128, 64)  # Azul (assustado)
        self.imagem = self.spriteNormal

    # Implementação do algoritmo BFS para encontrar o caminho até o pacman
    def bfsProx(self, mapa: Mapa, alvoX: int, alvoY: int) -> None:
        inicio = (self.xGrid, self.yGrid)
        meta = (alvoX, alvoY)

        # Se já está na posição do alvo, não faz nada
        if inicio == meta:
            return None

        fila = deque([inicio])
        came_from = {inicio: None}
        visitados = {inicio}

        encontrou = False

        while fila:
            atual = fila.popleft()
            if atual == meta:
                encontrou = True
                break

            cx, cy = atual
            vizinhos = [
                (cx, cy - 1),
                (cx, cy + 1),
                (cx - 1, cy),
                (cx + 1, cy),
            ]  # Cima, Baixo, Esquerda, Direita

            for nx, ny in vizinhos:
                # Checa se o vizinho está dentro dos limites do mapa e é visitável
                if (0 <= nx < mapa.col) and (0 <= ny < mapa.lin):
                    if mapa.matriz[ny][nx] != "#" and (nx, ny) not in visitados:
                        fila.append((nx, ny))
                        visitados.add((nx, ny))
                        came_from[(nx, ny)] = atual

        if not encontrou:
            return None  # Não encontrou caminho

        # Reconstrói o caminho do alvo até o início
        passo = meta
        while came_from[passo] != inicio:
            passo = came_from[passo]

        return passo  # Retorna o próximo passo na direção do alvo

    # Atualização do movimento do fantasma
    def update(self, mapa: Mapa, pacman: Pacman) -> None:
        # Verifica se está preso
        if self.tempoPreso > 0:
            self.tempoPreso -= 1
            return  # Ainda preso na casa dos fantasmas

        # Verifica se está centralizado para decidir o próximo movimento
        if self.esta_centralizado():
            if self.assustado:
                # inversão do alvo → fugir do Pacman
                alvoX = (self.xGrid * 2) - pacman.xGrid
                alvoY = (self.yGrid * 2) - pacman.yGrid
                prox = self.bfsProx(mapa, alvoX, alvoY)
            else:
                prox = self.bfsProx(mapa, pacman.xGrid, pacman.yGrid)

            if prox:
                px, py = prox
                dx = px - self.xGrid
                dy = py - self.yGrid
                self.direcao = (dx, dy)
            else:
                vizinhos = mapa.vizinhos(self.xGrid, self.yGrid)
                if vizinhos:
                    px, py = random.choice(
                        vizinhos
                    )  # Se BFS retornou None, escolhe um vizinho aleatório para seguir
                    self.direcao = (px - self.xGrid, py - self.yGrid)
        self.mover_fisica()
