from ..api.common.schemas.response import ErrorDetail
from ..common.exceptions import BadRequestException, NotFoundException
from ..models import Price
from ..repositories import PriceRepository
from .base import CrudService


class PriceService(CrudService[Price, str]):
    """
    Serviço responsável pelas regras de negócio relacionadas à entidade Preco.
    Fornece métodos para criação, atualização, busca e validação de preços.
    """

    repository: PriceRepository

    def __init__(self, repository: PriceRepository):
        """
        Inicializa o serviço de preços com o repositório fornecido.

        :param repository: Instância de PriceRepository para acesso aos dados.
        """
        super().__init__(repository)

    async def get_by_seller_id_and_sku(self, seller_id: str, sku: str) -> Price:
        """
        Busca um preço pelo seller_id e sku.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :return: Instância de Preco encontrada.
        :raises NotFoundException: Se não encontrar o preço.
        """
        price_dict = await self.repository.find_by_seller_id_and_sku(seller_id, sku)

        self._raise_not_found(seller_id, sku, price_dict is None)

        # Garantimos que price_dict não é None neste ponto, podemos usá-lo com segurança
        return Price.model_validate(price_dict)

    async def create_price(self, price_create: Price) -> Price:
        """
        Cria uma nova precificação após validações de unicidade e valores positivos.

        :param price_create: Objeto contendo os dados para criação do preço.
        :return: Instância de Preco criada.
        :raises BadRequestException: Se já existir preço para o produto ou valores inválidos.
        """
        await self._validate_non_existent_price(price_create.seller_id, price_create.sku)
        self._validate_positive_prices(price_create)
        # Converte PrecoCreate para Preco, gerando o id automaticamente
        price = Price(**price_create.model_dump())
        return await self.create(price)

    async def update_price(self, seller_id: str, sku: str, price_update: Price) -> Price:
        """
        Atualiza uma precificação existente com novos valores.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :param price_update: Objeto contendo os novos dados do preço.
        :return: Instância de Preco atualizada.
        :raises NotFoundException: Se não encontrar o preço.
        :raises BadRequestException: Se valores inválidos forem informados.
        """
        price_found = await self.repository.exists_by_seller_id_and_sku(seller_id, sku)

        self._raise_not_found(seller_id, sku, not price_found)
        self._validate_positive_prices(price_update)
        updated = await self.repository.update_by_seller_id_and_sku(seller_id, sku, price_update)
        return Price(**updated)

    async def delete_by_seller_id_and_sku(self, seller_id: str, sku: str):
        """
        Remove um preço baseado em seller_id e sku.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :raises NotFoundException: Se o preço não for encontrado.
        """
        price_found = await self.repository.find_by_seller_id_and_sku(seller_id, sku)
        self._raise_not_found(seller_id, sku, price_found is None)
        await self.repository.delete_by_seller_id_and_sku(seller_id, sku)

    def _validate_positive_prices(self, price):
        """
        Valida se os valores de preco_de e preco_por são positivos.

        :param price: Objeto de preço a ser validado.
        """
        self._validate_positives(price.preco_de, "preco_de")
        self._validate_positives(price.preco_por, "preco_por")

    def _validate_positives(self, value, field: str):
        """
        Valida se o valor fornecido é maior que zero.

        :param field: Nome do campo que está sendo validado.
        :param value: Valor númerico a ser validado (opcional).
        :raises BadRequestException: Se algum valor for menor ou igual a zero.
        """
        if value <= 0:
            self._raise_bad_request(f"{field} deve ser maior que zero.", field, value)

    async def _validate_non_existent_price(self, seller_id: str, sku: str):
        """
        Verifica se já existe um preço cadastrado para o seller_id e sku informados.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :raises BadRequestException: Se já existir preço cadastrado.
        """
        price_found = await self.repository.exists_by_seller_id_and_sku(seller_id, sku)
        if price_found:
            self._raise_bad_request("Preço para produto já cadastrado.", "sku")

    def _raise_not_found(self, seller_id: str, sku: str, condition: bool = True):
        """
        Lança exceção de NotFoundException com detalhes do erro.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :raises NotFoundException: Sempre.
        """
        if condition:
            raise NotFoundException(
                details=[
                    ErrorDetail(
                        message="Preço para produto não encontrado.",
                        location="path",
                        slug="preco_nao_encontrado",
                        field="sku",
                        ctx={"seller_id": seller_id, "sku": sku},
                    )
                ]
            )

    def _raise_bad_request(self, message: str, field: str, value=None):
        """
        Lança exceção de BadRequestException com detalhes do erro.

        :param message: Mensagem descritiva do erro.
        :param field: Campo relacionado ao erro.
        :param value: Valor que causou o erro (opcional).
        :raises BadRequestException: Sempre.
        """
        raise BadRequestException(
            details=[
                ErrorDetail(
                    message=message,
                    location="body",
                    slug="preco_invalido",
                    field=field,
                    ctx={"value": value} if value is not None else {},
                )
            ]
        )
