from abc import ABC, abstractmethod
import config as cfg
from mapa import Mapa
from entidades import Pacman, Fantasma
import pygame


# Classe Abstrata (Modelo)
class Estado(ABC):
    def __init__(self, jogo):
        self.jogo = jogo

    @abstractmethod
    def processar_eventos(self, evento):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def desenhar(self):
        pass


# Estado do Menu
class EstadoMenu(Estado):
    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_1:
                # Troca para o estado de jogo
                self.jogo.mudarEstado(EstadoJogo(self.jogo))
            elif evento.key == pygame.K_2:
                print("Carregar Jogo - Não implementado")
            elif evento.key == pygame.K_3:
                print("Ver Ranking - Não implementado")
            elif evento.key == pygame.K_4:
                self.jogo.rodando = False

    def update(self):
        pass  # Menu estático

    def desenhar(self):
        self.jogo.tela.fill(cfg.PRETO)

        # Título
        titulo = self.jogo.fonte.render("PACMAN", True, cfg.AMARELO)
        rect_titulo = titulo.get_rect(
            center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 4)
        )
        self.jogo.tela.blit(titulo, rect_titulo)

        # Opções
        opcoes = ["1. Novo Jogo", "2. Carregar", "3. Ranking", "4. Sair"]
        for i, texto in enumerate(opcoes):
            txt = self.jogo.fonte.render(texto, True, cfg.BRANCO)
            rect = txt.get_rect(
                center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2 + i * 40)
            )
            self.jogo.tela.blit(txt, rect)

        pygame.display.flip()


