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
        self.posicaoInicialPacman = []  # Para guardar a posição inicial do Pacman
        self.posicaoInicialFantasmas = []  # Para guardar as posições iniciais dos Fantasmas
        self.carregarMapa(arquivo)

    # Método para carregar o mapa a partir de um arquivo .txt
    def carregarMapa(self, arquivo: str) -> None:
        # Verifica se o arquivo existe
        if not os.path.exists(arquivo):
            print(
                f"ERRO: O arquivo '{arquivo}' não foi encontrado no diretório."
            )  # Debug
            return None

        # Abertura e leitura do arquivo
        try:
            with open(arquivo, "r") as arq:
                # Ler a primeira linha para pegar dimensoes
                dim = arq.readline()
                if dim:  # Se a linha existir
                    dims = dim.strip().split()  # Remove espaços e separa os valores
                    self.lin = int(dims[0])  # Guarda o primeiro valor como linha
                    self.col = int(dims[1])  # Guarda o primeiro valor como linha
                    print(f"Dimensões: {self.lin} linhas x {self.col} colunas")  # Debug

                # Ler o restante do mapa linha a linha e limpar quebras de linha
                for i, linha in enumerate(arq):
                    # O rstrsip remove apenas o \n a direita, isso evita apagar espaços
                    # propositais colocados nas bordas
                    linhaLimpa = linha.rstrip("\n")
                    if not linhaLimpa:
                        continue

                    # converter para lista para alterar índices
                    listaChars = list(linhaLimpa)

                    # Varredura de entidades
                    for j, char in enumerate(listaChars):
                        if char == "<":
                            # Guarda posição inicial do Pacman
                            self.posicaoInicialPacman = (
                                j,
                                i,
                            )  # Guarda a posição inicial do Pacman
                            # Substitui na matriz por ponto, considerando que Pacman começa sobre um ponto
                            listaChars[j] = "."
                        elif char == "F":
                            # Guarda posição inicial do Fantasma
                            self.posicaoInicialFantasmas.append((j, i))
                            # Substitui na matriz por espaço vazio
                            listaChars[j] = " "

                    # Adiciona a linha sem os chars das entidades na matriz
                    self.matriz.append(listaChars)

        except Exception as e:
            print(f"Erro ao ler o arquivo {e}")

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
        self.x_grid, self.y_grid = self.getPosGrad()


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
            prox = self.bfsProx(mapa, pacman.xGrid, pacman.yGrid)

            if prox:
                px, py = prox
                dx = px - self.xGrid
                dy = py - self.yGrid
                self.dreicao = (dx, dy)
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

        # Desenha os Fantasmas
        for fantasma in self.fantasmas:
            pygame.draw.circle(
                self.tela,
                VERMELHO,
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
                    print("Game Over!")
                    # Reiniciar posições ou encerrar
                    rodando = False

            # Lógica de comer pontos (baseada na grade)
            if self.pacman.esta_centralizado():
                px, py = self.pacman.getPosGrad()
                item = self.mapa.matriz[py][px]
                if item == "." or item == "0":
                    self.mapa.matriz[py][px] = " "  # Remove o ponto
                    self.pacman.pontos += 10

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
