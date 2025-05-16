from . import PersistableEntity


class Price(PersistableEntity):
    seller_id: str
    sku: str
    preco_de: int
    preco_por: int
