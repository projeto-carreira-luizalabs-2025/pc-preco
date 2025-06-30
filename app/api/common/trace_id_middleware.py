import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


# --- Middleware para X-Trace-ID ---
class TraceIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # 1. Tenta pegar o X-Trace-ID do cabeçalho da requisição
        trace_id = request.headers.get("x-trace-id")

        if not trace_id:
            # 2. Se não existir, cria um novo UUID4
            trace_id = str(uuid.uuid4())

        # 3. Adiciona o X-Trace-ID ao objeto Request.state
        #    Isso torna o trace_id acessível nas rotas e dependências
        request.state.trace_id = trace_id

        # 4. Processa a requisição e obtém a resposta da rota
        response = await call_next(request)

        # 5. Adiciona o X-Trace-ID no cabeçalho da resposta
        response.headers["X-Trace-ID"] = trace_id

        return response
