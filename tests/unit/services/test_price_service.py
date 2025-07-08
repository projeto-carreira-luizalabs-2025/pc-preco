from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.exceptions import BadRequestException, NotFoundException
from app.models import Price
from app.repositories import PriceRepository
from app.services import PriceService
from app.services.price_history_service import PriceHistoryService
from app.repositories.price_history_repository import PriceHistoryRepository
from app.integrations.cache.redis_asyncio_adapter import RedisAsyncioAdapter
from app.integrations.queue.rabbitmq_adapter import RabbitMQProducer


class TestPriceService:
    @pytest.fixture
    def repository_mock(self):
        """Cria um mock do repositório para os testes."""
        repository = AsyncMock(spec=PriceRepository)

        # Mock para create
        async def create(entity):
            return entity

        # Mock para find_by_seller_id_and_sku
        async def find_by_seller_id_and_sku(seller_id, sku):
            if seller_id == "1" and sku == "A":
                return Price(
                    id=1,
                    seller_id="1",
                    sku="A",
                    de=100,
                    por=90,
                    alerta_pendente=False,
                )
            return None

        # Mock para update_by_seller_id_and_sku
        async def update_by_seller_id_and_sku(seller_id, sku, price_update):
            if seller_id == "1" and sku == "A":
                return Price(
                    id=1,
                    seller_id=seller_id,
                    sku=sku,
                    de=price_update.de,
                    por=price_update.por,
                    alerta_pendente=False,
                )
            raise ValueError(f"Preço não encontrado para seller_id={seller_id}, sku={sku}")

        # Mock para delete_by_seller_id_and_sku
        async def delete_by_seller_id_and_sku(seller_id, sku):
            return None

        # Patch dos métodos da classe pai
        repository.create.side_effect = create
        repository.find_by_seller_id_and_sku.side_effect = find_by_seller_id_and_sku
        repository.update_by_seller_id_and_sku.side_effect = update_by_seller_id_and_sku
        repository.delete_by_seller_id_and_sku.side_effect = delete_by_seller_id_and_sku

        return repository

    @pytest.fixture
    def service(self, repository_mock):
        """Cria o serviço com todos os mocks necessários."""
        price_history_repo = AsyncMock(spec=PriceHistoryRepository)
        price_history_service = AsyncMock(spec=PriceHistoryService)
        redis_adapter = AsyncMock(spec=RedisAsyncioAdapter)
        alert_queue_producer = MagicMock(spec=RabbitMQProducer)
        suggestion_queue_producer = MagicMock(spec=RabbitMQProducer)
        return PriceService(
            repository=repository_mock,
            price_history_repo=price_history_repo,
            price_history_service=price_history_service,
            redis_adapter=redis_adapter,
            alert_queue_producer=alert_queue_producer,
            suggestion_queue_producer=suggestion_queue_producer,
        )

    @pytest.mark.asyncio
    async def test_get_by_seller_id_and_sku_found(self, service, repository_mock):
        """Deve retornar o preço quando seller_id e sku existem."""
        service.redis_adapter.get_json.return_value = None

        price = await service.get_by_seller_id_and_sku("1", "A")

        assert price is not None
        assert price.seller_id == "1"
        assert price.sku == "A"
        assert price.de == 100
        assert price.por == 90

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "A")

    @pytest.mark.asyncio
    async def test_get_by_seller_id_and_sku_not_found(self, service, repository_mock):
        """Deve lançar NotFoundException quando não encontrar o preço."""
        service.redis_adapter.get_json.return_value = None

        with pytest.raises(NotFoundException):
            await service.get_by_seller_id_and_sku("1", "Z")

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "Z")

    @pytest.mark.asyncio
    async def test_create_price_success(self, service, repository_mock):
        price_create = Price(seller_id="2", sku="B", de=200, por=180)
        created_price = await service.create(price_create)
        assert created_price is not None
        assert created_price.seller_id == "2"
        assert created_price.sku == "B"
        assert created_price.de == 200
        assert created_price.por == 180
        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("2", "B")
        repository_mock.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_price_already_exists(self, service, repository_mock):
        price_create = Price(seller_id="1", sku="A", de=100, por=90)
        with pytest.raises(BadRequestException):
            await service.create(price_create)
        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "A")
        repository_mock.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_price_invalid_price(self, service, repository_mock):
        price_create = Price(seller_id="2", sku="B", de=-100, por=90)
        with pytest.raises(BadRequestException) as excinfo:
            await service.create(price_create)
        assert any("de" in str(detail.message) for detail in excinfo.value.details)
        repository_mock.create.assert_not_called()
        price_create = Price(seller_id="2", sku="B", de=100, por=0)
        with pytest.raises(BadRequestException) as excinfo:
            await service.create(price_create)
        assert any("por" in str(detail.message) for detail in excinfo.value.details)
        repository_mock.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_price_success(self, service, repository_mock):
        price_update = Price(seller_id="1", sku="A", de=150, por=120)

        updated_price = await service.update('1', 'A', price_update)
        assert updated_price is not None
        assert updated_price.seller_id == "1"
        assert updated_price.sku == "A"
        assert updated_price.de == 150
        assert updated_price.por == 120
        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "A")
        repository_mock.update_by_seller_id_and_sku.assert_called_once_with("1", "A", price_update)

    @pytest.mark.asyncio
    async def test_update_price_not_found(self, service, repository_mock):
        repository_mock.find_by_seller_id_and_sku.return_value = False
        price_update = Price(seller_id="1", sku="Z", de=150, por=120)
        with pytest.raises(NotFoundException):
            await service.update('1', 'Z', price_update)
        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "Z")
        repository_mock.update_by_seller_id_and_sku.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_price_invalid_price(self, service, repository_mock):
        price_update = Price(seller_id="1", sku="A", de=-150, por=120)

        with pytest.raises(BadRequestException) as excinfo:
            await service.update('1', 'A', price_update)
        assert any("de" in str(detail.message) for detail in excinfo.value.details)
        repository_mock.update_by_seller_id_and_sku.assert_not_called()
        price_update = Price(seller_id="1", sku="A", de=150, por=0)
        with pytest.raises(BadRequestException) as excinfo:
            await service.update('1', 'A', price_update)
        assert any("por" in str(detail.message) for detail in excinfo.value.details)
        repository_mock.update_by_seller_id_and_sku.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku_success(self, service, repository_mock):
        await service.delete("1", "A")
        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "A")
        repository_mock.delete_by_seller_id_and_sku.assert_called_once_with("1", "A")

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku_not_found(self, service, repository_mock):
        repository_mock.find_by_seller_id_and_sku.return_value = None
        with pytest.raises(NotFoundException):
            await service.delete("1", "Z")
        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "Z")
        repository_mock.delete_by_seller_id_and_sku.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_price_limite_superior_valores(self, service, repository_mock):
        price_create = Price(seller_id="3", sku="C", de=2**31 - 1, por=2**31 - 1)
        repository_mock.find_by_seller_id_and_sku.return_value = False
        created_price = await service.create(price_create)
        assert created_price is not None
        assert created_price.de == 2**31 - 1
        assert created_price.por == 2**31 - 1
        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("3", "C")
        repository_mock.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_price_limite_superior_valores(self, service, repository_mock):
        price_update = Price(seller_id="1", sku="A", de=2**31 - 1, por=2**31 - 1)
        repository_mock.find_by_seller_id_and_sku.return_value = True
        repository_mock.update_by_seller_id_and_sku.return_value = Price(
            id=2,
            seller_id="1",
            sku="A",
            de=2**31 - 1,
            por=2**31 - 1,
            alerta_pendente=False,
        )

        updated_price = await service.update('1', 'A', price_update)
        assert updated_price is not None
        assert updated_price.de == 2**31 - 1
        assert updated_price.por == 2**31 - 1
        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "A")
        repository_mock.update_by_seller_id_and_sku.assert_called_once_with("1", "A", price_update)

    @pytest.mark.asyncio
    async def test_find_price_in_cache_hit(self, service):
        cached_price = {"seller_id": "1", "sku": "A", "de": 100, "por": 90, "alerta_pendente": False}
        service.redis_adapter.get_json.return_value = cached_price
        result = await service.find_price_in_cache("1", "A", "price:1:A")
        assert result.seller_id == "1"
        assert result.sku == "A"

    @pytest.mark.asyncio
    async def test_find_price_in_cache_miss(self, service):
        service.redis_adapter.get_json.return_value = None
        result = await service.find_price_in_cache("1", "A", "price:1:A")
        assert result is None

    def test_raise_not_found(self):
        from app.services.price_service import PriceService

        with pytest.raises(NotFoundException):
            PriceService._raise_not_found("1", "A", True)

    def test_raise_bad_request(self):
        from app.services.price_service import PriceService

        svc = PriceService(
            repository=AsyncMock(),
            price_history_repo=AsyncMock(),
            price_history_service=AsyncMock(),
            redis_adapter=AsyncMock(),
            alert_queue_producer=MagicMock(),
            suggestion_queue_producer=MagicMock(),
        )
        with pytest.raises(BadRequestException):
            svc._raise_bad_request("erro", "field", "value")

    def test_verify_pending_alert_raises(self, service):
        price = Price(seller_id="1", sku="A", de=100, por=90, alerta_pendente=True)
        with pytest.raises(BadRequestException):
            service._verify_pending_alert(price)

    @pytest.mark.asyncio
    async def test_detects_variation_triggers_alert(self, service):
        # Deve retornar True e criar task se variação > 50%
        entity = Price(seller_id="1", sku="A", de=100, por=200, alerta_pendente=False)
        result = service._detects_variation(100, entity)
        assert result is True

    @pytest.mark.asyncio
    async def test_detects_variation_no_alert(self, service):
        entity = Price(seller_id="1", sku="A", de=100, por=120, alerta_pendente=False)
        result = service._detects_variation(100, entity)
        assert result is False

    @pytest.mark.asyncio
    async def test_request_price_suggestion(self, service):
        # Simula histórico suficiente
        service.price_history_service.get_last_n_prices.return_value = [
            Price(seller_id="1", sku="A", de=100, por=90),
            Price(seller_id="1", sku="A", de=100, por=100),
            Price(seller_id="1", sku="A", de=100, por=110),
            Price(seller_id="1", sku="A", de=100, por=120),
            Price(seller_id="1", sku="A", de=100, por=130),
        ]
        resp = await service.request_price_suggestion("1", "A")
        assert resp.status == "pending"
        assert hasattr(resp, "job_id")

    @pytest.mark.asyncio
    async def test_request_price_suggestion_not_found(self, service):
        service.price_history_service.get_last_n_prices.return_value = []
        from app.services.price_service import PriceNotFoundException

        with pytest.raises(PriceNotFoundException):
            await service.request_price_suggestion("1", "A")

    @pytest.mark.asyncio
    async def test_get_price_suggestion_success(self, service):
        service.redis_adapter.get_json.return_value = {"status": "pending", "suggested_price": None}
        resp = await service.get_price_suggestion("fake-job-id")
        assert resp.status == "pending"
        assert resp.suggested_price is None

    @pytest.mark.asyncio
    async def test_get_price_suggestion_not_found(self, service):
        service.redis_adapter.get_json.return_value = None
        with pytest.raises(BadRequestException):
            await service.get_price_suggestion("fake-job-id")
