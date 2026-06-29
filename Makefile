PYTHON_VERSION ?= 3.14.5          # Alinhado com a versão do Docker
LIBRARY_DIRS = bookstore order product
BUILD_DIR ?= build
PYPI_PROXY ?= https://pypi.org/simple   # Definido para evitar erro

PYTEST_HTML_OPTIONS = --html=$(BUILD_DIR)/report.html --self-contained-html
PYTEST_TAP_OPTIONS = --tap-combined --tap-outdir $(BUILD_DIR)
PYTEST_COVERAGE_OPTIONS = --cov=$(LIBRARY_DIRS)
PYTEST_OPTIONS ?= $(PYTEST_HTML_OPTIONS) $(PYTEST_TAP_OPTIONS) $(PYTEST_COVERAGE_OPTIONS)

MYPY_OPTS ?= --python-version $(basename $(PYTHON_VERSION)) --show-column-numbers --pretty
PYTHON_VERSION_FILE=.python-version
ifeq ($(shell which pyenv),)
PYENV_VERSION_DIR ?= $(HOME)/.pyenv/versions/$(PYTHON_VERSION)
else
PYENV_VERSION_DIR ?= $(shell pyenv root)/versions/$(PYTHON_VERSION)
endif
PIP ?= pip3

POETRY_OPTS ?=
POETRY ?= poetry $(POETRY_OPTS)
RUN_PYPKG_BIN = $(POETRY) run

COLOR_ORANGE = \033[33m
COLOR_RESET = \033[0m

# ------------------------------------------------------------
# HELP
# ------------------------------------------------------------
.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# ------------------------------------------------------------
# PYTHON VERSION
# ------------------------------------------------------------
.PHONY: version-python
version-python: ## Exibe a versão do Python configurada
	@echo $(PYTHON_VERSION)

# ------------------------------------------------------------
# DEPENDÊNCIAS (LOCAL)
# ------------------------------------------------------------
$(PYENV_VERSION_DIR):
	pyenv install --skip-existing $(PYTHON_VERSION)

$(PYTHON_VERSION_FILE): $(PYENV_VERSION_DIR)
	pyenv local $(PYTHON_VERSION)

.PHONY: deps
deps: deps-brew deps-py ## Instala todas as dependências (Brew + Python)

.PHONY: deps-brew
deps-brew: Brewfile ## Instala dependências do sistema via Homebrew (macOS)
	brew bundle --file=Brewfile
	@echo "$(COLOR_ORANGE)Ensure that pyenv is setup in your shell.$(COLOR_RESET)"
	@echo "$(COLOR_ORANGE)It should have something like 'eval \$$(pyenv init -)'$(COLOR_RESET)"

.PHONY: deps-py
deps-py: $(PYTHON_VERSION_FILE) ## Instala Poetry e dependências Python via Poetry
	$(PIP) install --upgrade \
		--index-url $(PYPI_PROXY) \
		pip
	$(PIP) install --upgrade \
		--index-url $(PYPI_PROXY) \
		poetry
	$(POETRY) install

# ------------------------------------------------------------
# DOCKER (Gerenciamento do Ambiente)
# ------------------------------------------------------------
.PHONY: up
up: ## Sobe os containers em background (com rebuild)
	docker-compose up -d --build

.PHONY: down
down: ## Derruba os containers
	docker-compose down

.PHONY: logs
logs: ## Acompanha os logs do container web
	docker-compose logs -f web

.PHONY: shell
shell: ## Abre um shell bash dentro do container web
	docker-compose exec web bash

.PHONY: rebuild
rebuild: down up ## Reconstrói e sobe os containers do zero

# ------------------------------------------------------------
# DJANGO (Dentro do Container)
# ------------------------------------------------------------
.PHONY: migrate
migrate: ## Roda as migrações do Django dentro do container
	docker-compose exec web python manage.py migrate --noinput

.PHONY: seed
seed: ## Popula o banco com dados iniciais (seeds) dentro do container
	docker-compose exec web python manage.py seed

.PHONY: createsuperuser
createsuperuser: ## Cria um superusuário dentro do container
	docker-compose exec web python manage.py createsuperuser

.PHONY: shell-django
shell-django: ## Abre o shell interativo do Django dentro do container
	docker-compose exec web python manage.py shell

# ------------------------------------------------------------
# BUILD & PUBLISH (Pacote Python)
# ------------------------------------------------------------
.PHONY: build
build: ## Constrói o pacote Python
	$(POETRY) build

.PHONY: publish
publish: ## Publica o pacote no PyPI (use com cuidado)
	$(POETRY) publish $(POETRY_PUBLISH_OPTIONS_SET_BY_CI_ENV)

# ------------------------------------------------------------
# TESTES
# ------------------------------------------------------------
.PHONY: test
test: ## Roda os testes com pytest (cobertura, HTML, TAP)
	$(RUN_PYPKG_BIN) pytest \
		$(PYTEST_OPTIONS) \
		tests/   # <-- Agora pega todas as subpastas

# ------------------------------------------------------------
# QUALIDADE DE CÓDIGO (Linters e Formatadores)
# ------------------------------------------------------------
.PHONY: check
check: check-py ## Roda todas as verificações de qualidade

.PHONY: check-py
check-py: check-py-flake8 check-py-black check-py-mypy ## Roda linters Python

.PHONY: check-py-flake8
check-py-flake8:
	$(RUN_PYPKG_BIN) flake8 .

.PHONY: check-py-black
check-py-black:
	$(RUN_PYPKG_BIN) black --check --line-length 91 --fast .

.PHONY: check-py-mypy
check-py-mypy:
	$(RUN_PYPKG_BIN) mypy $(MYPY_OPTS) $(LIBRARY_DIRS)

# ------------------------------------------------------------
# FORMATAÇÃO AUTOMÁTICA
# ------------------------------------------------------------
.PHONY: format
format: format-py format-isort ## Formata todo o código Python

.PHONY: format-py
format-py: ## Formata com Black
	$(RUN_PYPKG_BIN) black .

.PHONY: format-autopep8
format-autopep8: ## Formata com autopep8
	$(RUN_PYPKG_BIN) autopep8 --in-place --recursive .

.PHONY: format-isort
format-isort: ## Ordena os imports com isort
	$(RUN_PYPKG_BIN) isort --recursive .

# ------------------------------------------------------------
# UTILITÁRIOS EXTRAS
# ------------------------------------------------------------
.PHONY: clean
clean: ## Limpa arquivos temporários e cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(BUILD_DIR)