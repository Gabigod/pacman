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

class EstadoNome(Estado):
    def __init__(self, jogo, score):
        super().__init__(jogo)
        self.score = score
        self.nome = ""

    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN and len(self.nome) > 0:
                self.jogo.salvar_score(self.nome, self.score)
                self.jogo.mudarEstado(EstadoGameOver(self.jogo))
            
            elif evento.key == pygame.K_BACKSPACE:
                self.nome = self.nome[:-1]

            else:
                if len(self.nome) < 10:
                    self.nome += evento.unicode

    def update(self):
        pass

    def desenhar(self):
        self.jogo.tela.fill(cfg.PRETO)

        titulo = self.jogo.fonte.render("DIGITE SEU NOME:", True, cfg.AMARELO)
        rect = titulo.get_rect(center=(self.jogo.larguraTela//2, 200))
        self.jogo.tela.blit(titulo, rect)

        nome_txt = self.jogo.fonte.render(self.nome, True, cfg.BRANCO)
        rect2 = nome_txt.get_rect(center=(self.jogo.larguraTela//2, 260))
        self.jogo.tela.blit(nome_txt, rect2)

        msg = self.jogo.fonte.render("Pressione ENTER para confirmar", True, cfg.VERMELHO)
        rect3 = msg.get_rect(center=(self.jogo.larguraTela//2, 320))
        self.jogo.tela.blit(msg, rect3)

        pygame.display.flip()


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
                self.jogo.mudarEstado(EstadoRanking(self.jogo))
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

class EstadoRanking(Estado):
    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self.jogo.mudarEstado(EstadoMenu(self.jogo))

    def update(self):
        pass

    def desenhar(self):
        self.jogo.tela.fill(cfg.PRETO)

        titulo = self.jogo.fonte.render("RANKING", True, cfg.AMARELO)
        rect = titulo.get_rect(center=(self.jogo.larguraTela//2, 60))
        self.jogo.tela.blit(titulo, rect)

        # exibir lista de scores
        y = 120
        for i, (nome, pontos) in enumerate(self.jogo.scores):
            texto = self.jogo.fonte.render(f"{i+1}. {nome} — {pontos} pontos", True, cfg.BRANCO)
            rect = texto.get_rect(center=(self.jogo.larguraTela//2, y))
            self.jogo.tela.blit(texto, rect)
            y += 40

        # instrução
        msg = self.jogo.fonte.render("Pressione ESC para voltar", True, cfg.VERMELHO)
        rect = msg.get_rect(center=(self.jogo.larguraTela//2, self.jogo.alturaTela - 60))
        self.jogo.tela.blit(msg, rect)

        pygame.display.flip()



class EstadoGameOver(Estado):
    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                self.jogo.rodando = False

            elif evento.key == pygame.K_1:
                self.reiniciar_jogo()

            elif evento.key == pygame.K_2:
                self.jogo.mudarEstado(EstadoRanking(self.jogo))



    def update(self):
        pass

    def desenhar(self):
        self.jogo.tela.fill(cfg.PRETO)

        txt = self.jogo.fonte.render("GAME OVER", True, cfg.VERMELHO)
        rect = txt.get_rect(center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2 - 40))
        self.jogo.tela.blit(txt, rect)

        txt2 = self.jogo.fonte.render("Pressione ENTER para sair", True, cfg.BRANCO)
        rect2 = txt2.get_rect(center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2))
        self.jogo.tela.blit(txt2, rect2)

        txt3 = self.jogo.fonte.render("Pressione 1 para reiniciar", True, cfg.BRANCO)
        rect3 = txt3.get_rect(center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2 + 40))
        self.jogo.tela.blit(txt3, rect3)

        txt4 = self.jogo.fonte.render("Pressione 2 para ver o Ranking", True, cfg.BRANCO)
        rect4 = txt4.get_rect(center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2 + 80))
        self.jogo.tela.blit(txt4, rect4)

        pygame.display.flip()

    def reiniciar_jogo(self):
        # Recarrega o mapa
        self.jogo.mapa = Mapa("fases/fase1.txt")

        # Reset do Pacman
        px, py = self.jogo.mapa.posicaoInicialPacman
        self.jogo.pacman = Pacman(px, py, self.jogo.folhaSprites)

        # Reset dos fantasmas
        self.jogo.fantasmas = []
        for fx, fy in self.jogo.mapa.posicaoInicialFantasmas:
            self.jogo.fantasmas.append(Fantasma(fx, fy, self.jogo.folhaSprites))

        # Reset powerups e status
        self.jogo.powerupAtivo = False
        self.jogo.powerupTimer = 0

        # VOLTA ao estado de jogo
        self.jogo.mudarEstado(EstadoJogo(self.jogo))

        

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

                # Se o PACMAN estiver invencível, ignorar colisões
                if self.jogo.pacman.invencivel:
                    continue

                if fantasma.assustado:
                    # Pacman come o fantasma
                    self.jogo.pacman.pontos += 200
                    fantasma.rect.x = fantasma.xInicio * cfg.TILE_SIZE
                    fantasma.rect.y = fantasma.yInicio * cfg.TILE_SIZE
                    fantasma.assustado = False
                    fantasma.tempoPreso = 150

                else:
                    # Perde vida
                    self.jogo.pacman.vidas -= 1

                    # Se acabou as vidas → GAME OVER
                    if self.jogo.pacman.vidas <= 0:
                        self.jogo.mudarEstado(EstadoNome(self.jogo, self.jogo.pacman.pontos))
                        return

                    # SENÃO → reset posição
                    self.jogo.pacman.rect.x = self.jogo.pacman.xInicio * cfg.TILE_SIZE
                    self.jogo.pacman.rect.y = self.jogo.pacman.yInicio * cfg.TILE_SIZE

                    self.jogo.pacman.direcao = (0, 0)
                    self.jogo.pacman.proximaDirecao = (0, 0)

                    # Ativa invencibilidade temporária
                    self.jogo.pacman.invencivel = True
                    self.jogo.pacman.invencivelTimer = 120  # 2 segundos (60 fps)


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

        # Se estiver invencível → piscar
        if self.jogo.pacman.invencivel and self.jogo.pacman.parpadeoToggle:
            # Não desenha o Pacman nesse frame (efeito de piscar)
            pass
        else:
            if self.jogo.pacman.imagem:
                self.jogo.tela.blit(self.jogo.pacman.imagem, rectDesenhoPacman)
            else:
                pygame.draw.circle(
                    self.jogo.tela,
                    cfg.AMARELO,
                    rectDesenhoPacman.center,
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
                    rectDesenhoFantasma.center,
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
        
        self.carregar_scores()

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
    
    def carregar_scores(self):
        self.scores = []
        try:
            with open("scores.txt", "r") as f:
                for linha in f:
                    nome, pontos = linha.strip().split(";")
                    self.scores.append((nome, int(pontos)))

            self.scores.sort(key=lambda x: x[1], reverse=True)

        except FileNotFoundError:
            self.scores = []


    def salvar_score(self, nome, pontos):
        self.scores.append((nome, pontos))
        self.scores.sort(key=lambda x: x[1], reverse=True)
        self.scores = self.scores[:5]  # Top 5 apenas

        with open("scores.txt", "w") as f:
            for nome, pts in self.scores:
                f.write(f"{nome};{pts}\n")



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
            self.estadoAtual.desenhar()


        pygame.quit()


#########################################
#       FUNÇÃO PRINCIPAL DO JOGO        #
#########################################
if __name__ == "__main__":
    pygame.init()
    jogo = Jogo()
    jogo.executar()
