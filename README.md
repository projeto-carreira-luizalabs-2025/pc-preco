# pc-preco

## 📌 O que é este projeto?

O `pc-preco` é um microsserviço que gerencia e fornece os **preços de produtos** exibidos ao consumidor final no marketplace, considerando:

- Preço à vista (com ou sem desconto)
- Preço a prazo (com ou sem juros)
- Variação de preços por vendedor (mesmo produto, diferentes preços)

## 👥 Equipe

- Carlos Eduardo
- Eduardo Ribeiro
- João Lucas Ferreira
- Layza Nauane De Paula Silva

## 📄 Design e documentação

<!-- Colar o design docs da sua aplicação no link abaixo -->

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
# Inicie os contêineres da aplicação, postgreSQL e Keycloak
make docker-compose-up

# Ajuste o arquivo .env alterando a variável APP_DB_URL para apontar para o seu banco de dados PostgreSQL local. 
APP_DB_URL: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE_NAME.

# Se desejar parar e remover os contêineres, execute: 
make docker-compose-down 
```

2.  Migração PostgreSQL

```bash
# Instale localmente
pip install alembic==1.16.1 psycopg2-binary==2.9.10

# Crie o ambiente de migração
alembic init alembic
```

Edite o arquivo env.py para carregar a variável de ambiente APP_DB_URL, tal como deixamos no arquivo dotenv.dev.txt.

3. Aplique as migrações
   
```bash
# Inicie a primeira migração:
alembic revision --autogenerate -m "anything-creeate"

# Rode a migração:
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
├── README.md
├── alembic/
│   └── versions
├── app/                        # Código-fonte principal da aplicação (Em construção)
│   └── api/                    # Rotas, controladores e interfaces REST da aplicação
│   └── common/                 # Utilitários e código compartilhado
│   └── integrations/           # Integrações com sistemas externos
│   └── models/                 # Definições de modelos para rotas
│   └── repositories/           # Persistência e acesso a banco de dados
│   └── services/               # Regras de negócio da aplicação
│   └── settings/               # Configurações da aplicação
│   └── worker/
├── devtools/                   # Ferramentas e scripts auxiliares para desenvolvimento
|   └── api/
│   └── docker/                  # Arquivos e configurações para Docker (ex: Dockerfile, docker-compose-sonar.yml)
|   └── keycloack-config/
│   └── scripts/                # Scripts automatizados usados no `makefile` (ex: configuração de ambiente)
│   └── info-projeto.md         # Documento de levantamento de requisitos
├── requirements/
├── tests/                       # Pasta para testes da aplicação
│   └── factories
│   └── fixtures
│   └── unit                    # Testes unitários
├── venv/
├── makefile                    # Comandos automatizados (ex: build, run, test)
├── pyproject.toml
├── requirements.txt
├── sonar-project.properties    # Configurações do SonarQube
```

## 📫 Contribuições

O projeto está aberto a contribuições. O fluxo para contribuição é o seguinte:

1. Realize um fork do repositório.
2. Crie uma branch descritiva para a sua feature ou correção.
3. Submeta um Pull Request.
4. Aguarde o Code Review pela equipe de desenvolvimento.
5. Após a aprovação, sua alteração será integrada ao código principal.
