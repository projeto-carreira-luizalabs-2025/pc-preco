from . import PersistableEntity


class Price(PersistableEntity):
    seller_id: str
    sku: str
    de: int
    por: int
