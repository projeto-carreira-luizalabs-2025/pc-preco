from contextlib import asynccontextmanager
from typing import AsyncIterator

from pydantic import PostgresDsn

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


class SQLAlchemyClient:
    def __init__(self, db_url: PostgresDsn):
        self.db_url = db_url
        self.engine = create_async_engine(str(db_url))
        self.session_maker = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    def close(self):
        """
        Fecha a conexão com o banco de dados.
        """
        try:
            self.session_maker.close_all()
            self.engine.dispose()
        finally:
            self.engine = None

    @asynccontextmanager
    async def make_session(self) -> AsyncIterator[AsyncSession]:
        """
        Cria um contexto assíncrono para gerenciar a sessão do banco de dados.
        :return: AsyncSession
        """
        async with self.session_maker() as session:
            yield session

    @staticmethod
    def init_select(base_class) -> select:
        """
        Inicializa uma consulta SELECT para a tabela de preços.
        :param base_class: Classe base do modelo de dados.
        :return: Consulta SELECT configurada.
        """
        s = select(base_class)
        return s

    @staticmethod
    def init_delete(base_class) -> delete:
        """
        Inicializa uma consulta DELETE para a tabela de preços.
        :param base_class: Classe base do modelo de dados.
        :return: Consulta DELETE configurada.
        """
        d = delete(base_class)
        return d

    @staticmethod
    def to_dict(base) -> dict | None:
        """
        Converte um objeto base em um dicionário.
        :param base: Objeto a ser convertido.
        :return: Dicionário representando o objeto ou None se o objeto for None.
        """
        if base is None:
            return None
        d = base.__dict__
        d.pop("_sa_instance_state", None)
        return d

    @staticmethod
    def get_pk_fields(base_class) -> list[str]:
        """
        Obtém os campos de chave primária de uma classe base.
        :param base_class: Classe base do modelo de dados.
        :return: Lista de nomes dos campos de chave primária.
        """
        pk_fields = [column.name for column in base_class.__table__.columns if column.primary_key]
        return pk_fields
