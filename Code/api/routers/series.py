"""Rotas das séries oficiais e do resumo de fatos."""

import time
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from Code.api import _paths  # noqa: F401
from Code.api.models import FatosOut, SerieOut, WorldBankEnvioOut, WorldBankOut
from Code.api.util import registros
from nucleo import (
    ANO_QUEBRA_SCN,
    CODIGO_IPEA,
    data_consulta,
    FONTE_IPEADATA,
    FONTE_WB,
    INDICADOR_WB,
    carregar_envio_wb,
    fatos_resumo,
    filtrar_world_bank,
    gravar_envio_wb,
    ler_databank,
    recortar_serie,
    serie_transformacao,
)

router = APIRouter(tags=["Séries"])

TTL_SERIE = 3600
_cache_serie: dict = {"quando": 0.0, "serie": None}


def serie_com_cache():
    agora = time.monotonic()
    if (
        _cache_serie["serie"] is not None
        and agora - _cache_serie["quando"] < TTL_SERIE
    ):
        return _cache_serie["serie"]
    serie = serie_transformacao()
    _cache_serie["quando"] = agora
    _cache_serie["serie"] = serie
    return serie


def limpar_cache_serie() -> None:
    _cache_serie["quando"] = 0.0
    _cache_serie["serie"] = None


@router.get(
    "/serie/transformacao",
    response_model=SerieOut,
    summary="Série da indústria de transformação no PIB",
    description=(
        "Consulta a série SCN10_VAITY10 no Ipeadata (indicador 9.2.1 da ONU, "
        "participação da indústria de transformação no PIB a preços "
        "correntes). Os parâmetros inicio e fim recortam os anos. Cada ponto "
        "traz fonte, código da série e data de extração. A página Série "
        "histórica e o gráfico da Início consomem esta rota."
    ),
)
def get_serie_transformacao(
    inicio: int | None = Query(None, description="Primeiro ano do recorte"),
    fim: int | None = Query(None, description="Último ano do recorte"),
) -> dict:
    try:
        serie = serie_com_cache()
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"Falha no Ipeadata: {exc}"
        ) from exc
    recorte = recortar_serie(serie, inicio, fim)
    return {
        "fonte": FONTE_IPEADATA,
        "codigo_serie": CODIGO_IPEA,
        "data_extracao": data_consulta(),
        "inicio": inicio,
        "fim": fim,
        "n": int(len(recorte)),
        "dados": registros(recorte),
    }


@router.post(
    "/world-bank",
    response_model=WorldBankEnvioOut,
    status_code=201,
    summary="Recebe um CSV do DataBank",
    description=(
        "Valida o export do DataBank enviado pelo usuário, converte para "
        "formato longo e grava em Data/processed/world_bank_envios/{id}.csv. "
        "Devolve um identificador para consulta em GET /world-bank/{id}. "
        "A página Comparação internacional consome esta rota. Arquivo "
        "fora do formato devolve 400."
    ),
)
async def post_world_bank(
    arquivo: UploadFile = File(..., description="CSV exportado do DataBank"),
) -> dict:
    conteudo = await arquivo.read()
    try:
        quadro = ler_databank(conteudo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if quadro.empty:
        raise HTTPException(
            status_code=400,
            detail="O arquivo não tem observações do DataBank.",
        )
    envio_id = gravar_envio_wb(quadro)
    anos = quadro["date"].dropna() if "date" in quadro.columns else None
    return {
        "id": envio_id,
        "n": int(len(quadro)),
        "paises": sorted(
            quadro["country.id"].dropna().astype(str).unique().tolist()
        )
        if "country.id" in quadro.columns
        else [],
        "indicadores": sorted(
            quadro["indicator.id"].dropna().astype(str).unique().tolist()
        )
        if "indicator.id" in quadro.columns
        else [],
        "ano_inicio": int(anos.min()) if anos is not None and not anos.empty else None,
        "ano_fim": int(anos.max()) if anos is not None and not anos.empty else None,
    }


@router.get(
    "/world-bank/{envio_id}",
    response_model=WorldBankOut,
    summary="Consulta um CSV do DataBank já enviado",
    description=(
        "Lê o envio gravado pelo POST /world-bank e filtra por país "
        "(código ISO3), indicador, início e fim. NV.IND.MANF.ZS é o "
        "indicador 9.2.1. A Comparação internacional consome esta rota "
        "depois do upload. Envio inexistente devolve 404."
    ),
)
def get_world_bank(
    envio_id: UUID,
    pais: str | None = Query(None, description="Código ISO3, por exemplo BRA"),
    indicador: str | None = Query(
        None, description=f"Código da série, por exemplo {INDICADOR_WB}"
    ),
    inicio: int | None = Query(None, description="Primeiro ano"),
    fim: int | None = Query(None, description="Último ano"),
) -> dict:
    quadro = carregar_envio_wb(str(envio_id))
    if quadro is None:
        raise HTTPException(status_code=404, detail="Envio não encontrado.")
    recorte = filtrar_world_bank(quadro, pais, indicador, inicio, fim)
    return {
        "id": str(envio_id),
        "fonte": FONTE_WB,
        "data_extracao": data_consulta(),
        "pais": pais,
        "indicador": indicador,
        "inicio": inicio,
        "fim": fim,
        "n": int(len(recorte)),
        "dados": registros(recorte),
    }


@router.get(
    "/fatos/resumo",
    response_model=FatosOut,
    summary="Indicadores calculados para geração de texto",
    description=(
        "Devolve último valor, variação desde 1995 e máximo da série do "
        "Ipeadata, e a posição do Brasil entre as economias do CSV de exemplo "
        f"do DataBank no indicador {INDICADOR_WB} — não um ranking mundial. "
        "O campo ranking traz universo, paises_no_arquivo, "
        "paises_com_valor_no_ano e nota. Os números são calculados pelo "
        "código; um LLM na etapa seguinte só deve redigir a partir deste "
        "JSON, sem inventar valores. A página Início consome esta rota. "
        f"Níveis comparáveis a partir de {ANO_QUEBRA_SCN}."
    ),
)
def get_fatos_resumo() -> dict:
    try:
        return fatos_resumo(serie_com_cache())
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"Não foi possível calcular o resumo: {exc}"
        ) from exc
