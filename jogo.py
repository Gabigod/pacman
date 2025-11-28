import config as cfg
from mapa import Mapa
from entidades import Pacman, Fantasma
import pygame


class Jogo:
    # Inicializa o jogo
    def __init__(self) -> None:
        self.estado = cfg.estadoJogo.MENU
        # Carrega o mapa
        self.mapa = Mapa("fases/fase1.txt")

        # Configuração da tela
        self.larguraTela = self.mapa.col * cfg.TILE_SIZE
        self.alturaTela = self.mapa.lin * cfg.TILE_SIZE
        self.tela = pygame.display.set_mode((self.larguraTela, self.alturaTela))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()

        # Cria uma fonte do sistema. None usa a padrão, tamanho 28.
        self.fonte = pygame.font.Font(None, 28)

        # Tenta carregar os sprites
        try:
            self.folhaSprites = pygame.image.load("Sprites.png").convert_alpha()
            print("Sprites carregados com sucesso.")
        except pygame.error as e:
            print(f"Erro ao carregar sprites: {e}")
            self.folhaSprites = None

        # Instancia o objeto pacman com as coordenadas lidas durante o carregamento do mapa
        px, py = self.mapa.posicaoInicialPacman
        self.pacman = Pacman(px, py, self.folhaSprites)

        # Instancia os fantasmas nas posições iniciais lidas durante o carregamento do mapa
        self.fantasmas = []
        self.powerupAtivo = False
        self.powerupTimer = 0

        for fx, fy in self.mapa.posicaoInicialFantasmas:
            fantasma = Fantasma(fx, fy, self.folhaSprites)
            self.fantasmas.append(fantasma)

    # Método para desenhar o estado atual do jogo
    def desenhar(self) -> None:
        self.tela.fill(cfg.PRETO)

        # Desenha o mapa
        for i in range(self.mapa.lin):
            for j in range(self.mapa.col):
                char = self.mapa.matriz[i][j]

                x = j * cfg.TILE_SIZE
                y = i * cfg.TILE_SIZE

                if char == "#":
                    pygame.draw.rect(
                        self.tela, cfg.AZUL, (x, y, cfg.TILE_SIZE, cfg.TILE_SIZE)
                    )
                elif char == ".":
                    pygame.draw.circle(
                        self.tela,
                        cfg.BRANCO,
                        (x + cfg.TILE_SIZE // 2, y + cfg.TILE_SIZE // 2),
                        4,
                    )
                elif char == "0":
                    pygame.draw.circle(
                        self.tela,
                        cfg.BRANCO,
                        (x + cfg.TILE_SIZE // 2, y + cfg.TILE_SIZE // 2),
                        8,
                    )

        # Desenha o Pacman
        if self.pacman.imagem:  # Se carregou a imagem do Pacman
            self.tela.blit(self.pacman.imagem, self.pacman.rect)  # Desenha com a imagem
        else:
            pygame.draw.circle(
                self.tela,
                cfg.AMARELO,
                self.pacman.rect.center,
                cfg.TILE_SIZE // 2,  # Se não, desenha um círculo amarelo
            )

        # Desenha todos os fantasmas
        for fantasma in self.fantasmas:
            if fantasma.imagem:
                self.tela.blit(fantasma.imagem, fantasma.rect)
            else:
                corFantasma = cfg.AZUL if fantasma.assustado else cfg.VERMELHO
                pygame.draw.circle(
                    self.tela,
                    corFantasma,
                    fantasma.rect.center,
                    cfg.TILE_SIZE // 2,
                )

        pygame.display.flip()

    # Texto do Score (Canto Superior Esquerdo)
        texto_score = self.fonte.render(f"SCORE: {self.pacman.pontos}", True, cfg.BRANCO)
        self.tela.blit(texto_score, (10, 5))

        # Texto das Vidas (Canto Superior Direito)
        texto_vidas = self.fonte.render(f"VIDAS: {self.pacman.vidas}", True, cfg.BRANCO)
        rect_vidas = texto_vidas.get_rect()
        # Posiciona a direita, com margem de 10 pixels
        rect_vidas.topright = (self.larguraTela - 10, 5)
        self.tela.blit(texto_vidas, rect_vidas)

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
                        fantasma.rect.x = fantasma.xInicio * cfg.TILE_SIZE
                        fantasma.rect.y = fantasma.yInicio * cfg.TILE_SIZE
                        fantasma.assustado = False
                        fantasma.tempoPreso = 150  # Fica preso por 150 frames
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
                        f.speed = cfg.VELOCIDADE - 1  # velocidade normal

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
