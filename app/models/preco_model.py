from . import PersistableEntity


class Preco(PersistableEntity):
    seller_id: str
    sku: str
    preco_de: int
    preco_por: int
