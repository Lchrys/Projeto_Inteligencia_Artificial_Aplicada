"""Rotas das metas do ODS 9 extraídas do Ipea."""

from fastapi import APIRouter, HTTPException

from Code.api import _paths  # noqa: F401
from Code.api.models import MetaDetalheOut, MetasOut
from Code.api.util import registros
from nucleo import FONTE_ODS9, carregar_ods9

router = APIRouter(prefix="/ods9", tags=["ODS 9"])


@router.get(
    "/metas",
    response_model=MetasOut,
    summary="Lista as metas do ODS 9 extraídas do Ipea",
    description="Lê Data/raw/ods9_metas.csv, gerado pelo scraping com "
    "Beautiful Soup da página ODS 9 do Ipea. A página Contexto ODS 9 "
    "consome esta rota.",
)
def get_ods9_metas() -> dict:
    metas = carregar_ods9()
    return {
        "fonte": FONTE_ODS9,
        "n": int(len(metas)),
        "dados": registros(metas),
    }


@router.get(
    "/metas/{codigo}",
    response_model=MetaDetalheOut,
    summary="Uma meta do ODS 9",
    description="Devolve a redação da ONU, a redação brasileira, justificativa, "
    "conceitos e indicadores da meta pedida (por exemplo 9.2).",
)
def get_ods9_meta(codigo: str) -> dict:
    metas = carregar_ods9()
    if metas.empty:
        raise HTTPException(
            status_code=404, detail="Arquivo ods9_metas.csv não encontrado."
        )
    recorte = metas[metas["meta"].astype(str) == str(codigo)]
    if recorte.empty:
        raise HTTPException(
            status_code=404, detail=f"Meta {codigo} não encontrada."
        )
    return {
        "fonte": FONTE_ODS9,
        "dados": registros(recorte)[0],
    }
