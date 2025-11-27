import os


# TAD para representar o mapa do jogo
class Mapa:
    # Construtor da classe mapa que recebe o arquivo .txt
    def __init__(self, arquivo: str) -> None:
        # Atributos da classe
        self.lin = 0
        self.col = 0
        self.matriz = []
        self.posicaoInicialPacman = None  # Posição inicial do Pacman
        self.posicaoInicialFantasmas = []  # Lista de fantasmas
        self.posicaoPowerUp = None  # Power-up (0)
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
