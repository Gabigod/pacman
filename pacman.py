import pygame
from enum import Enum
import os

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AMARELO = (255, 255, 0)
AZUL = (0, 0, 255)
VERMELHO = (255, 0, 0)

TILE_SIZE = 32  # Tamanho do tile em pixels


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

    # Metodo para atualizar o conteúdo da matriz do mapa
    def atualizarConteudo(self, x: int, y: int, novoChar: str) -> None:
        self.matriz[y][x] = novoChar


# TAD para representar as entidades do jogo
class Entidade:
    # Construtor da entidade
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        # Posição fixa para resetar caso morra
        self.xInicio = x
        self.yInicio = y

    # Metodo para verificar se a entidade pode se mover para a posição (x, y)
    def podeMover(self, mapa: Mapa, x: int, y: int) -> bool:
        if x < 0 or x >= mapa.col or y < 0 or y >= mapa.lin:
            return False  # Fora dos limites do mapa
        if mapa.matriz[y][x] == "#":
            return False  # Paredes bloqueiam o movimento
        return True


# Subclasse específica para o Pacman
class Pacman(Entidade):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.tempoInvencivel = 0  # 0 indica que está vulnerável
        self.vidas = 3
        self.pontos = 0

    # Método que gerencia o movimento do Pacman
    def move(self, mapa: Mapa, direcao: str) -> None:
        if direcao == pygame.K_UP and super().podeMover(mapa, self.x, self.y - 1):
            self.y -= 1
        if direcao == pygame.K_DOWN and super().podeMover(mapa, self.x, self.y + 1):
            self.y += 1
        if direcao == pygame.K_LEFT and super().podeMover(mapa, self.x - 1, self.y):
            self.x -= 1
        if direcao == pygame.K_RIGHT and super().podeMover(mapa, self.x + 1, self.y):
            self.x += 1


# Subclasse específica para os Fantasmas
class Fantasma(Entidade):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.tempoLivre = 0  # 0 indica que está preso na casa dos fantasmas
        self.tempoAssustado = 0  # 0 indica que está normal


class Jogo:
    def __init__(self) -> None:
        self.estado = estadoJogo.MENU
        # Carrega o mapa
        self.mapa = Mapa("fase1.txt")

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
                    pygame.draw.rect(
                        self.tela, AZUL, (x, y, TILE_SIZE, TILE_SIZE)
                    )  # Parede                # Desenha a parede
                elif char == ".":
                    pygame.draw.circle(
                        self.tela, BRANCO, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 4
                    )  # Desenha o ponto
                elif char == "0":
                    pygame.draw.circle(
                        self.tela, BRANCO, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 8
                    )  # Desenha o power-up

        # Desenha o Pacman
        pacman_x = self.pacman.x * TILE_SIZE
        pacman_y = self.pacman.y * TILE_SIZE
        pygame.draw.circle(
            self.tela,
            AMARELO,
            (pacman_x + TILE_SIZE // 2, pacman_y + TILE_SIZE // 2),
            TILE_SIZE // 2,
        )

        # Desenha os Fantasmas
        for fantasma in self.fantasmas:
            fantasma_x = fantasma.x * TILE_SIZE
            fantasma_y = fantasma.y * TILE_SIZE
            pygame.draw.circle(
                self.tela,
                VERMELHO,
                (fantasma_x + TILE_SIZE // 2, fantasma_y + TILE_SIZE // 2),
                TILE_SIZE // 2,
            )

        pygame.display.flip()

    # Método principal para executar o jogo
    def executar(self) -> None:
        rodando = True
        while rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.KEYDOWN:
                    self.pacman.move(self.mapa, evento.key)
                if evento.type == pygame.QUIT:
                    rodando = False
                    pygame.quit()

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
