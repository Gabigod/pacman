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

        self.animacaoIndex = 0.0  # Índice para animação futura
        self.animacaoSpeed = 0.15  # Velocidade da animação futura

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
        self.vidas = 3
        self.pontos = 0
        self.invencivel = False
        self.visivel = True
        self.timerPiscar = 0
        self.proximaDirecao = (0, 0)  # Direção que o jogador quer ir
        self.invencivelTimer = 0  # 0 indica que está vulnerável
        self.parpadeoToggle = False
        # Carrega as sprites do Pacman
        # Assume-se: (0,0) Fechado, (16,0) Aberto, (32,0) Muito Aberto
        self.sprites = []
        if sheet:
            # Cria a sequência: Fechado -> Meio -> Aberto -> Meio
            s0 = self.getSprite(sheet, 0, 0)  # Fechado
            s1 = self.getSprite(sheet, 16, 0)  # Meio
            s2 = self.getSprite(sheet, 32, 0)  # Aberto
            self.sprites = [s0, s1, s2, s1]
        else:
            self.sprites = [None]

        self.imagem = self.sprites[0]
        self.animacaoSpeed = 0.3  # Pacman mastiga rápido

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
        # --- SISTEMA DE INVENCIBILIDADE ---
        if self.invencivel:
            self.invencivelTimer -= 1

            # alterna invisível / visível a cada 10 frames
            if self.invencivelTimer % 10 == 0:
                self.parpadeoToggle = not self.parpadeoToggle

            # acabou a invencibilidade
            if self.invencivelTimer <= 0:
                self.invencivel = False
                self.parpadeoToggle = False

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

        # LÓGICA DA ANIMAÇÃO DO PACMAN
        # Só anima se estiver se movendo
        if self.direcao != (0, 0) and self.sprites:
            self.animacaoIndex += self.animacaoSpeed
            if self.animacaoIndex >= len(self.sprites):
                self.animacaoIndex = 0.0

        # Seleciona o frame base
        idx = int(self.animacaoIndex)
        spriteBase = self.sprites[idx] if idx < len(self.sprites) else self.sprites[0]

        # Rotaciona a sprite conforme a direção
        if spriteBase:
            angulo = 0
            if self.direcao == (-1, 0):
                angulo = 180  # Esquerda
            elif self.direcao == (0, -1):
                angulo = 90  # Cima
            elif self.direcao == (0, 1):
                angulo = 270  # Baixo
            self.imagem = pygame.transform.rotate(
                spriteBase, angulo
            )  # Gira a partir da original conforme o angulo
    def desenhar(self, tela):
        # Se estiver invencível e for um frame "invisível", NÃO desenha
        if self.invencivel and self.parpadeoToggle:
            return

        # Caso contrário, desenha normalmente
        tela.blit(self.imagem, self.rect)
    def morrer(self):
        # perde 1 vida
        self.vidas -= 1

        # se acabou vidas → retorna True (game over)
        if self.vidas <= 0:
            return True

        # caso contrário, reinicia pacman e liga invencibilidade
        self.rect.x = self.xInicio * TILE_SIZE
        self.rect.y = self.yInicio * TILE_SIZE
        self.direcao = (0, 0)
        self.invencivel = True
        self.invencivelTimer = 120  # 2 segundos invencível
        self.parpadeoToggle = False

        return False
   


# Subclasse específica para os Fantasmas
class Fantasma(Entidade):
    # Construtor do objeto Fantasma
    def __init__(self, x: int, y: int, sheet=None) -> None:
        super().__init__(x, y)
        self.tempoPreso = 300  # 300 frames preso na casa dos fantasmas
        self.assustado = False  # Flag para estado assustado
        self.tempoAssustado = 0  # 0 indica que está normal
        self.speed = VELOCIDADE - 1  # Fantasmas são um pouco mais lentos que o Pacman

        # Carrega animações
        self.framesNormal = []
        self.framesAssustado = []

        if sheet:
            # Normal (Vermelho): (0, 64) e (16, 64)
            self.framesNormal = [
                self.getSprite(sheet, 0, 64),
                self.getSprite(sheet, 16, 64),
            ]
            # Assustado (Azul): (128, 64) e (144, 64)
            self.framesAssustado = [
                self.getSprite(sheet, 128, 64),
                self.getSprite(sheet, 144, 64),
            ]
            self.imagem = self.framesNormal[0]

    # Metodo para atualizar a sprite baseada no estado
    def atualizarSprite(self) -> None:
        self.animacaoIndex += self.animacaoSpeed

        if self.assustado:
            conjunto = self.framesAssustado
        else:
            conjunto = self.framesNormal

        if conjunto:
            idx = int(self.animacaoIndex) % len(conjunto)
            self.imagem = conjunto[idx]

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
        # Atualiza a sprite antes de processar a lógica
        self.atualizarSprite()
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
