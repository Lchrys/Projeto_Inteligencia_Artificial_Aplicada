import pandas as pd
import streamlit as st

from dados import ANO_QUEBRA_SCN, CODIGO_IPEA, amostra_ipeadata, eixo_ano
from interface import configurar_pagina

URL_ODS9 = (
    "https://upload.wikimedia.org/wikipedia/commons/7/7f/"
    "Objetivo_Desenvolvimento_Sustent%C3%A1vel_9_PT.webp"
)


def serie_transformacao() -> pd.DataFrame:
    """Série anual do Ipeadata com as colunas ano e valor já numéricas."""
    try:
        ipeadata = amostra_ipeadata(CODIGO_IPEA)
    except Exception as exc:
        st.error(f"Falha no Ipeadata: {exc}")
        return pd.DataFrame()
    if ipeadata.empty or "YEAR" not in ipeadata.columns:
        return pd.DataFrame()
    if "VALUE ((% PIB))" in ipeadata.columns:
        coluna = "VALUE ((% PIB))"
    elif "VALUE" in ipeadata.columns:
        coluna = "VALUE"
    else:
        return pd.DataFrame()
    serie = pd.DataFrame(
        {
            "ano": pd.to_numeric(ipeadata["YEAR"], errors="coerce"),
            "valor": pd.to_numeric(ipeadata[coluna], errors="coerce"),
        }
    )
    return serie.dropna().sort_values("ano")


def mostrar_inicio() -> None:
    configurar_pagina("Monitor Brasileiro de Desindustrialização")

    col_tit, col_img = st.columns((4, 1), vertical_alignment="center")
    with col_tit:
        st.title("Monitor Brasileiro de Desindustrialização")
        st.caption(
            "Participação da indústria de transformação no PIB "
            "(ODS 9, indicador 9.2.1)"
        )
    with col_img:
        st.image(URL_ODS9, width=120)

    col_problema, col_objetivo = st.columns(2)
    with col_problema:
        st.subheader("Problema")
        st.markdown(
            "A indústria de transformação perde participação no PIB brasileiro "
            "há décadas, movimento que a literatura chama de "
            "desindustrialização (Tregenna, 2009; Oreiro e Feijó, 2010). O "
            "resultado é menos emprego formal e de maior produtividade e menos "
            "capacidade de inovar e de exportar bens sofisticados. A evidência "
            "oficial existe, mas fica dispersa entre bases estatísticas e "
            "relatórios."
        )
    with col_objetivo:
        st.subheader("Objetivo")
        st.markdown(
            "- Reunir num só painel as séries oficiais do indicador 9.2.1 da "
            "ONU: IBGE/SIDRA, Ipeadata e World Bank.\n"
            "- Isolar a transformação do agregado industrial, que pode se "
            "sustentar na extrativa e na construção enquanto a manufatura "
            "recua.\n"
            "- Comparar o Brasil com outros países e registrar fonte, código "
            "da série e data de extração."
        )

    st.caption(
        "ODS 9, meta 9.2 | pilar Social do ESG | público: gestores de política "
        "industrial, federações, pesquisadores e áreas de ESG."
    )

    st.subheader("A trajetória brasileira")

    serie = serie_transformacao()

    if not serie.empty:
        ultimo = serie.iloc[-1]
        base = serie[serie["ano"] == ANO_QUEBRA_SCN]
        comparavel = serie[serie["ano"] >= ANO_QUEBRA_SCN]
        if comparavel.empty:
            comparavel = serie

        c1, c2, c3 = st.columns(3)
        c1.metric(
            f"Transformação no PIB ({int(ultimo['ano'])})",
            f"{ultimo['valor']:.1f}%",
        )
        if not base.empty:
            variacao = ultimo["valor"] - float(base.iloc[0]["valor"])
            c2.metric(
                f"Variação desde {ANO_QUEBRA_SCN}",
                f"{variacao:+.1f} p.p.",
            )
        c3.metric(
            "Máximo do período",
            f"{comparavel['valor'].max():.1f}%",
        )

        st.line_chart(eixo_ano(comparavel.set_index("ano")[["valor"]]))
        st.caption(
            f"Série {CODIGO_IPEA} (Ipeadata, preços correntes), "
            f"de {ANO_QUEBRA_SCN} em diante, quando os níveis das Contas "
            "Nacionais passam a ser comparáveis."
        )

    with st.expander("Como ler os dados"):
        st.markdown(
            "**Indústria** (código 90691 no SIDRA) é o agregado, que inclui "
            "extrativa, construção e utilities. **Transformação** (90693) é a "
            "manufatura, objeto da desindustrialização na literatura.\n\n"
            "As séries do SIDRA e do Ipeadata estão a preços correntes: a "
            "participação no PIB também se move quando muda o preço relativo "
            "dos setores, e não apenas o volume produzido."
        )

    st.subheader("Páginas do painel")

    atalhos = [
        (panorama, "Último trimestre do SIDRA, com os subsetores industriais."),
        (historico, "Série anual do Ipeadata, no maior período disponível."),
        (internacional, "World Bank, a partir do CSV enviado pelo usuário."),
        (ods9, "Texto do Ipea, nuvem de palavras e frequência."),
        (fontes, "Links oficiais, hierarquia das fontes e ressalvas."),
    ]

    for comeco in (0, 3):
        colunas = st.columns(3)
        for col, (pagina, descricao) in zip(colunas, atalhos[comeco:comeco + 3]):
            with col:
                st.page_link(pagina, width="stretch")
                st.caption(descricao)


inicio = st.Page(mostrar_inicio, title="Início", default=True)
panorama = st.Page("pages/1_Panorama_setorial.py", title="Panorama setorial")
historico = st.Page("pages/2_Serie_historica.py", title="Série histórica")
internacional = st.Page(
    "pages/3_Comparacao_internacional.py", title="Comparação internacional"
)
ods9 = st.Page("pages/4_Contexto_ODS9.py", title="Contexto ODS 9")
fontes = st.Page("pages/5_Fontes_e_metodo.py", title="Fontes e método")

pg = st.navigation([inicio, panorama, historico, internacional, ods9, fontes])
pg.run()
