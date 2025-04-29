<div align="center">
  <h1>🐍 Boilerplate Projeto Carreira 🐍</h1>
  <!-- Substituir a descrição abaixo. Insira uma breve descrição do propósito do seu front. -->
   Template de uma aplicação API Python com FastAPI.
</div>

## Introdução
<!-- Este tópico pode ser removido na documentação do seu app. -->

Este repositório contém um código boilerplate desenvolvido pelos desenvolvedores da plataforma seller. O objetivo deste boilerplate é servir como uma fundação sólida e padronizada para os diversos projetos que serão desenvolvidos a partir dele. Este código base facilita a consistência e a eficiência no desenvolvimento, assegurando que todos os projetos iniciem com uma estrutura comprovada e otimizada.

Lembre-se de seguir os padrões definidos para nosso projetos nos docs: Padrões - [Plataforma do Seller](https://magazine.atlassian.net/wiki/spaces/Maganets/pages/3495559495/Padr+es+-+Plataforma+do+Seller)

### Uso
O código boilerplate é projetado para ser facilmente replicado e modificado. O processo padrão de uso envolve:

* **Fork do Projeto**: Os desenvolvedores devem fazer um fork deste repositório para criar uma nova instância do boilerplate, que pode ser personalizada conforme necessário.
* **Customização**: Após o fork, o código pode ser adaptado para as necessidades específicas do novo projeto.
* **Integração**: O novo projeto integrará as ferramentas e bibliotecas especificadas, mantendo a estrutura base fornecida pelo boilerplate.

## 📄 Documentação

<!-- Colar o design docs da sua aplicação no link abaixo -->

Você pode encontrar a documentação completa referente a este projeto neste [design docs](substituir com o link do seu design doc)


## 💻 Tecnologias
Este projeto foi construído usando várias tecnologias chaves para garantir performance, segurança e facilidade de uso:

* **Python 3.12**: Escolhido por sua simplicidade e poderosas capacidades de programação. A versão 3.13 é a mais recente, oferecendo melhorias significativas em eficiência e recursos linguísticos.
* **FastAPI**: Uma moderna e rápida (altas performances) web framework para Python, que é ideal para a construção de APIs.


## ✨ Configuração do ambiente local

Todos os comandos serão via terminal (Linux 🐧).

Este _seed_ trabalha com o [Python 3.12](https://docs.python.org/3.12/), confirme se o mesmo está instalado em sua máquina.

Depois de clonar o projeto, acesse o diretório:

```sh
cd ps-boilerparte
```

Crie o [ambiente virtual](https://docs.python.org/3.12/tutorial/venv.html)
para instalar as bibliotecas e trabalharmos com o projeto:

```sh
make build-venv
# Ou:
# python3.12 -m venv venv
```

Uma vez criado o ambiente virtual do Python, você precisa ativá-lo
(estou supondo que você está no Linux 🐧):

```sh
. ./venv/bin/activate
# ou
# source ./venv/bin/activate
```

Quaisquer comandos daqui para frente, iremos considerar que você está dentro
do ambiente virtual `(venv)`.

Instale as bibliotecas necessárias para o seu projeto, veja com a equipe qual é a URL do [pypi](https://pypi.org/) do Magalu e defina o seu valor para `PIP_LUIZALABS_URL`. Execute os comandos:

```sh
# Definindo a PIP do Magalu
export PIP_LUIZALABS_URL=<pega com alguém 😉>
# Verifique se sua PIP foi gerada
echo $PIP_LUIZALABS_URL
# Instala os pacotes.
make requirements-dev
# OU instale sem o makefile:
# pip install -i $PIP_URL -r requirements/develop.txt
# Instala configurações do pre-commit
make install-pre-commit
```

### 🐳 Para instalar o Docker 

Instalação do [Docker](https://docs.docker.com/engine/install/ubuntu/)

## ⭐  Formatação de lint e código

O aplicativo usa [black](https://black.readthedocs.io/en/stable/) para formatação de código com [isort](https://pycqa.github.io/isort/) para classificação de importação, [flake8](https://flake8.pycqa.org/en/latest/) para aplicação de guia de estilo e, por último, o mypy para verificação de tipo estático.

Para executar a validação do lint, execute:
```bash
$ make lint
```

Para se gerar novos commits, favor seguir o padrão do https://commitlint.io/


## ▶️ Execução

Após a configuração dos pacotes e docker compose, se você deseja executar seu projeto localmente, configure o arquivo de env:
```bash
$ make load-test-env
```

Use o comando para criar os tópicos localmente:
```bash
$ make pubsub-create-topics
```

Use o comando para subir a api:
```bash
$ make run-dev
```
Acesse a doc da API em: [localhost:8000/api/docs](http://0.0.0.0:8000/api/docs) ou em [localhost:8000/redoc](http://0.0.0.0:8000/redoc)

Para rodar os workers configurados no .env:
```bash
$ make run-workers
```

## Contribuições e Atualizações
O projeto está aberto a contribuições e atualizações da comunidade. O processo para contribuições é o seguinte:

* **Pull Requests**: Contribuições devem ser submetidas como pull requests.
* **Code Review**: Cada pull request passará por um code review detalhado pela equipe. Isso garante que o código esteja alinhado com os padrões de qualidade e funcionamento do projeto.
* **Incorporação de Mudanças**: Após a aprovação no code review, as mudanças serão integradas ao código principal.



## 📖 Recursos úteis

- [Conventional Commits](https://www.conventionalcommits.org)

## 👍 Merge Requests

- Fluxo de desenvolvimento e entrega contínua documentado no Kanban.
