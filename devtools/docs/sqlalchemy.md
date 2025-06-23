# SQLAlchemy e Postgresql

Este tutorial irá guiá-los pelos passos básicos para configurar um ambiente, conectar-se a um banco de dados 
[PostgreSQL](https://www.postgresql.org/) e realizar operações CRUD (Create, Read, Update, Delete) 
usando o [SQLAlchemy](https://www.sqlalchemy.org/).

## Pré-requisitos

Antes de começar, certifique-se de ter o seguinte:

1. Python 3.12 instalado.
2. PostgreSQL _instalado_ com o nosso [docker-compose](../../docker-compose.yml).

```shell
docker-compose up
```

3.  Um banco de dados PostgreSQL criado (vamos usar um chamado `bd01`). 

Teste o acesso:

```bash
docker exec -it postgresql psql -U admin -h localhost bd01
```
4. Configure o ambiente Python:

```shell
python3.12 -m venv venv
# No Windows
.\venv\Scripts\activate
# No macOS/Linux
source venv/bin/activate
```

Instale as bibliotecas: Precisamos do SQLAlchemy e do driver Python para PostgreSQL (psycopg2).

```shell
pip install SQLAlchemy psycopg2-binary
```

## Próximos Passos e Tópicos Avançados

Este tutorial cobriu o básico. Para aprofundar, considerem explorar:

- Relacionamentos (One-to-Many, Many-to-Many): Como definir e gerenciar relações entre tabelas no SQLAlchemy.
- Migrações de Banco de Dados com Alembic: Uma ferramenta essencial para gerenciar as mudanças no esquema do seu banco de dados de forma controlada.
- Sessões Assíncronas (Asyncio com SQLAlchemy 2.0): Para aplicações de alta performance que usam programação assíncrona.
- Consultas Avançadas: join, group_by, order_by, subqueries, etc.
- Controle de Transações: rollback() para desfazer alterações.
- Raw SQL: Como executar SQL puro através do SQLAlchemy quando o ORM não é suficiente ou você precisa de otimização específica.

O SQLAlchemy é uma ferramenta poderosa e com uma curva de aprendizado inicial. No entanto, o investimento vale a pena pela robustez, flexibilidade e controle que ele oferece sobre suas interações com o banco de dados.

Bom aprendizado e ótimos desenvolvimentos!