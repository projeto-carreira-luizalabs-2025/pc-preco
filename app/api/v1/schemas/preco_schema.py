from app.api.common.schemas import ResponseEntity, SchemaType


class PrecoSchema(SchemaType):
    """
    Schema base para a entidade Preco.
    Contém os campos comuns a todas as operações.
    """
    seller_id: str
    sku: str
    preco_de: int
    preco_por: int


class PrecoResponse(PrecoSchema, ResponseEntity):
    """
    Schema para resposta de operações com Preco.
    Adiciona os campos de auditoria e identificação.
    """


class PrecoCreate(PrecoSchema):
    """
    Schema para criação de Precos.
    Utiliza todos os campos do schema base.
    """


class PrecoUpdate(SchemaType):
    """
    Schema para atualização de Precos.
    Permite apenas a atualização do "preco_de" e "preco_por".
    """
    preco_de: int
    preco_por: int
