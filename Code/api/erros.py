"""Os erros da API: o formato, a documentação e a rede de segurança (TP4, Etapa 4).

Todo erro que a própria API levanta tem o mesmo corpo: {"detail": "uma frase"}.
O erro 422 (entrada fora do contrato) continua o do FastAPI: {"detail": [ {loc, msg, type}, ... ]}.

Três peças:
  · Erro: o formato do corpo de erro. Serve para o /docs mostrar os erros de cada rota.
  · erro(): atalho para o `responses=` de cada rota, por exemplo {502: erro("…")}.
  · erro_inesperado(): a rede de segurança. Qualquer exceção que nenhuma rota tratou
    vira um 500 em JSON, com um código de rastreio. Ao cliente: uma frase e o código,
    nunca o traceback (ele pode conter caminhos de arquivo e pedaços de dado). Ao log: o
    mesmo código e o traceback completo, para quem mantém a API.
"""

import logging
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# O mesmo logger que o uvicorn usa para os erros: a linha aparece no terminal da API.
log = logging.getLogger("uvicorn.error")


class Erro(BaseModel):
    """O corpo de todo erro levantado pela API."""

    detail: str = Field(description="O que aconteceu e, quando houver, o que fazer.")


def erro(descricao: str) -> dict:
    """Uma entrada do `responses=` de uma rota: o /docs passa a listar o erro, com o formato."""
    return {"model": Erro, "description": descricao}


def erro_inesperado(request: Request, exc: Exception) -> JSONResponse:
    codigo = uuid.uuid4().hex[:8]
    log.error(
        "Erro inesperado [%s] em %s %s — %s: %s",
        codigo,
        request.method,
        request.url.path,
        type(exc).__name__,
        exc,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Erro interno na API (código {codigo}). Avise quem mantém a API e informe o código."
        },
    )
