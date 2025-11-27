from config import (
    TILE_SIZE,
    VELOCIDADE,
    PRETO,
    BRANCO,
    AMARELO,
    VERMELHO,
    AZUL,
    estadoJogo,
)
from mapa import Mapa
from entidades import Pacman, Fantasma
import pygame


class Jogo:
    def __init__(self) -> None:
        self.estado = estadoJogo.MENU
        # Carrega o mapa
        self.mapa = Mapa("fases/fase1.txt")

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
