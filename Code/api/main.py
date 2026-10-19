"""API local do monitor: consulta e envio de dados oficiais e textuais."""

from fastapi import FastAPI

from Code.api import _paths  # noqa: F401
from Code.api.models import SaudeOut
from Code.api.routers import ods9, series

app = FastAPI(
    title="Monitor Brasileiro de Desindustrialização",
    description=(
        "API local (FastAPI) para consultar as séries oficiais do indicador "
        "9.2.1 e os textos do ODS 9, e para receber o CSV do DataBank. "
        "O painel Streamlit consome estas rotas quando a API está no ar "
        "(Início, Série histórica, Comparação internacional e Contexto ODS 9). "
        "Documentação interativa em /docs. Modelos de resposta em "
        "Code/api/models.py."
    ),
    version="0.4.0",
)

app.include_router(series.router)
app.include_router(ods9.router)


@app.get(
    "/saude",
    response_model=SaudeOut,
    summary="Verifica se a API está no ar",
    description="Retorna o estado do serviço. O painel consulta esta rota para "
    "saber se as demais rotas podem ser usadas.",
)
def saude() -> dict:
    return {"status": "ok", "servico": "monitor-desindustrializacao"}
