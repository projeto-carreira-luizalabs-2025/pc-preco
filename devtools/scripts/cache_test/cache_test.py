import httpx
import time
import asyncio
import json


KEYCLOAK_TOKEN_URL = "http://localhost:8080/realms/marketplace/protocol/openid-connect/token"
KC_CLIENT_ID = "pc-preco"
KC_USERNAME = "vendedor1"
KC_PASSWORD = "senha123"

API_URL = "http://localhost:8000/api/v2/precos/sku003"  # Lembrar que estamnos testando com o SKU sku003
SELLER_ID = "luizalabs"
REDIS_URL = "redis://localhost:6379/0"
CACHE_KEY = f"price:{SELLER_ID}:sku003"


async def get_token():
    async with httpx.AsyncClient() as client:
        data = {
            "client_id": KC_CLIENT_ID,
            "grant_type": "password",
            "username": KC_USERNAME,
            "password": KC_PASSWORD,
            "scope": "openid",
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = await client.post(KEYCLOAK_TOKEN_URL, data=data, headers=headers)
        resp.raise_for_status()
        return resp.json()["access_token"]


async def limpar_cache():
    import redis.asyncio as aioredis

    redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    await redis.delete(CACHE_KEY)
    await redis.aclose()
    print(f"\nCache removido para a chave: {CACHE_KEY}")


async def medir_requisicoes():
    # Limpando cache antes de iniciar os testes
    await limpar_cache()
    token = await get_token()
    headers = {"x-seller-id": SELLER_ID, "Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        # Cache MISS
        start = time.perf_counter()
        response1 = await client.get(API_URL, headers=headers)
        end = time.perf_counter()
        print(f"\n{'='*40}\n")
        print("1ª Requisição (sem cache): {:.4f} segundos".format(end - start))
        print("Resposta:")
        print(json.dumps(response1.json(), indent=2, ensure_ascii=False))

        # Cache HIT
        start = time.perf_counter()
        response2 = await client.get(API_URL, headers=headers)
        end = time.perf_counter()
        print(f"\n{'='*40}\n")
        print("2ª Requisição (com cache): {:.4f} segundos".format(end - start))
        print("Resposta:")
        print(json.dumps(response2.json(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(medir_requisicoes())