# Estado de Gameplay
class EstadoJogo(Estado):
    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            self.jogo.pacman.processarEvento(evento.key)

    def update(self):
        # Acessa pacman e mapa através de self.jogo
        self.jogo.pacman.update(self.jogo.mapa)

        for fantasma in self.jogo.fantasmas:
            fantasma.update(self.jogo.mapa, self.jogo.pacman)

            # Colisão (usando colisão de retângulos do Pygame)
            hitbox_pacman = self.jogo.pacman.rect.inflate(-10, -10)
            hitbox_fantasma = fantasma.rect.inflate(-10, -10)

            if hitbox_pacman.colliderect(hitbox_fantasma):
                if fantasma.assustado:
                    # Pacman come o fantasma
                    self.jogo.pacman.pontos += 200
                    fantasma.rect.x = fantasma.xInicio * cfg.TILE_SIZE
                    fantasma.rect.y = fantasma.yInicio * cfg.TILE_SIZE
                    fantasma.assustado = False
                    fantasma.tempoPreso = 150  # Fica preso por 150 frames
                else:
                    if self.jogo.pacman.vidas > 0:
                        self.jogo.pacman.vidas -= 1
                        # Reseta posição usando coordenadas de grid * TILE_SIZE
                        self.jogo.pacman.rect.x = (
                            self.jogo.pacman.xInicio * cfg.TILE_SIZE
                        )
                        self.jogo.pacman.rect.y = (
                            self.jogo.pacman.yInicio * cfg.TILE_SIZE
                        )

            # Lógica de comer pontos (baseada na grade)
            if self.jogo.pacman.esta_centralizado():
                px, py = self.jogo.pacman.getPosGrad()
                # Verifica limites para evitar crash se sair do mapa
                if 0 <= py < self.jogo.mapa.lin and 0 <= px < self.jogo.mapa.col:
                    item = self.jogo.mapa.matriz[py][px]

                    if item == ".":
                        self.jogo.mapa.matriz[py][px] = " "
                        self.jogo.pacman.pontos += 10

                    elif item == "0":  # POWERUP
                        self.jogo.mapa.matriz[py][px] = " "
                        self.jogo.pacman.pontos += 50

                        # Ativa powerup (no objeto jogo)
                        self.jogo.powerupAtivo = True
                        self.jogo.powerupTimer = 15 * 60

                        # Deixa todos os fantasmas assustados
                        for f in self.jogo.fantasmas:
                            f.assustado = True
                            f.speed = 1  # mais lentos

            # Timer do powerup
            if self.jogo.powerupAtivo:
                self.jogo.powerupTimer -= 1
                if self.jogo.powerupTimer <= 0:
                    self.jogo.powerupAtivo = False
                    for f in self.jogo.fantasmas:
                        f.assustado = False
                        f.speed = cfg.VELOCIDADE - 1  # velocidade normal

            self.desenhar()

    def desenhar(self) -> None:
        # Limpa a Tela usando self.jogo.tela
        self.jogo.tela.fill(cfg.PRETO)

        # Variável auxiliar para a altura da barra de score/vidas
        offsetY = cfg.TILE_SIZE

        # Desenha o mapa
        for i in range(self.jogo.mapa.lin):
            for j in range(self.jogo.mapa.col):
                char = self.jogo.mapa.matriz[i][j]

                x = j * cfg.TILE_SIZE
                y = i * cfg.TILE_SIZE + offsetY

                if char == "#":
                    pygame.draw.rect(
                        self.jogo.tela, cfg.AZUL, (x, y, cfg.TILE_SIZE, cfg.TILE_SIZE)
                    )
                elif char == ".":
                    pygame.draw.circle(
                        self.jogo.tela,
                        cfg.BRANCO,
                        (x + cfg.TILE_SIZE // 2, y + cfg.TILE_SIZE // 2),
                        4,
                    )
                elif char == "0":
                    pygame.draw.circle(
                        self.jogo.tela,
                        cfg.BRANCO,
                        (x + cfg.TILE_SIZE // 2, y + cfg.TILE_SIZE // 2),
                        8,
                    )

        # Desenha o Pacman
        rectDesenhoPacman = self.jogo.pacman.rect.move(0, offsetY)

        if self.jogo.pacman.imagem:
            self.jogo.tela.blit(self.jogo.pacman.imagem, rectDesenhoPacman)
        else:
            pygame.draw.circle(
                self.jogo.tela,
                cfg.AMARELO,
                self.jogo.pacman.rect.center,
                cfg.TILE_SIZE // 2,
            )

        # Desenha todos os fantasmas
        for fantasma in self.jogo.fantasmas:
            rectDesenhoFantasma = fantasma.rect.move(0, offsetY)

            if fantasma.imagem:
                self.jogo.tela.blit(fantasma.imagem, rectDesenhoFantasma)
            else:
                corFantasma = cfg.AZUL if fantasma.assustado else cfg.VERMELHO
                pygame.draw.circle(
                    self.jogo.tela,
                    corFantasma,
                    fantasma.rect.center,
                    cfg.TILE_SIZE // 2,
                )

        # Texto do Score
        textoScore = self.jogo.fonte.render(
            f"SCORE: {self.jogo.pacman.pontos}", True, cfg.BRANCO
        )
        yText = (cfg.TILE_SIZE - textoScore.get_height()) // 2
        self.jogo.tela.blit(textoScore, (10, yText))

        # Texto das Vidas
        textoVidas = self.jogo.fonte.render(
            f"VIDAS: {self.jogo.pacman.vidas}", True, cfg.BRANCO
        )
        rectVidas = textoVidas.get_rect()
        rectVidas.topright = (self.jogo.larguraTela - 10, yText)
        self.jogo.tela.blit(textoVidas, rectVidas)

        pygame.display.flip()


class Jogo:
    # Inicializa o jogo
    def __init__(self) -> None:
        self.estado = cfg.estadoJogo.MENU
        # Carrega o mapa
        self.mapa = Mapa("fases/fase1.txt")

        # Configuração da tela
        self.larguraTela = self.mapa.col * cfg.TILE_SIZE
        self.alturaTela = (
            self.mapa.lin + 1
        ) * cfg.TILE_SIZE  # O +1 é para a barra de score/vidas
        self.tela = pygame.display.set_mode((self.larguraTela, self.alturaTela))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()

        # Inicializa variáveis de jogo
        self.powerupAtivo = False
        self.powerupTimer = 0
        self.rodando = True  # Controle do loop principal

        # fonte para a HUD.
        self.fonte = pygame.font.Font(None, 28)

        # Tenta carregar os sprites
        try:
            self.folhaSprites = pygame.image.load("Sprites.png").convert_alpha()
            print("Sprites carregados com sucesso.")
        except pygame.error as e:
            print(f"Erro ao carregar sprites: {e}")
            self.folhaSprites = None

        # Instancia o objeto pacman
        if self.mapa.posicaoInicialPacman:
            px, py = self.mapa.posicaoInicialPacman
            self.pacman = Pacman(px, py, self.folhaSprites)
        else:
            print("ERRO: Posição inicial do Pacman não encontrada no mapa!")
            # Posição padrão segura ou sair
            self.pacman = Pacman(1, 1, self.folhaSprites)

        # Instancia os fantasmas
        self.fantasmas = []
        for fx, fy in self.mapa.posicaoInicialFantasmas:
            fantasma = Fantasma(fx, fy, self.folhaSprites)
            self.fantasmas.append(fantasma)

        # Define o estado inicial
        self.estadoAtual = EstadoMenu(self)

    def mudarEstado(self, novo_estado: Estado) -> None:
        self.estadoAtual = novo_estado

    def desenhar(self) -> None:
        self.estadoAtual.desenhar()

    def executar(self) -> None:
        while self.rodando:
            self.clock.tick(60)

            # Processa os eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                else:
                    self.estadoAtual.processar_eventos(evento)

            # Update do estado atual
            self.estadoAtual.update()

            # Nota: O desenho já é chamado dentro de update() do EstadoJogo,
            # mas para o Menu pode ser necessário chamar aqui se o update for vazio.
            # Para garantir consistência, o ideal é chamar desenhar() aqui se o estado não o fizer.
            # No código original, EstadoJogo chama desenhar() no final do update,
            # mas EstadoMenu não chama.
            if isinstance(self.estadoAtual, EstadoMenu):
                self.estadoAtual.desenhar()

        pygame.quit()


#########################################
#       FUNÇÃO PRINCIPAL DO JOGO        #
#########################################
if __name__ == "__main__":
    pygame.init()
    jogo = Jogo()
    jogo.executar()
