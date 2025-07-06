import logging


def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    # Silencia bibliotecas de terceiros
    for lib in ["pika", "sqlalchemy", "alembic", "httpx"]:
        logging.getLogger(lib).setLevel(logging.WARNING)
