# pc-preco

## 📌 O que é este projeto?

O `pc-preco` é um microsserviço que gerencia e fornece os **preços de produtos** exibidos ao consumidor final no marketplace, considerando:

- Preço à vista (com ou sem desconto)
- Preço a prazo (com ou sem juros)
- Variação de preços por vendedor (mesmo produto, diferentes preços)

Ele se integra com outros microsserviços para garantir que o preço exibido ao consumidor final seja o mais preciso possível.

### 🔗 Integrações

- `pc-catalogo`: para identificar a qual produto o preço se refere.
- `pc-identidade`: para saber qual varejista está ofertando o preço.
- `pc-estoque`: para que o preço exibido esteja alinhado à disponibilidade do produto.
- `pc-frete`: que junto ao preço, compõe o custo final percebido pelo consumidor.

Cada microsserviço mantém responsabilidades bem definidas, mas trabalham de forma integrada para oferecer uma experiência de compra completa.

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

- **Linguagem**: [Python 3.12](https://docs.python.org/3.12/)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Banco de Dados**: [PostgreSQL](https://www.postgresql.org/)
- **Docker**: Containers para app, banco e SonarQube
- **Testes**: [Pytest](https://docs.pytest.org/)
- **Code Quality**: [SonarQube](https://www.sonarsource.com/products/sonarqube/)
- **Gerenciador de dependências**: Pip + `requirements.txt`
- **Makefile**: Automação de tarefas comuns
- **Documentação de API**: Swagger (via FastAPI)

## 🧰 Configuração do ambiente local

Todos os comandos serão via terminal (Linux 🐧).

1️⃣ Clone o projeto em sua máquina:

```bash
git clone https://github.com/projeto-carreira-luizalabs-2025/pc-preco.git
```

2️⃣ Acesse o diretório:

```bash
cd pc-preco
```

3️⃣ Crie o [ambiente virtual](https://docs.python.org/3.12/tutorial/venv.html):

```bash
make build-venv # Instala as bibliotecas para trabalhar com o projeto
# Ou:
# python3.12 -m venv venv
```

4️⃣ Ative o [ambiente virtual](https://docs.python.org/3.12/tutorial/venv.html):

```bash
. ./venv/bin/activate
# ou
# source ./venv/bin/activate
```

Quaisquer comandos daqui para frente, iremos considerar que você está dentro
do ambiente virtual `(venv)`.

5️⃣ Instale as dependências

```bash
make requirements-dev
```

## 🛠️ Execução local

Após configurar o ambiente local e ativar o ambiente virtual, você pode rodar a aplicação localmente com os seguintes comandos:

1️⃣ Carregue as variáveis de ambiente para o modo de teste:

```bash
make load-test-env
```

2️⃣ Inicie a API em modo desenvolvimento:

```bash
make run-dev
```

Após iniciar a aplicação, consulte a seção [📘 Acesso à documentação da API](#-acesso-a-documentação-da-api) para saber como acessá-la.

## 🐳 Execução com Docker

1️⃣ Construir a imagem

```bash
make docker-build # Esse comando criará uma imagem Docker chamada pc/preco.
```

2️⃣ Executar a aplicação

```bash
make docker-run # Inicia um contêiner chamado pc-preco
```

3️⃣ Executar com serviços auxiliares (como PostgreSQL)

```bash
make docker-compose-up # Sobe o BD PostgreSQL e demais serviços definidos no docker-compose.yml
```

**🛑 ATENÇÃO: Execute o comando abaixo apenas se quiser:**

1️⃣ Parar e remover contêineres

```bash
make docker-compose-down # Encerra e remove os contêineres gerenciados pelo Docker Compose.
```

2️⃣ Acessar o shell do contêiner

Se precisar acessar o shell do contêiner para depuração ou outras operações:

```bash
make docker-shell # Abre uma sessão bash interativa dentro do contêiner para depuração ou comandos manuais.
```

🔗 Após iniciar a aplicação, consulte a seção [📘 Acesso à documentação da API](#-acesso-a-documentação-da-api) para instruções detalhadas de como acessá-la.

## 📘 Acesso à documentação da API

Após iniciar a aplicação (localmente ou via Docker), a documentação da API estará disponível nos seguintes endereços:

- Swagger UI: [localhost:8000/api/docs](http://0.0.0.0:8000/api/docs)
- ReDoc: [localhost:8000/redoc](http://0.0.0.0:8000/redoc)

## 🧪 Testes

Para rodar os testes automatizados do projeto, use o comando abaixo:

```bash
make test
```

## 🔍 Análise de qualidade com SonarQube

Para subir o ambiente do SonarQube, execute:

```bash
make docker-compose-sonar-up # Inicia o servidor SonarQube e seus serviços dependentes.
```

### ⚠️ Possível erro: vm.max_map_count

Durante a inicialização do SonarQube, você pode se deparar com o seguinte erro:

```bash
vm.max_map_count [65530] is too low
```

Esse problema ocorre porque o Elasticsearch (utilizado pelo SonarQube) exige que `vm.max_map_count` seja pelo menos `262144`.

### ✅ Como resolver

Siga os passos abaixo para ajustar esse parâmetro no seu sistema:

1️⃣ Verifique o valor atual:

```bash
sysctl vm.max_map_count
```

Se o valor for menor que 262144, prossiga com os próximos passos.

2️⃣ Aumente temporariamente (até o próximo reboot):

```bash
sudo sysctl -w vm.max_map_count=262144
```

3️⃣ Torne o valor permanente:

Abra o arquivo de configurações:

```bash
sudo nano /etc/sysctl.conf
```

Adicione a seguinte linha ao final do arquivo:

```bash
vm.max_map_count=262144
```

Salve o arquivo e aplique a configuração:

```bash
sudo sysctl -p
```

### 🌐 Acessando o SonarQube

Após o ambiente estar no ar, acesse a interface web pelo endereço: `http://localhost:9000`

Para encerrar o ambiente, utilize:

```bash
make docker-compose-sonar-down # Esse comando irá desligar e remover os contêineres do SonarQube.
```

### 🔐 Gerando Token de Autenticação

1️⃣ Acesse o SonarQube: http://localhost:9000

2️⃣ Vá até: **My Account** > **Security**

3️⃣ Gere um token de autenticação pessoal ( _Guarde-o com segurança — ele não poderá ser visualizado novamente._ )

4️⃣ No terminal, exporte as variáveis de ambiente:

```bash
export SONAR_TOKEN=<seu_token>
export SONAR_HOST_URL=http://localhost:9000
```

5️⃣ Execute o Scanner:

```bash
pysonar-scanner
```

Ao finalizar, o SonarQube exibirá um relatório completo de qualidade do código na interface web.

## 📁 Estrutura do projeto

```bash
.
├── README.md
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
│   └── docker                  # Arquivos e configurações para Docker (ex: Dockerfile, docker-compose-sonar.yml)
│   └── scripts/                # Scripts automatizados usados no `makefile` (ex: configuração de ambiente)
│   └── info-projeto.md         # Documento de levantamento de requisitos
├── requirements/
├── tests                       # Pasta para testes da aplicação
│   └── unit                    # Testes unitários
├── makefile                    # Comandos automatizados (ex: build, run, test)
├── pyproject.toml
├── requirements.txt
├── sonar-project.properties    # Configurações do SonarQube
```
