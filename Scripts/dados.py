import pandas as pd
import streamlit as st
from wordcloud import WordCloud

from nucleo import (
    ANO_QUEBRA_SCN,
    ARQ_ODS9_CSV,
    ARQ_ODS9_TXT,
    ARQ_WB_CSV,
    CODIGO_IPEA,
    COLUNAS_DATABANK,
    COLUNAS_DOCUMENTOS,
    data_consulta,
    fatos_resumo as _fatos_resumo,
    FONTE_IPEADATA,
    FONTE_ODS9,
    FONTE_WB,
    HEADERS,
    INDICADOR_WB,
    INDICADORES_WB,
    RAIZ,
    URL_SIDRA_SUBSETORES,
    URL_SIDRA_TRIMESTRAL,
    achatar_agregados,
    achatar_databank,
    amostra_sidra as _amostra_sidra,
    carregar_corpus_ods9 as _carregar_corpus_ods9,
    carregar_ods9 as _carregar_ods9,
    carregar_world_bank as _carregar_world_bank,
    consultar_ipeadata,
    data_extracao_wb as _data_extracao_wb,
    eixo_ano,
    frequencia_palavras as _frequencia_palavras,
    normalizar_serie_transformacao,
    rotulos_periodos_sidra as _rotulos_periodos_sidra,
    tokens_corpus,
    transformar_pivot,
)

__all__ = [
    "ANO_QUEBRA_SCN",
    "ARQ_ODS9_CSV",
    "ARQ_ODS9_TXT",
    "ARQ_WB_CSV",
    "CODIGO_IPEA",
    "COLUNAS_DATABANK",
    "COLUNAS_DOCUMENTOS",
    "data_consulta",
    "fatos_resumo",
    "FONTE_IPEADATA",
    "FONTE_ODS9",
    "FONTE_WB",
    "HEADERS",
    "INDICADOR_WB",
    "INDICADORES_WB",
    "RAIZ",
    "URL_SIDRA_SUBSETORES",
    "URL_SIDRA_TRIMESTRAL",
    "achatar_agregados",
    "achatar_databank",
    "amostra_ipeadata",
    "amostra_sidra",
    "carregar_corpus_ods9",
    "carregar_ods9",
    "carregar_world_bank",
    "data_extracao_wb",
    "eixo_ano",
    "frequencia_palavras",
    "imagem_nuvem",
    "rotulos_periodos_sidra",
    "serie_transformacao",
    "tokens_corpus",
    "transformar_pivot",
]


@st.cache_data(ttl=3600, show_spinner="Consultando Ipeadata...")
def amostra_ipeadata(codigo: str) -> pd.DataFrame:
    return consultar_ipeadata(codigo)


@st.cache_data(ttl=3600, show_spinner="Consultando SIDRA...")
def rotulos_periodos_sidra(agregado: str = "1846") -> dict:
    return _rotulos_periodos_sidra(agregado)


@st.cache_data(ttl=3600, show_spinner="Consultando SIDRA...")
def amostra_sidra(url: str) -> pd.DataFrame:
    return _amostra_sidra(url)


@st.cache_data
def data_extracao_wb() -> str:
    return _data_extracao_wb()


@st.cache_data
def carregar_ods9() -> pd.DataFrame:
    return _carregar_ods9()


@st.cache_data
def carregar_corpus_ods9() -> str:
    return _carregar_corpus_ods9()


@st.cache_data
def carregar_world_bank() -> pd.DataFrame:
    return _carregar_world_bank()


@st.cache_data
def frequencia_palavras(
    texto: str, n: int = 15, corpus_completo: bool = False
) -> pd.Series:
    return _frequencia_palavras(texto, n=n, corpus_completo=corpus_completo)


def serie_transformacao() -> pd.DataFrame:
    return normalizar_serie_transformacao(amostra_ipeadata(CODIGO_IPEA))


@st.cache_data(ttl=3600, show_spinner="Calculando indicadores...")
def fatos_resumo() -> dict:
    return _fatos_resumo(serie_transformacao())


@st.cache_data
def imagem_nuvem(texto: str, corpus_completo: bool = False):
    palavras = " ".join(tokens_corpus(texto, corpus_completo))
    if not palavras:
        return None
    cores = ("#1b4f72", "#922b21", "#1a5276", "#6c3483", "#196f3d", "#b03a2e")

    def cor_escura(word, font_size, position, orientation, random_state=None, **kwargs):
        if random_state is None:
            return cores[0]
        return cores[int(random_state.randint(0, len(cores) - 1))]

    nuvem = WordCloud(
        width=800,
        height=360,
        background_color="white",
        color_func=cor_escura,
    ).generate(palavras)
    return nuvem.to_array()
