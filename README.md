# pc-preco

## 📌 O que é este projeto?

O `pc-preco` é um microsserviço responsável por gerenciar e expor as **informações de preço** dos produtos vendidos por
varejistas no marketplace.

Esse serviço tem como função principal fornecer os valores exibidos ao consumidor final, considerando diferentes
condições de pagamento, como:

- Preço à vista (com ou sem desconto)
- Preço a prazo (com ou sem juros)
- Variações por vendedor (mesmo produto, diferentes preços)

Ele se integra diretamente com os microsserviços de:

- `pc-catalogo`: para identificar a qual produto o preço se refere.
- `pc-identidade`: para saber qual varejista está ofertando o preço.

Além disso, o `pc-preco` atua em conjunto com:

- `pc-estoque`: para que o preço exibido esteja alinhado à disponibilidade do produto.
- `pc-frete`: que junto ao preço, compõe o custo final percebido pelo consumidor.

Cada microsserviço mantém responsabilidades bem definidas, mas trabalham de forma integrada para oferecer uma
experiência de compra completa.

## 👥 Equipe

- Carlos Eduardo
- Eduardo Ribeiro
- João Lucas Ferreira
- Layza Nauane De Paula Silva

## 📄 Documentação

<!-- Colar o design docs da sua aplicação no link abaixo -->

Você pode encontrar a documentação inicial referente a este projeto neste [design docs](https://github.com/projeto-carreira-luizalabs-2025/pc-preco/blob/main/devtools/info-projeto.md)

```bash
.
├── devtools/
    └── info-projeto.md     # Documento de levantamento da informação base
```

## 💻 Tecnologias

Este projeto foi construído usando várias tecnologias chaves para garantir performance, segurança e facilidade de uso:

- **Python 3.12**: Escolhido por sua simplicidade e poderosas capacidades de programação. A versão 3.13 é a mais recente, oferecendo melhorias significativas em eficiência e recursos linguísticos.
- **FastAPI**: Uma moderna e rápida (altas performances) web framework para Python, que é ideal para a construção de APIs.
- O restante das dependências estão em `requirements`.

## ✨ Configuração do ambiente local

Todos os comandos serão via terminal (Linux 🐧).

Este projeto trabalha com [Python 3.12](https://docs.python.org/3.12/), confirme se o mesmo está instalado em sua máquina.

Clone o projeto em sua máquina:

```bash
git clone https://github.com/projeto-carreira-luizalabs-2025/pc-preco.git
```

Depois de clonar o projeto, acesse o diretório:

```bash
cd ps-preco
```

Crie o [ambiente virtual](https://docs.python.org/3.12/tutorial/venv.html)
para instalar as bibliotecas e trabalharmos com o projeto:

```bash
make build-venv
# Ou:
# python3.12 -m venv venv
```

Uma vez criado o ambiente virtual do Python, você precisa ativá-lo
(estou supondo que você está no Linux 🐧):

```bash
. ./venv/bin/activate
# ou
# source ./venv/bin/activate
```

Quaisquer comandos daqui para frente, iremos considerar que você está dentro
do ambiente virtual `(venv)`.

Instale as dependências usando os requirements

```bash
make requirements-dev
```

## ▶️ Execução

Após configuração do ambiente local, caso desejar executar o projeto localmente, configure o arquive de env:

```bash
make load-test-env
```

Use o comando para subir a api:

```bash
make run-dev
```

Acesse a doc da API em: [localhost:8000/api/docs](http://0.0.0.0:8000/api/docs) ou em [localhost:8000/redoc](http://0.0.0.0:8000/redoc)

## 📦 Pré-requisitos (ambiente Python)

Antes de rodar os testes, executar a aplicação localmente ou realizar a análise de qualidade com o SonarQube, certifique-se de:

```bash
make build-venv
make requirements-dev
```

Esses comandos criam o ambiente virtual e instalam as dependências necessárias para o funcionamento do projeto.

## 🧪 Testes

Para rodar os testes automatizados do projeto, use o comando abaixo:

```bash
make test
```
## 🐳 Docker

Para construir a imagem Docker da aplicação, execute:

``` bash
make docker-build # Criará uma imagem com o nome pc/preco.
```

Para rodar a aplicação em um contêiner Docker:

``` bash
make docker-run # Iniciará um contêiner chamado pc-preco, expondo a porta 8000 do contêiner para a porta 8000 do seu host.
```

Se precisar acessar o shell do contêiner para depuração ou outras operações:

```bash
make docker-shell # Isso abrirá uma sessão bash interativa dentro do contêiner.
```

## 🔍 Análise de Qualidade com SonarQube

Para subir o ambiente do SonarQube com Docker Compose, execute:

``` bash
make docker-compose-sonar-up # Inicia o servidor SonarQube e seus serviços dependentes (como o banco de dados) via Docker Compose
```

Após a execução, acesse a interface web do SonarQube em: http://localhost:9000

Se em algum momento quiser parar o ambiente do SonarQube, execute:

```bash
make docker-compose-sonar-down # Desligará o ambiente do SonarQube e removerá os contêineres
```

🔐 Gerar Token de Autenticação

1. Acesse o SonarQube: http://localhost:9000

2. Vá em: **My Account** > **Security**

3. Gere um token de autenticação pessoal. Guarde-o bem, pois você não terá acesso a ele novamente.

4. Exporte as variáveis de ambiente com o token gerado:

``` bash
export SONAR_TOKEN=<seu_token>
export SONAR_HOST_URL=http://localhost:9000 pysonar-scanner
```

Após isso, o SonarQube exibirá um relatório completo de qualidade do código na interface web.

## 📁 Estrutura do projeto

```bash
.
├── README.md                   # Documentação principal do projeto: informações do projeto, instruções de setup, uso e execução
├── app/                        # Diretório principal do código-fonte da aplicação (em construção)
│   └── api/                    # Rotas, controladores e interfaces REST da aplicação
│   └── common/                 # Utilitários, constantes, exceções e helpers compartilhados entre os módulos
│   └── integrations/           # Integrações com sistemas externos
│   └── models/                 # Definições de modelos para rotas
│   └── repositories/           # Módulos para interação com o banco de dados e persistência de dados
│   └── services/               # Camada de lógica de negócio da aplicação
│   └── settings/               # Configurações da aplicação
│   └── worker/                 
├── devtools/                   # Ferramentas e scripts auxiliares para desenvolvimento
│   └── docker                  # Arquivos e configurações para Docker (ex: Dockerfile, docker-compose-sonar.yml)
│   └── scripts/                # Scripts automatizados usados no `makefile` (ex: configuração de ambiente)
│   └── info-projeto.md         # Documento de levantamento da informação base
├── requirements/               # Pasta com arquivos de dependências específicas (ex: develop.txt, base.txt)
├── tests                       # Pasta para testes da aplicação
│   └── unit                    # Testes unitários para módulos e funções específicas
├── venv                        # Ambiente virtual Python para isolamento de dependências
├── makefile                    # Automatiza tarefas comuns do projeto (ex: build, test, run)
├── pyproject.toml              # Arquivo de configuração do projeto Python
├── requirements.txt            # Lista geral de dependências do projeto
├── sonar-project.properties    # Configurações para o SonarQube Scanner
```
