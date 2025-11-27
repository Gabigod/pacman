import pygame
from enum import Enum
import os
from collections import deque  # Necessário para o BFS

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AMARELO = (255, 255, 0)
AZUL = (0, 0, 255)
VERMELHO = (255, 0, 0)

TILE_SIZE = 32  # Tamanho do tile em pixels
VELOCIDADE = 2


# Enum do jogo
class estadoJogo(Enum):
    MENU = 0
    GAMEPLAY = 1
    GAMEOVER = 2
    VITORIA = 3
    DERROTA = 4
    RANKING = 5



# TAD para representar o mapa do jogo
class Mapa:
    # Construtor da classe mapa que recebe o arquivo .txt
    def __init__(self, arquivo: str) -> None:
        # Atributos da classe
        self.lin = 0
        self.col = 0
        self.matriz = []
        self.posicaoInicialPacman = None       # Posição inicial do Pacman
        self.posicaoInicialFantasmas = []      # Lista de fantasmas
        self.posicaoPowerUp = None             # Power-up (0)
        self.carregarMapa(arquivo)

    # Método para carregar o mapa a partir de um arquivo .txt
    def carregarMapa(self, arquivo: str) -> None:

        # Reset das estruturas
        self.posicaoInicialPacman = None
        self.posicaoInicialFantasmas = []
        self.posicaoPowerUp = None
        self.matriz = []

        # Verifica se o arquivo existe
        if not os.path.exists(arquivo):
            print(f"ERRO: O arquivo '{arquivo}' não foi encontrado.")
            return None

        try:
            with open(arquivo, "r", encoding="utf-8") as arq:

                # Ler primeira linha com dimensões
                dim = arq.readline()
                if dim:
                    dims = dim.strip().split()
                    self.lin = int(dims[0])
                    self.col = int(dims[1])
                    print(f"Dimensões do mapa: {self.lin} x {self.col}")

                # Leitura das linhas seguintes
                linha_index = 0
                for linha in arq:
                    linhaLimpa = linha.rstrip("\n")
                    if not linhaLimpa:
                        continue

                    listaChars = list(linhaLimpa)

                    # Analisa cada caractere da linha
                    for j, char in enumerate(listaChars):

                        # PACMAN (4 direções possíveis no TXT)
                        if char in ["<", ">", "^", "v"]:
                            print(f"PACMAN ENCONTRADO EM: ({j}, {linha_index})")
                            self.posicaoInicialPacman = (j, linha_index)
                            listaChars[j] = "."  # Pacman começa sobre um ponto

                        # FANTASMA
                        elif char == "F":
                            print(f"FANTASMA ENCONTRADO EM: ({j}, {linha_index})")
                            self.posicaoInicialFantasmas.append((j, linha_index))
                            listaChars[j] = " "  # Fantasma não é chão nem ponto

                        # POWER-UP (o caractere '0')
                        elif char == "0":
                            print(f"POWER-UP ENCONTRADO EM: ({j}, {linha_index})")
                            self.posicaoPowerUp = (j, linha_index)
                            listaChars[j] = "."  # Fica como ponto no mapa

                    # Linha final sem entidades
                    self.matriz.append(listaChars)
                    linha_index += 1

        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")


    # Método que recebe a posição (x,y) do mapa e retorna uma lista de adjancência dos vizinhos possíveis de se visitar
    def vizinhos(self, x: int, y: int) -> list:
        # Verifica se a posição está dentro dos limites do mapa
        if x < 0 or x >= self.col or y < 0 or y >= self.lin:
            return []  # Fora dos limites do mapa
        if self.matriz[y][x] == "#":
            return []  # Paredes não têm vizinhos visitáveis

        # Se chegou aqui, a posição é válida
        vizinhos = []
        vizinhosPotenciais = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]

        for nx, ny in vizinhosPotenciais:
            if self.matriz[ny][nx] != "#":
                vizinhos.append((nx, ny))

        return vizinhos

    # Metodo para atualizar o conteúdo da matriz do mapa
    def atualizarConteudo(self, x: int, y: int, novoChar: str) -> None:
        self.matriz[y][x] = novoChar


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

    # Reorna a posição atual na grade baseada no centro do rect
    def getPosGrad(self):
        cx = self.rect.centerx // TILE_SIZE
        cy = self.rect.centery // TILE_SIZE
        return cx, cy

    # Verifica se a entidade está perfeitamente centralizada no tile
    def esta_centralizado(self):
        return (self.rect.x % TILE_SIZE == 0) and (self.rect.y % TILE_SIZE == 0)

    # Metodo para verificar se a entidade pode se mover para a posição (x, y)
    def podeMover(self, mapa: Mapa, x: int, y: int) -> bool:
        if x < 0 or x >= mapa.col or y < 0 or y >= mapa.lin:
            return False  # Fora dos limites do mapa
        if mapa.matriz[y][x] == "#":
            return False  # Paredes bloqueiam o movimento
        return True

    # Movimento básico contínuo
    def mover_fisica(self):
        self.rect.x += self.direcao[0] * self.speed
        self.rect.y += self.direcao[1] * self.speed

        # Atualiza a referência da grade para lógica do jogo
        self.xGrid, self.yGrid = self.getPosGrad()



