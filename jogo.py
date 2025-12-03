from abc import ABC, abstractmethod
import config as cfg
from mapa import Mapa
from entidades import Pacman, Fantasma
import pygame  # Para a GUI
import pickle  # Para salvar
import os  # Para funcionalidades do sistema, como listar diretórios


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


class EstadoVitoria(Estado):
    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                # Vai para a tela de registrar nome no Ranking
                self.jogo.mudarEstado(EstadoNome(self.jogo, self.jogo.pacman.pontos))

    def update(self):
        pass

    def desenhar(self):
        self.jogo.tela.fill(cfg.PRETO)

        # Título
        titulo = self.jogo.fonte.render("PARABÉNS!", True, cfg.AMARELO)
        rectT = titulo.get_rect(
            center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2 - 40)
        )
        self.jogo.tela.blit(titulo, rectT)

        # Subtítulo
        msg = self.jogo.fonte.render("Você completou o nível!", True, cfg.BRANCO)
        rectM = msg.get_rect(
            center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2)
        )
        self.jogo.tela.blit(msg, rectM)

        # Score Final
        score = self.jogo.fonte.render(
            f"Score Final: {self.jogo.pacman.pontos}", True, cfg.AZUL
        )
        rectS = score.get_rect(
            center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2 + 40)
        )
        self.jogo.tela.blit(score, rectS)

        # Instrução
        info = self.jogo.fonte.render(
            "Pressione ENTER para continuar", True, cfg.VERMELHO
        )
        rectI = info.get_rect(
            center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2 + 80)
        )
        self.jogo.tela.blit(info, rectI)

        pygame.display.flip()


