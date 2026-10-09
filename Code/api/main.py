"""API local do monitor: consulta e envio de dados oficiais e textuais."""

import json
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
SCRIPTS = RAIZ / "Scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from nucleo import (  # noqa: E402
    ANO_QUEBRA_SCN,
    CODIGO_IPEA,
    data_consulta,
    FONTE_IPEADATA,
    FONTE_ODS9,
    FONTE_WB,
    INDICADOR_WB,
    anexar_documento,
    carregar_documentos,
    carregar_ods9,
    carregar_world_bank,
    fatos_resumo,
    filtrar_documentos,
    filtrar_world_bank,
    recortar_serie,
    serie_transformacao,
)

app = FastAPI(
    title="Monitor Brasileiro de Desindustrialização",
    description=(
        "API local (FastAPI) para consultar as séries oficiais do indicador "
        "9.2.1 e os textos do ODS 9, e para receber documentos textuais. "
        "O painel Streamlit consome estas rotas quando a API está no ar "
        "(Início, Série histórica e Contexto ODS 9). Documentação interativa "
        "em /docs."
    ),
    version="0.3.0",
)


class DocumentoIn(BaseModel):
    titulo: str = Field(..., min_length=1, examples=["Nota sobre a meta 9.2"])
    texto: str = Field(..., min_length=1, examples=["Texto do documento."])
    fonte: str = Field(..., min_length=1, examples=["Usuário"])
    data: str = Field(..., min_length=1, examples=["2026-10-09"])
    url: str = Field("", examples=["https://exemplo.org"])
    tipo: str = Field("usuario", examples=["usuario"])


def registros(quadro: pd.DataFrame) -> list:
    if quadro.empty:
        return []
    return json.loads(quadro.to_json(orient="records"))


@app.get(
    "/saude",
    summary="Verifica se a API está no ar",
    description="Retorna o estado do serviço. O painel consulta esta rota para "
    "saber se as demais rotas podem ser usadas.",
)
def saude() -> dict:
    return {"status": "ok", "servico": "monitor-desindustrializacao"}


@app.get(
    "/serie/transformacao",
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
        serie = serie_transformacao()
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


@app.get(
    "/world-bank",
    summary="Recorte do World Development Indicators",
    description=(
        "Lê o CSV exportado do DataBank em Data/raw/world_bank_setorial.csv, "
        "converte para formato longo e filtra por país (código ISO3), "
        "indicador, início e fim. NV.IND.MANF.ZS é o indicador 9.2.1."
    ),
)
def get_world_bank(
    pais: str | None = Query(None, description="Código ISO3, por exemplo BRA"),
    indicador: str | None = Query(
        None, description=f"Código da série, por exemplo {INDICADOR_WB}"
    ),
    inicio: int | None = Query(None, description="Primeiro ano"),
    fim: int | None = Query(None, description="Último ano"),
) -> dict:
    try:
        quadro = carregar_world_bank()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    recorte = filtrar_world_bank(quadro, pais, indicador, inicio, fim)
    return {
        "fonte": FONTE_WB,
        "data_extracao": data_consulta(),
        "pais": pais,
        "indicador": indicador,
        "inicio": inicio,
        "fim": fim,
        "n": int(len(recorte)),
        "dados": registros(recorte),
    }


@app.get(
    "/ods9/metas",
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


@app.get(
    "/ods9/metas/{codigo}",
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


@app.get(
    "/documentos",
    summary="Lista os documentos enviados pelo POST",
    description="Lê Data/processed/documentos.csv. Busca no título, no texto e "
    "na fonte. O limite corta o número de linhas devolvidas. A aba Corpus "
    "da página Contexto ODS 9 consome esta rota.",
)
def get_documentos(
    busca: str | None = Query(None, description="Termo no título, texto ou fonte"),
    limite: int | None = Query(None, ge=1, le=500, description="Máximo de linhas"),
) -> dict:
    recorte = filtrar_documentos(carregar_documentos(), busca, limite)
    return {"n": int(len(recorte)), "dados": registros(recorte)}


@app.get(
    "/fatos/resumo",
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
        return fatos_resumo()
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"Não foi possível calcular o resumo: {exc}"
        ) from exc


@app.post(
    "/documentos",
    summary="Inclui um documento textual no corpus",
    description="Valida título, texto, fonte e data e anexa uma linha a "
    "Data/processed/documentos.csv, com identificador gerado na API. "
    "Esses textos entram na aba Corpus da página Contexto ODS 9 e ficam "
    "disponíveis para Q&A na etapa de LLM.",
)
def post_documento(corpo: DocumentoIn) -> dict:
    linha = anexar_documento(
        titulo=corpo.titulo,
        texto=corpo.texto,
        fonte=corpo.fonte,
        data=corpo.data,
        url=corpo.url or "",
        tipo=corpo.tipo or "usuario",
    )
    return {"mensagem": "Documento gravado.", "dados": linha}
