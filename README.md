# pc-preco

## 📌 O que é este projeto?

O `pc-preco` é um microsserviço que gerencia e fornece os **preços de produtos** do seller do marketplace:

- Preço de custo
- Preço de venda

## 👥 Equipe

- Carlos Eduardo
- Eduardo Ribeiro
- João Lucas Ferreira
- Layza Nauane De Paula Silva

## 📄 Design e documentação

Você pode encontrar a documentação inicial referente a este projeto neste [design docs](https://github.com/projeto-carreira-luizalabs-2025/pc-preco/blob/main/devtools/info-projeto.md)

```bash
.
├── devtools/
    └── info-projeto.md # Documento de levantamento da informação base
```

## 💻 Tecnologias

- **Linguagem:** [Python 3.12](https://docs.python.org/3.12/)
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Banco de Dados:** [PostgreSQL](https://www.postgresql.org/)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
- **Migração:** [Alembic](https://alembic.sqlalchemy.org/en/latest/)
- **Autenticação e Autorização:** [Keycloak](https://www.keycloak.org/)
- **Caching:** [Redis](https://redis.io/)
- **Filas de mensagens:** [RabbitMQ](https://www.rabbitmq.com/)
- **Orquestração:** [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/)
- **Documentação da API:** [Swagger](https://swagger.io/)
- **Testes:** [Pytest](https://docs.pytest.org/)
- **Qualidade:** [SonarQube](https://www.sonarsource.com/products/sonarqube/)
- **IA**: [Ollama](https://ollama.com/)

## 🧰 Configuração do ambiente virtual

Todos os comandos serão via terminal (Linux 🐧).

1. Clone o projeto em sua máquina:

```bash
git clone https://github.com/projeto-carreira-luizalabs-2025/pc-preco.git
```

2. Crie o [ambiente virtual](https://docs.python.org/3.12/tutorial/venv.html):

```bash
# Linux
make build-venv

# Windows
python3.12 -m venv venv
```

3. Ative o [ambiente virtual](https://docs.python.org/3.12/tutorial/venv.html):

```bash
# Linux
source ./venv/bin/activate

# Windows
./venv/bin/activate
```

4. Instale as dependências

```bash
make requirements-dev
```

5. Copie o arquivo de ambiente

```bash
# Linux
make load-dev-env

# Windows
cp ./devtools/dotenv.dev .env
```

Quaisquer comandos daqui para frente, iremos considerar que você está dentro
do ambiente virtual `(venv)`.

## ⚙️ Configuração do Banco de Dados

1. Configuração dos contêineres da aplicação

```bash
# Inicie os contêineres da aplicação (PostgreSQL, Keycloak, RabbitMQ, Redis e Ollama)
make docker-compose-up

# Se desejar parar e remover os contêineres, execute:
make docker-compose-down
```

2. Migração PostgreSQL

```bash
# Rode as migrações:
make migration
# ou
alembic upgrade head
```

## 🛠️ Execução

Com o ambiente virtual ativado, você pode rodar a aplicação executando:

```bash
# Linux
make run-dev

# Windows
uvicorn app.api_main:app --reload
```

## 🛠️ Criação de filas e execução de workers

Nosso projeto utiliza filas para gerenciar o processamento assíncrono de tarefas, garantindo maior escalabilidade, desacoplamento e performance na aplicação.

### ⚙️ Criação das filas

Para criar as filas no RabbitMQ, execute o comando correspondente ao seu sistema operacional, em um novo terminal:

```bash
# Linux
make create-queue

# Windows
python -m devtools.scripts.queue.create_queue
```

### ⚙️ Execução dos workers

Além das filas, temos workers responsáveis por consumir e processar as mensagens inseridas nelas.

Para executar os workers (o terminal deve permanecer aberto durante a execução), use:

```bash
# Linux
make worker

# Windows
python -m app.worker.worker_main
```


## 📘 Acesso à documentação da API

Após iniciar a aplicação (localmente ou via Docker), a documentação da API estará disponível nos seguintes endereços:

- Swagger UI: [localhost:8000/api/docs](http://0.0.0.0:8000/api/docs)
- ReDoc: [localhost:8000/redoc](http://0.0.0.0:8000/redoc)

## 🧪 Testes e Qualidade de Código

### 📂 Estrutura dos testes

Os testes estão organizados na pasta `tests/`:

```bash
tests/
└── unit/         # Testes unitários de funções, serviços, modelos e repositórios
└── factories/    # Fábricas e mocks para facilitar a criação de objetos de teste
└── conftest.py   # Fixtures globais do pytest
```

### 📝 O que é testado

- **Modelos:** Validação, criação e atualização de entidades.
- **Serviços:** Regras de negócio e fluxos principais.
- **Repositórios:** Operações de CRUD e acesso ao banco de dados.
- **APIs:** Testes de integração das rotas principais.
- **Workers:** Processamento assíncrono de tarefas, execução de rotinas em background e integração com sistemas externos.

### 🚀 Como executar os testes

Para rodar os testes automatizados do projeto, use os comandos abaixo:

```bash
# Linux
make test

# Windows
pytest
```

### 📈 Cobertura de testes

Para verificar a cobertura dos testes, execute:

```bash
# Linux
make coverage
# ou
make coverage-html

# Windows
pytest --cov=app --cov-report=html
```

O relatório será gerado na pasta `htmlcov/`. Você pode abrir o arquivo `index.html` em seu navegador para visualizar os detalhes.

## 🔍 Análise de qualidade com SonarQube

1. Inicie o SonarQube:

```bash
make docker-compose-sonar-up # Inicia o servidor SonarQube e seus serviços dependentes.
```

ATENÇÃO: Se ocorrer o erro de `vm.max_map_count`, consulte [Solução de Problemas](#erro-sonar-vm-max-map-count)

2. Gere o Token de Autenticação

   1. Acesse interface web do SonarQube: [SonarQube](http://localhost:9000)
   2. Vá até: **My Account** > **Security**
   3. Gere um token de autenticação pessoal ( _Guarde-o com segurança — ele não poderá ser visualizado novamente._ )

3. No terminal, exporte as variáveis de ambiente:

```bash
export SONAR_TOKEN=<seu_token>
export SONAR_HOST_URL=http://localhost:9000
```

4. Execute o Scanner:

```bash
pysonar-scanner
```

5. Para encerrar o ambiente, utilize:

```bash
# Esse comando irá desligar e remover os contêineres do SonarQube.
make docker-compose-sonar-down
```

Ao finalizar, o SonarQube exibirá um relatório completo de qualidade do código na interface web.

## ⚠️ Solução de Problemas

### <a id="erro-sonar-vm-max-map-count"></a> 🐛 Erro sonar vm.max_map_count>

Durante a inicialização do SonarQube, você pode se deparar com o seguinte erro:

```bash
vm.max_map_count [65530] is too low
```

Esse problema ocorre porque o Elasticsearch (utilizado pelo SonarQube) exige que `vm.max_map_count` seja pelo menos `262144`.

### ✅ Como resolver

Para ajustar esse parâmetro no seu sistema:

1. Verifique o valor atual:

```bash
sysctl vm.max_map_count
```

Se o valor for menor que 262144, prossiga com uma das seguintes opções:

2. Aumente temporariamente (até o próximo reboot)

```bash
sudo sysctl -w vm.max_map_count=262144
```

3. Torne o valor permanente

   1. Abra o arquivo de configurações:

   ```bash
   sudo nano /etc/sysctl.conf
   ```

   2. Adicione a seguinte linha ao final do arquivo:

   ```bash
    vm.max_map_count=262144
   ```

   3. Salve o arquivo e aplique a configuração

   ```bash
    sudo sysctl -p
   ```

## 📁 Estrutura do projeto

```bash
.
.
├── README.md                       # Documentação principal do projeto, instruções de uso e informações gerais.
├── alembic/                        # Diretório de controle de versões de migrações do banco de dados (usando Alembic).
│   └── versions/                   # Scripts de migração gerados pelo Alembic.
├── app/                            # Código-fonte principal da aplicação.
│   └── api/                        # Implementação da camada de API da aplicação.
│   └── common/                     # Utilitários e código compartilhado entre módulos.
│   └── integrations/               # Integrações com sistemas externos (ex: APIs, filas, etc).
│   └── models/                     # Definições de modelos de dados (ex: Pydantic, ORM).
│   └── repositories/               # Persistência e acesso a banco de dados.
│   └── services/                   # Regras de negócio e lógica da aplicação.
│   └── settings/                   # Configurações e variáveis de ambiente da aplicação.
│   └── worker/                     # Implementação de workers e processamento assíncrono.
├── devtools/                       # Ferramentas e scripts auxiliares para desenvolvimento.
│   └── api/                        # Arquivos http para execução de rotas da api fora do swagger.
│   └── docker/                     # Arquivos e configurações para Docker (ex: Dockerfile, docker-compose-sonar.yml).
│   └── keycloack-config/           # Configurações e scripts para Keycloak (autenticação/autorização).
│   └── scripts/                    # Scripts automatizados usados no Makefile (ex: configuração de ambiente, filas).
│   └── info-projeto.md             # Documento de levantamento de requisitos e informações do projeto.
├── requirements/                   # Diretório com arquivos de dependências do projeto.
│   └── base.txt                    # Dependências principais da aplicação.
│   └── develop.txt                 # Dependências adicionais para desenvolvimento.
├── tests/                          # Testes automatizados da aplicação.
│   └── factories/                  # Fábricas de objetos para testes.
│   └── fixtures/                   # Fixtures para testes.
│   └── unit/                       # Testes unitários.
├── venv/                           # Ambiente virtual Python (gerado localmente, não versionar).
├── makefile                        # Comandos automatizados para build, testes, lint, etc.
├── pyproject.toml                  # Configuração de ferramentas Python (ex: Black, isort, pytest).
├── requirements.txt                # Lista geral de dependências.
├── sonar-project.properties        # Configurações do SonarQube para análise de qualidade de código.
```

## 📫 Contribuições

O projeto está aberto a contribuições. O fluxo para contribuição é o seguinte:

1. Realize um fork do repositório.
2. Crie uma branch descritiva para a sua feature ou correção.
3. Submeta um Pull Request.
4. Aguarde o Code Review pela equipe de desenvolvimento.
5. Após a aprovação, sua alteração será integrada ao código principal.
