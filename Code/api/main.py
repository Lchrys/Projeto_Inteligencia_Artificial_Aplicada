"""API local do monitor: consulta e envio de dados oficiais e textuais."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from Code.api import _paths  # noqa: F401
from Code.api.erros import erro, erro_inesperado
from Code.api.models import SaudeOut
from Code.api.routers import ods9, series, texto


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Carrega o modelo de linguagem ao subir a API e o libera ao descer."""
    texto.carregar_na_subida()
    yield
    texto.liberar_na_descida()


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
    lifespan=lifespan,
    # Documenta o 500 em todas as rotas: qualquer uma pode falhar por um motivo imprevisto.
    responses={500: erro("Erro interno, com um código para informar a quem mantém a API.")},
)

# A rede de segurança: o que nenhuma rota tratou vira 500 em JSON, com código (erros.py).
app.add_exception_handler(Exception, erro_inesperado)

app.include_router(series.router)
app.include_router(ods9.router)
app.include_router(texto.router)


@app.get(
    "/saude",
    response_model=SaudeOut,
    summary="Verifica se a API está no ar",
    description="Retorna o estado do serviço. O painel consulta esta rota para "
    "saber se as demais rotas podem ser usadas.",
)
def saude() -> dict:
    return {"status": "ok", "servico": "monitor-desindustrializacao"}
