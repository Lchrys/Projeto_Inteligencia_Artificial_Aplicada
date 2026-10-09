import pandas as pd
import streamlit as st

from dados import (
    URL_SIDRA_SUBSETORES,
    URL_SIDRA_TRIMESTRAL,
    amostra_sidra,
    data_consulta,
    rotulos_periodos_sidra,
)
from interface import botao_download, configurar_pagina
from nucleo import conferir_somas, participacao_setorial, participacao_subsetores

configurar_pagina("Panorama setorial")

st.title("Panorama setorial")
st.caption(
    "Contas Nacionais Trimestrais (SIDRA, tabela 1846, último trimestre "
    "disponível). Agropecuária, indústria e serviços somam o valor adicionado "
    "a preços básicos; valor adicionado mais impostos líquidos sobre produtos "
    "é o PIB a preços de mercado. A transformação é um subsetor da indústria "
    "(código 90693)."
)

try:
    sidra_trimestral = amostra_sidra(URL_SIDRA_TRIMESTRAL)
    sidra_subsetores = amostra_sidra(URL_SIDRA_SUBSETORES)
    rotulos = rotulos_periodos_sidra()
except Exception as exc:
    sidra_trimestral = pd.DataFrame()
    sidra_subsetores = pd.DataFrame()
    rotulos = {}
    st.error(f"Não foi possível consultar o SIDRA: {exc}")

periodo = ""
if not sidra_trimestral.empty and "D2C" in sidra_trimestral.columns:
    periodo = str(sidra_trimestral["D2C"].iloc[0])
rotulo_periodo = rotulos.get(periodo, periodo)
if rotulo_periodo:
    st.caption(f"Período: {rotulo_periodo} ({periodo})")

participacoes = participacao_setorial(sidra_trimestral, sidra_subsetores)
subsetores = participacao_subsetores(sidra_trimestral, sidra_subsetores)
somas = conferir_somas(sidra_trimestral)
data_hoje = data_consulta()
fonte_sidra = "IBGE, SIDRA, tabela 1846 (Contas Nacionais Trimestrais)"


def _fmt_pct(valor) -> str:
    if valor is None or pd.isna(valor):
        return "—"
    return f"{valor:.1f}%"


def _fmt_diff(valor) -> str:
    if valor is None:
        return "indisponível"
    return f"{valor:.2%}"


aba_tri, aba_sub = st.tabs(["Trimestral", "Subsetores"])

with aba_tri:
    if participacoes.empty:
        st.info("Sem dados setoriais neste trimestre.")
    else:
        colunas = st.columns(4)
        for coluna, linha in zip(colunas, participacoes.to_dict("records")):
            coluna.metric(
                linha["setor"],
                _fmt_pct(linha["pct_pib"]),
                help=f"% do PIB a preços de mercado (código {linha['codigo']})",
            )
        grafico = participacoes.dropna(subset=["pct_pib"]).set_index("setor")[
            ["pct_pib"]
        ]
        if not grafico.empty:
            st.bar_chart(grafico, y="pct_pib")
            st.caption("Participação no PIB a preços de mercado, último trimestre.")

        if somas["ok"]:
            st.success(
                "Conferência das somas: agropecuária + indústria + serviços "
                "fecha com o valor adicionado, e valor adicionado + impostos "
                "fecha com o PIB (tolerância de 0,5% para arredondamento)."
            )
        else:
            st.warning(
                "Conferência das somas: diferença relativa de "
                f"{_fmt_diff(somas['diff_setores_va'])} entre setores e VA, "
                f"e de {_fmt_diff(somas['diff_va_impostos_pib'])} entre "
                "VA + impostos e PIB (tolerância de 0,5%)."
            )

        with st.expander("Tabela SIDRA (trimestral)"):
            st.dataframe(sidra_trimestral, hide_index=True, width="stretch")

        botao_download(
            participacoes,
            "sidra_participacao_setorial.csv",
            "dl_sidra_part",
            "Baixar participações (CSV)",
            fonte=fonte_sidra,
            codigo_serie="90707;90705;90687;90691;90696;90693",
            data_extracao=data_hoje,
        )
        botao_download(
            sidra_trimestral,
            "sidra_trimestral.csv",
            "dl_sidra_tri",
            "Baixar tabela SIDRA (CSV)",
            fonte=fonte_sidra,
            codigo_serie="1846",
            data_extracao=data_hoje,
        )

with aba_sub:
    if subsetores.empty:
        st.info("Sem subsetores da indústria neste trimestre.")
    else:
        colunas = st.columns(len(subsetores))
        for coluna, linha in zip(colunas, subsetores.to_dict("records")):
            coluna.metric(
                linha["setor"],
                _fmt_pct(linha["pct_industria"]),
                help="Participação na indústria total (código 90691).",
            )
        visivel = subsetores.rename(
            columns={
                "pct_industria": "% da indústria",
                "pct_pib": "% do PIB",
            }
        )
        st.dataframe(
            visivel[["setor", "codigo", "valor_milhoes", "% da indústria", "% do PIB"]],
            hide_index=True,
            width="stretch",
        )
        with st.expander("Tabela SIDRA (subsetores)"):
            st.dataframe(sidra_subsetores, hide_index=True, width="stretch")
        botao_download(
            subsetores,
            "sidra_participacao_subsetores.csv",
            "dl_sidra_sub_part",
            "Baixar participações dos subsetores (CSV)",
            fonte=fonte_sidra,
            codigo_serie="90693;90692;90694;90695",
            data_extracao=data_hoje,
        )
        botao_download(
            sidra_subsetores,
            "sidra_subsetores.csv",
            "dl_sidra_sub",
            "Baixar tabela SIDRA (CSV)",
            fonte=fonte_sidra,
            codigo_serie="1846",
            data_extracao=data_hoje,
        )