# Subclasse específica para o Pacman
class Pacman(Entidade):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.tempoInvencivel = 0  # 0 indica que está vulnerável
        self.vidas = 3
        self.pontos = 0
        self.proximaDirecao = (0, 0)  # Direção que o jogador quer ir

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


# Subclasse específica para os Fantasmas
class Fantasma(Entidade):
    # Construtor do objeto Fantasma
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.tempoLivre = 0  # 0 indica que está preso na casa dos fantasmas
        self.assustado = False #
        self.tempoAssustado = 0  # 0 indica que está normal
        self.speed = VELOCIDADE - 1  # Fantasmas são um pouco mais lentos que o Pacman

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
        # Verifica se está livre para se mover
        if self.tempoLivre > 0:
            self.tempoLivre -= 1
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
                self.direcao = (0, 0)  # Não encontrou caminho
        self.mover_fisica()


class Jogo:
    def __init__(self) -> None:
        self.estado = estadoJogo.MENU
        # Carrega o mapa
        self.mapa = Mapa("fase2.txt")

        # Configuração da tela
        self.larguraTela = self.mapa.col * TILE_SIZE
        self.alturaTela = self.mapa.lin * TILE_SIZE
        self.tela = pygame.display.set_mode((self.larguraTela, self.alturaTela))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()

        # Instancia o objeto pacman com as coordenadas lidas durante o carregamento do mapa
        px, py = self.mapa.posicaoInicialPacman
        self.pacman = Pacman(px, py)

        # Instancia os fantasmas nas posições iniciais lidas durante o carregamento do mapa
        self.fantasmas = []
        self.powerupAtivo = False
        self.powerupTimer = 0

        for fx, fy in self.mapa.posicaoInicialFantasmas:
            fantasma = Fantasma(fx, fy)
            self.fantasmas.append(fantasma)

    # Método para desenhar o estado atual do jogo
    def desenhar(self) -> None:
        self.tela.fill(PRETO)

        for i in range(self.mapa.lin):
            for j in range(self.mapa.col):
                char = self.mapa.matriz[i][j]
            
                x = j * TILE_SIZE
                y = i * TILE_SIZE

                if char == "#":
                    pygame.draw.rect(self.tela, AZUL, (x, y, TILE_SIZE, TILE_SIZE))
                elif char == ".":
                    pygame.draw.circle(
                        self.tela, BRANCO, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 4
                    )
                elif char == "0":
                    pygame.draw.circle(
                        self.tela, BRANCO, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 8
                    )

        # Desenha o Pacman
        pygame.draw.circle(self.tela, AMARELO, self.pacman.rect.center, TILE_SIZE // 2)

        # Desenha todos os fantasmas
        for fantasma in self.fantasmas:
            corFantasma = AZUL if fantasma.assustado else VERMELHO
            pygame.draw.circle(
                self.tela,
                corFantasma,
                fantasma.rect.center,
                TILE_SIZE // 2,
            )



        pygame.display.flip()

    # Método principal para executar o jogo
    def executar(self) -> None:
        rodando = True
        while rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                    pygame.quit()
                    return
                # Input do Pacman
                if evento.type == pygame.KEYDOWN:
                    self.pacman.processarEvento(evento.key)

            # Lógica de atualização do jogo
            self.pacman.update(self.mapa)

            for fantasma in self.fantasmas:
                fantasma.update(self.mapa, self.pacman)

                # Colisão (usando colisão de retângulos do Pygame)
                # Reduzimos um pouco o rect para a colisão não ser injusta nas bordas
                hitbox_pacman = self.pacman.rect.inflate(-10, -10)
                hitbox_fantasma = fantasma.rect.inflate(-10, -10)

                if hitbox_pacman.colliderect(hitbox_fantasma):
                    if fantasma.assustado:
                        # Pacman come o fantasma
                        self.pacman.pontos += 200
                        fantasma.rect.x = fantasma.xInicio * TILE_SIZE
                        fantasma.rect.y = fantasma.yInicio * TILE_SIZE
                        fantasma.assustado = False
                        fantasma.speed = VELOCIDADE - 1
                    else:
                        print("Game Over!")
                        rodando = False


            # Lógica de comer pontos (baseada na grade)
            if self.pacman.esta_centralizado():
                px, py = self.pacman.getPosGrad()
                item = self.mapa.matriz[py][px]

                if item == ".":
                    self.mapa.matriz[py][px] = " "
                    self.pacman.pontos += 10

                elif item == "0":  # POWERUP
                    self.mapa.matriz[py][px] = " "
                    self.pacman.pontos += 50

                    # Ativa powerup
                    self.powerupAtivo = True
                    self.powerupTimer = 8 * 60  # 8 segundos a 60 FPS

                    # Deixa todos os fantasmas assustados
                    for f in self.fantasmas:
                        f.assustado = True
                        f.speed = 1  # mais lentos

            # Timer do powerup
            if self.powerupAtivo:
                self.powerupTimer -= 1
                if self.powerupTimer <= 0:
                    self.powerupAtivo = False
                    for f in self.fantasmas:
                        f.assustado = False
                        f.speed = VELOCIDADE - 1  # velocidade normal

            self.desenhar()
            self.clock.tick(60)

        pygame.quit()


#########################################
#       FUNÇÃO PRINCIPAL DO JOGO        #
#########################################
if __name__ == "__main__":
    pygame.init()
    jogo = Jogo()
    jogo.executar()
