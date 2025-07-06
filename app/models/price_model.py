from . import SellerSkuIntPersistableEntity


class Price(SellerSkuIntPersistableEntity):
    de: int
    por: int
    alerta_pendente: bool = False
