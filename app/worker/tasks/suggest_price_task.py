import asyncio
import json
from logging import getLogger

import httpx

from app.integrations.cache.redis_asyncio_adapter import RedisAsyncioAdapter
from app.integrations.queue.rabbitmq_adapter import QueueMessage, RabbitMQConsumer

logger = getLogger(__name__)


class SuggestPriceTask:

    def __init__(self, redis_adapter: RedisAsyncioAdapter, consumer: RabbitMQConsumer, ia_api_url: str, ia_model: str):
        self.redis_adapter = redis_adapter
        self.consumer = consumer
        self._running = False
        self.ia_api_url = ia_api_url
        self.ia_model = ia_model
        self.lock = asyncio.Lock()

    async def close(self):
        async with self.lock:
            self.consumer.close()
            self._running = False
        self.consumer = None

    async def set_running(self, r: bool):
        async with self.lock:
            self._running = r

    async def run(self):
        logger.info("Executando tarefa de geração de sugestão de preço")
        await self.set_running(True)
        while self._running:
            async with self.lock:
                message = self.consumer.consume()
            if message.has_value():
                await self.process(message)
            else:
                # XXX Exportar o tempo para variável
                await asyncio.sleep(1)

    async def process(self, message: QueueMessage):
        sugestao_data = message.value

        price_suggestion = await self.generate_price_suggestion(sugestao_data)

        cache_key = f"suggestion:{sugestao_data['job_id']}"

        await self.redis_adapter.set_json(
            cache_key, {"status": "done", "suggested_price": price_suggestion}, expires_in_seconds=300
        )

        self.consumer.commit_message(message)

    async def generate_price_suggestion(self, data: dict):
        """
        Vamos conversar com a IA, o texto seria bom carregar do banco!
        """

        seller_id = data.get("seller_id")
        sku = data.get("sku")
        history = data.get("history", [])

        # Montando o prompt para a IA
        prompt = (
            f"Você é um especialista em precificação de produtos.\n"
            f"Analise o histórico dos últimos preços de venda ('por') para o produto SKU '{sku}' do seller '{seller_id}'.\n"
            f"Histórico de preços (do mais antigo para o mais recente): {history}\n"
            f"Com base nessa sequência, sugira um novo preço de venda ('por') para maximizar as chances de venda, "
            f"considerando tendências e possíveis promoções. "
            f"Responda apenas com o valor sugerido, sem texto adicional."
        )
        # Payload de envio para IA
        payload = {"model": self.ia_model, "prompt": prompt, "stream": False}

        try:
            logger.info(
                f"Enviando histórico do seller-id {seller_id} e sku {sku} para análise da IA. Modelo: {self.ia_model}",
                extra={"historico": history, "sku": sku, "seller_id": seller_id},
            )
            # XXX O timeout poderia ser configurável.
            async with httpx.AsyncClient(timeout=120) as http_client:
                response = await http_client.post(self.ia_api_url, json=payload)
            # Lança um erro para respostas com código 4xx ou 5xx
            response.raise_for_status()

            # A resposta da API do Ollama com format: "json" já é um JSON
            response_data = response.json()

            ia_response = response_data.get("response", "").strip()

            logger.info(
                f"Análise da IA recebida: {ia_response}",
                extra={"sku": sku, "seller_id": seller_id},
            )

            return ia_response
        except httpx.HTTPError as e:
            logger.error(f"Erro ao chamar a API do Ollama: {e}", exc_info=True)
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar a resposta JSON da IA: {e}")
        except Exception as e:
            logger.error(f"Erro inesperado na função de análise da IA: {e}")
