from pydantic import Field

from app.api.common.schemas import ResponseEntity, SchemaType


class PrecoSchema(SchemaType):
    """
    Schema base para a entidade Preco.
    Contém os campos comuns a todas as operações.
    """
    seller_id: str = Field(
        ..., 
        description="Identificador único do seller", 
        example="seller123"
    )
    sku: str = Field(
        ..., 
        description="Código SKU do produto", 
        example="SKU001"
    )
    preco_de: int = Field(
        ..., 
        description="Preço original em centavos (ex: R$ 100,00 = 10000)", 
        example=10000,
        gt=0
    )
    preco_por: int = Field(
        ..., 
        description="Preço promocional em centavos (ex: R$ 85,00 = 8500)", 
        example=8500,
        gt=0
    )


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

    # Herda a configuração do modelo base


class PrecoUpdate(SchemaType):
    """
    Schema para atualização de Precos.
    Permite apenas a atualização do "preco_de" e "preco_por".
    """
    preco_de: int = Field(
        ..., 
        description="Novo preço original em centavos (ex: R$ 120,00 = 12000)", 
        example=12000,
        gt=0
    )
    preco_por: int = Field(
        ..., 
        description="Novo preço promocional em centavos (ex: R$ 95,00 = 9500)", 
        example=9500,
        gt=0
    )
