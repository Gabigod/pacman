PYTHON = python3
PIP = pip
MAIN_FILE = jogo.py
VENV_NAME = .venv
VENV_ACTIVATE = $(VENV_NAME)/bin/activate

all: run

# --- Comandos Principais --- 
install: $(VENV_NAME)/bin/activate

$(VENV_NAME)/bin/activate: prerequisites.txt
		test -d $(VENV_NAME) || $(PYTHON) -m venv $(VENV_NAME)
		$(VENV_NAME)/bin/$(PIP) install -U pip
		$(VENV_NAME)/bin/$(PIP) install -r prerequisites.txt
		touch $(VENV_NAME)/bin/activate

run: install
		@echo "Iniciando o Pacman..."
		$(VENV_NAME)/bin/python $(MAIN_FILE)

# --- Limpeza e Manutenção ---
clean:
		@echo "Limpando arquivos de bytecode..."
		find . -type f -name '*.pyc' -delete
		find . -type d -name '__pycache__' -delete

fclean: clean
		@echo "Removendo ambiente virtual..."
		rm -rf $(VENV_NAME)

# Reinstala tudo do zero
re: fclean install

.PHONY: all install run clean fclean re
