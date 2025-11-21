from enum import Enum
import os

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AMARELO = (255, 255, 0)
AZUL = (0, 0, 255)
VERMELHO = (255, 0, 0)

# Enum do jogo
class estadoJogo(Enum):
    MENU = 0
    GAMEPLAY = 1
    GAMEOVER = 2
    VITORIA = 3
    DERROTA = 4
    RANKING = 5

############
#   TAD    #
############
class Entidade:
    # Construtor da entidade
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        print(f"Entidade criada em ({x},{y})")

class Mapa:
    # Construtor da classe mapa que recebe o arquivo
    def __init__(self, arquivo) -> None:
        # Atributos da classe
        self.lin = 0
        self.col = 0
        self.matriz = []

        self.carregarMapa(arquivo)

    def carregarMapa(self, arquivo):
        # Verifica se o arquivo existe
        if not os.path.exists(arquivo):
            print(f"ERRO: O arquivo '{arquivo}' não foi encontrado no diretório.") # Debug
            return None

        print(f"--- Lendo o arquivo: {arquivo} --- \n")

        # Abertura e leitura do arquivo
        try:
            with open(arquivo, 'r') as arq:
                # Ler a primeira linha para pegar dimensoes
                dim = arq.readline()
                if dim:
                    dims = dim.strip().split() # Remove espaços e separa os valores
                    self.lin = int(dims[0])
                    self.col = int(dims[1])
                    print(f"Dimensões: {self.lin} linhas x {self.col} colunas") # Debug
                # Ler o restante do mapa linha a linha e limpar quebras de linha
                for linha in range(self.lin):
                    linhaMapa = arq.readline().strip()

        except Exception as e:
            print(f"Erro ao ler o arquivo {e}")

if __name__ == "__main__":
    mapa = Mapa("fase1.txt")
    print(mapa.matriz)
