import pandas as pd
import streamlit as st

from dados import (
    URL_SIDRA_SUBSETORES,
    URL_SIDRA_TRIMESTRAL,
    amostra_sidra,
    data_consulta,
    rotulos_periodos_sidra,
)
from interface import botao_download, configurar_pagina, sobre_os_dados
from nucleo import (
    conferir_somas,
    participacao_setorial,
    participacao_subsetores,
    participacao_transformacao,
    periodos_sidra,
    tabela_sidra_legivel,
)

configurar_pagina("Panorama setorial")

st.title("Panorama setorial")
st.caption(
    "Como se divide o PIB brasileiro nos últimos quatro trimestres, "
    "e quanto da indústria é transformação."
)
sobre_os_dados(
    "IBGE/SIDRA, tabela 1846 (Contas Nacionais Trimestrais), últimos "
    "quatro trimestres (`periodos/-4`). Agropecuária, indústria, serviços "
    "e impostos líquidos somam o PIB a preços de mercado. A transformação "
    "(código 90693) é um subsetor da indústria, não um quarto setor; entra "
    "como 'dos quais'. A trajetória de longo prazo está na Série histórica."
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

janela = periodos_sidra(sidra_trimestral)
if janela["inicio"]:
    rotulo_inicio = rotulos.get(janela["inicio"], janela["rotulo_inicio"])
    rotulo_fim = rotulos.get(janela["fim"], janela["rotulo_fim"])
    if janela["inicio"] == janela["fim"]:
        st.caption(f"Período: {rotulo_fim} ({janela['fim']})")
    else:
        st.caption(
            f"Acumulado de {rotulo_inicio} a {rotulo_fim} "
            f"({janela['inicio']}–{janela['fim']})."
        )

participacoes = participacao_setorial(sidra_trimestral)
transformacao = participacao_transformacao(sidra_trimestral, sidra_subsetores)
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


aba_tri, aba_sub = st.tabs(["Composição do PIB", "Subsetores"])

with aba_tri:
    if participacoes.empty:
        st.info("Sem dados setoriais neste intervalo.")
    else:
        colunas = st.columns(4)
        for coluna, linha in zip(colunas, participacoes.to_dict("records")):
            coluna.metric(
                linha["setor"],
                _fmt_pct(linha["pct_pib"]),
                help=f"% do PIB a preços de mercado (código {linha['codigo']})",
            )
        if transformacao.get("pct_pib") is not None:
            st.metric(
                "Dos quais: transformação",
                _fmt_pct(transformacao["pct_pib"]),
                help=(
                    "Participação da indústria de transformação no PIB "
                    f"(código {transformacao['codigo']}). É subsetor da "
                    "indústria, não um setor à parte."
                ),
            )
        grafico = participacoes.dropna(subset=["pct_pib"]).set_index("setor")[
            ["pct_pib"]
        ]
        if not grafico.empty:
            st.bar_chart(grafico, y="pct_pib")
            st.caption(
                "Participação no PIB a preços de mercado, acumulado dos "
                "últimos quatro trimestres. A transformação não entra no "
                "gráfico para não ser lida como um quarto setor."
            )

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

        with st.expander("Tabela SIDRA (composição)"):
            st.dataframe(
                tabela_sidra_legivel(sidra_trimestral),
                hide_index=True,
                width="stretch",
            )

        botao_download(
            participacoes,
            "sidra_participacao_setorial.csv",
            "dl_sidra_part",
            "Baixar participações (CSV)",
            fonte=fonte_sidra,
            codigo_serie="90707;90705;90687;90691;90696;90706",
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
        st.info("Sem subsetores da indústria neste intervalo.")
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
            st.dataframe(
                tabela_sidra_legivel(sidra_subsetores),
                hide_index=True,
                width="stretch",
            )
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
