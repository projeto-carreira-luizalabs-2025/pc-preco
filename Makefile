APP_DIR?=app
ROOT_TESTS_DIR?=tests
SCRIPTS_DIR?=scripts
ENV?="$$(dotenv get ENV)"
MAKE_ARGS?=--no-print-directory
API_PATH := ${APP_DIR}/
API_MODULE_MAIN := ${APP_DIR}.api_main
HOST?=0.0.0.0
PORT?=8000
INIT?=uvicorn ${API_MODULE_MAIN}:app --host $(HOST) --port $(PORT)
DOCKER_IMAGE_NAME=pc/preco
DOCKERFILE_PATH=./devtools/docker/dockerfile
CONTAINER_NAME?=pc-preco

clean:
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "*.log" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@find . -name ".pytest_cache" -type d | xargs rm -rf
	@rm -f .coverage
	@rm -f .coverage.NB-SBDEV*
	@rm -rf htmlcov/
	@rm -f coverage.xml
	@rm -f *.log
	@rm -f .env.bkp*

# Criar o diretório venv
build-venv:
	python3.12 -m venv venv

# Instalar os pacotes
requirements-dev:
	pip install --upgrade pip
	@pip install -r requirements/develop.txt

lint:
	isort ${APP_DIR} ${ROOT_TESTS_DIR}
	bandit -c pyproject.toml -r -f custom ${APP_DIR} ${ROOT_TESTS_DIR}
	black ${APP_DIR} ${ROOT_TESTS_DIR}
	flake8 --max-line-length=120 ${APP_DIR} ${ROOT_TESTS_DIR}

# Verificar o código
check-lint:
	isort -c ${APP_DIR} ${ROOT_TESTS_DIR}
	bandit -c pyproject.toml -r -f custom ${APP_DIR} ${ROOT_TESTS_DIR}
	black --check ${APP_DIR} ${ROOT_TESTS_DIR}
	flake8 --max-line-length=120 ${APP_DIR} ${ROOT_TESTS_DIR}
	mypy ${APP_DIR} ${ROOT_TESTS_DIR}

safety:
	@pip-audit -r requirements/base.txt

dead-fixtures:
ifeq ($(OS),Windows_NT)
	@cmd /C "set ENV=$(ENV)&& pytest --dead-fixtures"
else
	@ENV=$(ENV) pytest --dead-fixtures
endif

test:
ifeq ($(OS),Windows_NT)
	@cmd /C "set ENV=test&& pytest ${ROOT_TESTS_DIR}/"
else
	@ENV=test pytest ${ROOT_TESTS_DIR}/
endif

.PHONY: build test run
build: check-lint test

pop-env:
	@./devtools/scripts/pop-env

load-env:
	@./devtools/scripts/push-env "devtools/dotenv.$(env)"

load-dev-env:
ifeq ($(OS),Windows_NT)
	@cmd /C "set env=dev&& make $(MAKE_ARGS) load-env"
else
	@env=dev make $(MAKE_ARGS) load-env
endif

# Carregar a variável 
load-test-env:
ifeq ($(OS),Windows_NT)
	@cmd /C "set env=test&& make $(MAKE_ARGS) load-env"
else
	@env=test make $(MAKE_ARGS) load-env
endif

.PHONY: run
run:
	$(INIT)

run-dev:
ifeq ($(OS),Windows_NT)
	@cmd /C "set ENV=dev&& $(INIT) --reload"
else
	@ENV=dev $(INIT) --reload
endif

docker-build:
	docker build -f $(DOCKERFILE_PATH) -t $(DOCKER_IMAGE_NAME) .

docker-run:
	docker run --rm --name $(CONTAINER_NAME) -e ENV=dev -e app_db_url=$(APP_DB_URL) -p 8000:8000 $(DOCKER_IMAGE_NAME)

docker-shell:
	docker run --rm -it --name $(CONTAINER_NAME) -e ENV=dev $(DOCKER_IMAGE_NAME) /bin/bash

docker-compose-sonar-up:
	docker compose -f ./devtools/docker/docker-compose-sonar.yml up -d

docker-compose-sonar-down:
	docker compose -f ./devtools/docker/docker-compose-sonar.yml down

docker-compose-up:
	docker compose -f ./devtools/docker/docker-compose.yml up -d

docker-compose-down:
	docker compose -f ./devtools/docker/docker-compose.yml down
# Subir o docker para os testes

docker-tests-up:
	docker-compose up -d

# Descer e remover o docker dos testes
docker-tests-down:
	docker-compose down -v

# Testar fazendo a cobertura do código
coverage:
ifeq ($(OS),Windows_NT)
	@cmd /C "set ENV=test&& pytest --cov=${APP_DIR} --cov-report=term-missing --cov-report=xml ${ROOT_TESTS_DIR} --cov-fail-under=90 --durations=5"
else
	@ENV=test pytest --cov=${APP_DIR} --cov-report=term-missing --cov-report=xml ${ROOT_TESTS_DIR} --cov-fail-under=90 --durations=5
endif

coverage-no-fail:
ifeq ($(OS),Windows_NT)
	@cmd /C "set ENV=test&& pytest --cov=${APP_DIR} --cov-report=term-missing --cov-report=xml ${ROOT_TESTS_DIR}"
else
	@ENV=test pytest --cov=${APP_DIR} --cov-report=term-missing --cov-report=xml ${ROOT_TESTS_DIR}
endif

coverage-html:
ifeq ($(OS),Windows_NT)
	@cmd /C "set ENV=test&& pytest --cov=${APP_DIR} --cov-report=term-missing --cov-report=html ${ROOT_TESTS_DIR}"
else
	@ENV=test pytest --cov=${APP_DIR} --cov-report=term-missing --cov-report=html ${ROOT_TESTS_DIR}
endif

# Realizar a migração do banco de dadosAdd commentMore actions
migration:
	alembic revision --autogenerate -m "$(MSG)" && alembic upgrade head
