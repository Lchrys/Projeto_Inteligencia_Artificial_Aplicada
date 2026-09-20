import pandas as pd
import streamlit as st

from dados import ANO_QUEBRA_SCN


def configurar_pagina(titulo: str) -> None:
    st.set_page_config(
        page_title=titulo,
        page_icon=":bar_chart:",
        layout="centered",
    )
    st.markdown(
        """
        <style>
          .block-container { max-width: 860px; padding-top: 2rem; }
          h1 { font-size: 1.85rem; line-height: 1.25; margin-bottom: 0.25rem; }
          h3 { margin-top: 1.6rem; margin-bottom: 0.6rem; }
          div[data-testid="stLinkButton"] { width: 100%; }
          div[data-testid="stLinkButton"] a {
            width: 100%;
            min-height: 2.75rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-align: center;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.caption(
        "Participação da indústria de transformação no PIB "
        "(ODS 9, indicador 9.2.1)"
    )


def aviso_quebra(inicio: int, fim: int) -> None:
    if inicio < ANO_QUEBRA_SCN <= fim:
        st.warning(
            "O período escolhido atravessa "
            f"{ANO_QUEBRA_SCN}, ano em que as Contas Nacionais "
            "brasileiras mudaram de referência. Parte da queda da "
            "transformação nesse intervalo é revisão metodológica, "
            "não desindustrialização. Para comparar níveis, use "
            f"{ANO_QUEBRA_SCN} em diante."
        )


def metrica_completude(serie: pd.Series) -> None:
    if serie.empty:
        return
    valores = pd.to_numeric(serie, errors="coerce")
    st.metric("Completude do recorte", f"{1 - valores.isna().mean():.0%}")


def botao_download(
    df: pd.DataFrame,
    nome: str,
    chave: str,
    rotulo: str = "Baixar esta tabela (CSV)",
    fonte: str = "",
    codigo_serie: str = "",
    data_extracao: str = "",
) -> None:
    if df.empty:
        return
    saida = df.copy()
    if fonte:
        saida["fonte"] = fonte
    if codigo_serie:
        saida["codigo_serie"] = codigo_serie
    if data_extracao:
        saida["data_extracao"] = data_extracao
    st.download_button(
        rotulo,
        saida.to_csv(index=False).encode("utf-8"),
        file_name=nome,
        mime="text/csv",
        key=chave,
    )