class EstadoPause(Estado):
    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_p or evento.key == pygame.K_ESCAPE:
                # Volta para o jogo (despausa)
                self.jogo.mudarEstado(self.jogo.estadoAnterior)

            elif evento.key == pygame.K_s:
                # Vai para tela de salvar
                self.jogo.mudarEstado(EstadoSalvar(self.jogo))

            elif evento.key == pygame.K_q:
                # Sai para o menu principal
                self.jogo.mudarEstado(EstadoMenu(self.jogo))

    def update(self):
        pass

    def desenhar(self):
        # Sobreposição simples preta
        self.jogo.tela.fill(cfg.PRETO)

        titulo = self.jogo.fonte.render("JOGO PAUSADO", True, cfg.AMARELO)
        rect = titulo.get_rect(
            center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 3)
        )
        self.jogo.tela.blit(titulo, rect)

        opcoes = ["(P) Continuar", "(S) Salvar Jogo", "(Q) Sair para Menu"]

        y = self.jogo.alturaTela // 2
        for op in opcoes:
            txt = self.jogo.fonte.render(op, True, cfg.BRANCO)
            rectOp = txt.get_rect(center=(self.jogo.larguraTela // 2, y))
            self.jogo.tela.blit(txt, rectOp)
            y += 40

        pygame.display.flip()


class EstadoSalvar(Estado):
    def __init__(self, jogo):
        super().__init__(jogo)
        self.nomeArquivo = "save"  # Nome padrão

    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                if self.nomeArquivo:
                    self.jogo.salvarJogo(self.nomeArquivo)
                    # Volta para o pause após salvar
                    self.jogo.mudarEstado(EstadoPause(self.jogo))

            elif evento.key == pygame.K_ESCAPE:
                self.jogo.mudarEstado(EstadoPause(self.jogo))

            elif evento.key == pygame.K_BACKSPACE:
                self.nomeArquivo = self.nomeArquivo[:-1]
            else:
                if len(self.nomeArquivo) < 15:  # Limite de caracteres
                    self.nomeArquivo += evento.unicode

    def update(self):
        pass

    def desenhar(self):
        self.jogo.tela.fill(cfg.PRETO)

        titulo = self.jogo.fonte.render("NOME DO SAVE:", True, cfg.AMARELO)
        self.jogo.tela.blit(titulo, (50, 100))

        entrada = self.jogo.fonte.render(self.nomeArquivo, True, cfg.BRANCO)
        self.jogo.tela.blit(entrada, (50, 150))

        info = self.jogo.fonte.render(
            "ENTER para Salvar / ESC para Cancelar", True, cfg.AZUL
        )
        self.jogo.tela.blit(info, (50, 250))

        pygame.display.flip()


class EstadoSeletorLoad(Estado):
    def __init__(self, jogo):
        super().__init__(jogo)
        self.diretorio = "saves"
        if not os.path.exists(self.diretorio):
            os.makedirs(self.diretorio)

        try:
            self.arquivos = [
                f for f in os.listdir(self.diretorio) if f.endswith(".pkl")
            ]
            self.arquivos.sort()
        except Exception:
            self.arquivos = []

        self.indexSelecionado = 0

    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self.jogo.mudarEstado(EstadoMenu(self.jogo))
            elif evento.key == pygame.K_UP:
                self.indexSelecionado = (self.indexSelecionado - 1) % len(self.arquivos)
            elif evento.key == pygame.K_DOWN:
                self.indexSelecionado = (self.indexSelecionado + 1) % len(self.arquivos)
            elif evento.key == pygame.K_RETURN:
                if self.arquivos:
                    arquivo = self.arquivos[self.indexSelecionado]
                    if self.jogo.carregarJogo(arquivo):
                        # Se carregar com sucesso, o metodo carregarJogo já define o estado
                        pass

    def update(self):
        pass

    def desenhar(self):
        self.jogo.tela.fill(cfg.PRETO)

        titulo = self.jogo.fonte.render("CARREGAR JOGO", True, cfg.AMARELO)
        rectT = titulo.get_rect(center=(self.jogo.larguraTela // 2, 50))
        self.jogo.tela.blit(titulo, rectT)

        if not self.arquivos:
            msg = self.jogo.fonte.render("Nenhum save encontrado.", True, cfg.VERMELHO)
            self.jogo.tela.blit(msg, (50, 100))
            return

        y = 100
        for i, arq in enumerate(self.arquivos):
            cor = cfg.AMARELO if i == self.indexSelecionado else cfg.BRANCO
            txt = f"> {arq}" if i == self.indexSelecionado else arq
            render = self.jogo.fonte.render(txt, True, cor)
            rect = render.get_rect(center=(self.jogo.larguraTela // 2, y))
            self.jogo.tela.blit(render, rect)
            y += 40

        pygame.display.flip()


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
        rect = titulo.get_rect(center=(self.jogo.larguraTela // 2, 200))
        self.jogo.tela.blit(titulo, rect)

        nome_txt = self.jogo.fonte.render(self.nome, True, cfg.BRANCO)
        rect2 = nome_txt.get_rect(center=(self.jogo.larguraTela // 2, 260))
        self.jogo.tela.blit(nome_txt, rect2)

        msg = self.jogo.fonte.render(
            "Pressione ENTER para confirmar", True, cfg.VERMELHO
        )
        rect3 = msg.get_rect(center=(self.jogo.larguraTela // 2, 320))
        self.jogo.tela.blit(msg, rect3)

        pygame.display.flip()


class EstadoSeletorFase(Estado):
    def __init__(self, jogo):
        super().__init__(jogo)
        self.diretorio = "fases"
        # Lista apenas os arquifos .txt no diretório de fases
        try:
            self.arquivos = [
                f for f in os.listdir(self.diretorio) if f.endswith(".txt")
            ]
            self.arquivos.sort()  # Ordena alfabeticamente

        except FileNotFoundError:
            print(f"Erro: Diretório '{self.diretorio}' não encontrado.")
            self.arquivos = []

        self.indexSelecionado = 0

    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self.jogo.mudarEstado(EstadoMenu(self.jogo))

            elif evento.key == pygame.K_UP:
                self.indexSelecionado = (self.indexSelecionado - 1) % len(self.arquivos)

            elif evento.key == pygame.K_DOWN:
                self.indexSelecionado = (self.indexSelecionado + 1) % len(self.arquivos)

            elif evento.key == pygame.K_RETURN:
                if self.arquivos:
                    arquivoEscolhido = self.arquivos[self.indexSelecionado]
                    # Inicia o jogo com o mapa selecionado
                    self.jogo.mudarEstado(EstadoJogo(self.jogo, arquivoEscolhido))

    def update(self):
        pass

    def desenhar(self):
        self.jogo.tela.fill(cfg.PRETO)

        titulo = self.jogo.fonte.render("SELECIONE A FASE", True, cfg.AMARELO)
        rectTitulo = titulo.get_rect(center=(self.jogo.larguraTela // 2, 50))
        self.jogo.tela.blit(titulo, rectTitulo)

        if not self.arquivos:
            msg = self.jogo.fonte.render("Nenhuma fase encontrada!", True, cfg.VERMELHO)
            self.jogo.tela.blit(msg, (50, 100))
            return

        # Renderiza a lista de fases
        yInicial = 120
        espacamento = 40

        for i, arquivo in enumerate(self.arquivos):
            cor = cfg.AMARELO if i == self.indexSelecionado else cfg.BRANCO
            texto = f"> {arquivo}" if i == self.indexSelecionado else arquivo

            render = self.jogo.fonte.render(texto, True, cor)
            rect = render.get_rect(
                center=(self.jogo.larguraTela // 2, yInicial + i * espacamento)
            )
            self.jogo.tela.blit(render, rect)

        pygame.display.flip()


# Estado do Menu
class EstadoMenu(Estado):
    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_1:
                # Troca para o estado de jogo
                self.jogo.mudarEstado(EstadoSeletorFase(self.jogo))
            elif evento.key == pygame.K_2:
                self.jogo.mudarEstado(EstadoSeletorLoad(self.jogo))
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
        rect = titulo.get_rect(center=(self.jogo.larguraTela // 2, 60))
        self.jogo.tela.blit(titulo, rect)

        # Cabeçalho
        header = self.jogo.fonte.render("Nome      |  Pts  |  Mapa", True, cfg.AZUL)
        rectH = header.get_rect(center=(self.jogo.larguraTela // 2, 100))
        self.jogo.tela.blit(header, rectH)

        y = 140
        for i, (nome, pontos, mapaNome) in enumerate(self.jogo.scores):
            # Formatação simples para alinhar
            textoStr = f"{i + 1}. {nome} - {pontos} - {mapaNome}"
            texto = self.jogo.fonte.render(textoStr, True, cfg.BRANCO)
            rect = texto.get_rect(center=(self.jogo.larguraTela // 2, y))
            self.jogo.tela.blit(texto, rect)
            y += 30

        msg = self.jogo.fonte.render("Pressione ESC para voltar", True, cfg.VERMELHO)
        rect = msg.get_rect(
            center=(self.jogo.larguraTela // 2, self.jogo.alturaTela - 40)
        )
        self.jogo.tela.blit(msg, rect)

        pygame.display.flip()


class EstadoGameOver(Estado):
    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                self.jogo.rodando = False

            elif evento.key == pygame.K_1:
                self.jogo.mudarEstado(EstadoJogo(self.jogo, self.jogo.nomeMapaAtual))

            elif evento.key == pygame.K_2:
                self.jogo.mudarEstado(EstadoRanking(self.jogo))

    def update(self):
        pass

    def desenhar(self):
        self.jogo.tela.fill(cfg.PRETO)

        txt = self.jogo.fonte.render("GAME OVER", True, cfg.VERMELHO)
        rect = txt.get_rect(
            center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2 - 40)
        )
        self.jogo.tela.blit(txt, rect)

        txt2 = self.jogo.fonte.render("Pressione ENTER para sair", True, cfg.BRANCO)
        rect2 = txt2.get_rect(
            center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2)
        )
        self.jogo.tela.blit(txt2, rect2)

        txt3 = self.jogo.fonte.render("Pressione 1 para reiniciar", True, cfg.BRANCO)
        rect3 = txt3.get_rect(
            center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2 + 40)
        )
        self.jogo.tela.blit(txt3, rect3)

        txt4 = self.jogo.fonte.render(
            "Pressione 2 para ver o Ranking", True, cfg.BRANCO
        )
        rect4 = txt4.get_rect(
            center=(self.jogo.larguraTela // 2, self.jogo.alturaTela // 2 + 80)
        )
        self.jogo.tela.blit(txt4, rect4)

        pygame.display.flip()

    def reiniciar_jogo(self):
        # Recarrega o mapa
        self.jogo.mudarEstado(EstadoJogo(self.jogo, self.jogo.nomeMapaAtual))

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
        self.jogo.mudarEstado(EstadoJogo(self.jogo, self.jogo.nomeMapaAtual))


# Estado de Gameplay
class EstadoJogo(Estado):
    def __init__(self, jogo, arquivoMapa):
        super().__init__(jogo)
        # Carrega o nível utilizando o metodo da classe jogo
        self.jogo.carregarNivel(arquivoMapa)

    def processar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_p:
                # Salva a referência deste estado para voltar depois
                self.jogo.estadoAnterior = self
                self.jogo.mudarEstado(EstadoPause(self.jogo))
            else:
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
                        self.jogo.mudarEstado(
                            EstadoNome(self.jogo, self.jogo.pacman.pontos)
                        )
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
                # Verifica limites para evitar sair do mapa
                if 0 <= py < self.jogo.mapa.lin and 0 <= px < self.jogo.mapa.col:
                    item = self.jogo.mapa.matriz[py][px]

                    if item == ".":
                        self.jogo.mapa.matriz[py][px] = " "
                        self.jogo.pacman.pontos += 10
                        self.jogo.mapa.pontosRestantes -= 1  # Decrementa

                    elif item == "0":  # POWERUP
                        self.jogo.mapa.matriz[py][px] = " "
                        self.jogo.pacman.pontos += 50
                        self.jogo.mapa.pontosRestantes -= 1  # Decrementa

                        # Ativa powerup (no objeto jogo)
                        self.jogo.powerupAtivo = True
                        self.jogo.powerupTimer = 15 * 60

                        # Deixa todos os fantasmas assustados
                        for f in self.jogo.fantasmas:
                            f.assustado = True
                            f.speed = 1  # mais lentos

                    # --- Verifica a vitoria ---
                    if self.jogo.mapa.pontosRestantes <= 0:
                        # Adiciona um bônus por completar a fase
                        self.jogo.pacman.pontos += 1000
                        self.jogo.mudarEstado(EstadoVitoria(self.jogo))
                        return  # Para o update atual

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
        # Carrega o primeiro mapa para modelar a janela (gambiarra, o correto seria ter um padrão)
        self.mapa = Mapa("fases/fase1.txt")
        self.nomeMapaAtual = "fase1.txt"

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

        # Define o estado inicial
        self.estadoAtual = EstadoMenu(self)

        # Inicializa pacman e fantasmas vazios (serão criados no carregarNivel)
        self.pacman = None
        self.fantasmas = []

        # Define o estado inicial diretamente usando a Classe, não o Enum
        self.estadoAtual = EstadoMenu(self)

    # Método para salvar o estado atual do jogo
    def salvarJogo(self, nomeArquivo):
        caminhoDir = "saves"
        if not os.path.exists(caminhoDir):
            os.makedirs(caminhoDir)

        # Garante extensão .pkl
        if not nomeArquivo.endswith(".pkl"):
            nomeArquivo += ".pkl"

        caminhoCompleto = os.path.join(caminhoDir, nomeArquivo)

        # Preparar objetos (remover imagens que não podem ser salvas)
        self.pacman.limparImagens()
        for f in self.fantasmas:
            f.limparImagens()

        # Coletar dados do estado atual
        dados = {
            "mapa": self.mapa,
            "pacman": self.pacman,
            "fantasmas": self.fantasmas,
            "score": self.pacman.pontos,
            "vidas": self.pacman.vidas,
            "nomeMapaAtual": self.nomeMapaAtual,
            "powerupAtivo": self.powerupAtivo,
            "powerupTimer": self.powerupTimer,
        }

        try:
            with open(caminhoCompleto, "wb") as f:
                pickle.dump(dados, f)
            print(f"Jogo salvo em {caminhoCompleto}")
        except Exception as e:
            print(f"Erro ao salvar: {e}")

        # Restaura imagens imediatamente para o jogo não quebrar se continuar
        self.pacman.restaurarImagens(self.folhaSprites)
        for f in self.fantasmas:
            f.restaurarImagens(self.folhaSprites)

    # Método para carregar
    def carregarJogo(self, nomeArquivo):
        caminho = os.path.join("saves", nomeArquivo)
        if not os.path.exists(caminho):
            print("Arquivo não encontrado.")
            return False

        try:
            with open(caminho, "rb") as f:
                dados = pickle.load(f)

            # Restaura variáveis globais
            self.mapa = dados["mapa"]
            self.nomeMapaAtual = dados["nomeMapaAtual"]
            self.powerupAtivo = dados.get("powerupAtivo", False)
            self.powerupTimer = dados.get("powerupTimer", 0)

            # Restaura entidades
            self.pacman = dados["pacman"]
            self.fantasmas = dados["fantasmas"]

            # IMPORTANTE: Recarregar as sprites (imagens)
            self.pacman.restaurarImagens(self.folhaSprites)
            for f in self.fantasmas:
                f.restaurarImagens(self.folhaSprites)

            # Atualiza dimensões da tela caso o save seja de um mapa diferente
            self.larguraTela = self.mapa.col * cfg.TILE_SIZE
            self.alturaTela = (self.mapa.lin + 1) * cfg.TILE_SIZE
            self.tela = pygame.display.set_mode((self.larguraTela, self.alturaTela))

            # Cria o Estado de Jogo JÁ restaurado
            # Precisamos instanciar o EstadoJogo, mas SEM chamar carregarNivel,
            # pois já carregamos os objetos manualmente.

            estadoJ = EstadoJogo(self, self.nomeMapaAtual)
            # O construtor do EstadoJogo chama carregarNivel, o que RESETARIA o jogo.
            # Precisamos evitar isso ou ajustar o EstadoJogo.
            # temos que modificar levemente a criação do estado ou apenas setar o estado
            # e forçar os objetos que acabamos de carregar.

            # Como o EstadoJogo chama self.jogo.carregarNivel no __init__,
            # ele vai sobrescrever o que acabamos de carregar.
            # Vamos corrigir recarregando os objetos DO SAVE logo após instanciar o estado.

            self.pacman = dados[
                "pacman"
            ]  # Reatribui para garantir (o carregarNivel resetou)
            self.pacman.restaurarImagens(self.folhaSprites)
            self.fantasmas = dados["fantasmas"]
            for f in self.fantasmas:
                f.restaurarImagens(self.folhaSprites)
            self.mapa = dados["mapa"]  # O mapa do save pode ter pontinhos comidos

            # Define o estado "Paused"
            self.estadoAnterior = estadoJ
            self.mudarEstado(EstadoPause(self))

            return True

        except Exception as e:
            print(f"Erro ao carregar save: {e}")
            return False

    # Lógica para carregar o mapa
    def carregarNivel(self, nomeArquivo):
        caminho = f"fases/{nomeArquivo}"
        self.nomeMapaAtual = nomeArquivo  # Salva para o ranking
        self.mapa = Mapa(caminho)

        # Redimensiona tela se necessário (caso os mapas tenham tamanhos diferentes)
        novaLargura = self.mapa.col * cfg.TILE_SIZE
        novaAltura = (self.mapa.lin + 1) * cfg.TILE_SIZE
        if novaLargura != self.larguraTela or novaAltura != self.alturaTela:
            self.larguraTela = novaLargura
            self.alturaTela = novaAltura
            self.tela = pygame.display.set_mode((self.larguraTela, self.alturaTela))

        # Reset do Pacman
        if self.mapa.posicaoInicialPacman:
            px, py = self.mapa.posicaoInicialPacman
            self.pacman = Pacman(px, py, self.folhaSprites)
        else:
            self.pacman = Pacman(1, 1, self.folhaSprites)

        # Reset dos fantasmas
        self.fantasmas = []
        for fx, fy in self.mapa.posicaoInicialFantasmas:
            self.fantasmas.append(Fantasma(fx, fy, self.folhaSprites))

        self.powerupAtivo = False
        self.powerupTimer = 0

    def mudarEstado(self, novo_estado: Estado) -> None:
        self.estadoAtual = novo_estado

    def carregar_scores(self):
        self.scores = []
        try:
            with open("scores.txt", "r") as f:
                for linha in f:
                    partes = linha.strip().split(";")
                    if len(partes) == 3:
                        nome, pontos, mapaNome = partes
                        self.scores.append((nome, int(pontos), mapaNome))
                    elif len(partes) == 2:  # Retrocompatibilidade
                        nome, pontos = partes
                        self.scores.append((nome, int(pontos), "Desconhecido"))

            self.scores.sort(key=lambda x: x[1], reverse=True)
        except FileNotFoundError:
            self.scores = []

    def salvar_score(self, nome, pontos):
        self.scores.append((nome, pontos, self.nomeMapaAtual))
        self.scores.sort(key=lambda x: x[1], reverse=True)
        self.scores = self.scores[:10]  # Top 10

        with open("scores.txt", "w") as f:
            for nome, pts, mapaNome in self.scores:
                f.write(f"{nome};{pts};{mapaNome}\n")

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
