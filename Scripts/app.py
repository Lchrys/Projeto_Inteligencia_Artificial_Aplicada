import pandas as pd
import streamlit as st

from cliente_api import obter, quadro, legenda_origem
from dados import ANO_QUEBRA_SCN, CODIGO_IPEA, eixo_ano, fatos_resumo, serie_transformacao
from interface import configurar_pagina

URL_ODS9 = (
    "https://upload.wikimedia.org/wikipedia/commons/7/7f/"
    "Objetivo_Desenvolvimento_Sustent%C3%A1vel_9_PT.webp"
)


def _fallback_serie() -> dict:
    return {"dados": serie_transformacao().to_dict(orient="records")}


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

    try:
        fatos, origem = obter("/fatos/resumo", fallback=fatos_resumo)
        payload_serie, origem_serie = obter(
            "/serie/transformacao", fallback=_fallback_serie
        )
    except Exception as exc:
        st.error(f"Falha no Ipeadata: {exc}")
        fatos, origem, payload_serie, origem_serie = {}, "leitura direta", {}, "leitura direta"

    serie = quadro(payload_serie)
    if not serie.empty and "ano" in serie.columns and "valor" in serie.columns:
        serie["ano"] = pd.to_numeric(serie["ano"], errors="coerce")
        serie["valor"] = pd.to_numeric(serie["valor"], errors="coerce")
        serie = serie.dropna().sort_values("ano")

    bloco = fatos.get("serie") if isinstance(fatos, dict) else None
    if bloco:
        c1, c2, c3 = st.columns(3)
        c1.metric(
            f"Transformação no PIB ({int(bloco['ultimo_ano'])})",
            f"{bloco['ultimo_valor']:.1f}%",
        )
        if "variacao_desde_1995" in bloco:
            c2.metric(
                f"Variação desde {ANO_QUEBRA_SCN}",
                f"{bloco['variacao_desde_1995']:+.1f} p.p.",
            )
        c3.metric("Máximo do período", f"{bloco['maximo']:.1f}%")

    if not serie.empty:
        comparavel = serie[serie["ano"] >= ANO_QUEBRA_SCN]
        if comparavel.empty:
            comparavel = serie
        st.line_chart(eixo_ano(comparavel.set_index("ano")[["valor"]]))
        st.caption(
            f"Série {CODIGO_IPEA} (Ipeadata, preços correntes), "
            f"de {ANO_QUEBRA_SCN} em diante, quando os níveis das Contas "
            "Nacionais passam a ser comparáveis."
        )

    origem_pagina = origem if origem == origem_serie else f"{origem}; série: {origem_serie}"
    legenda_origem(origem_pagina)

    with st.expander("Como ler os dados"):
        st.markdown(
            "**Indústria** (código 90691 no SIDRA) é o agregado, que inclui "
            "extrativa, construção e utilities. **Transformação** (90693) é a "
            "manufatura, objeto da desindustrialização na literatura.\n\n"
            "As séries do SIDRA e do Ipeadata estão a preços correntes: a "
            "participação no PIB também se move quando muda o preço relativo "
            "dos setores, e não apenas o volume produzido.\n\n"
            "Os números desta página vêm de GET /fatos/resumo e o gráfico de "
            "GET /serie/transformacao quando a API está no ar."
        )

    st.subheader("Páginas do painel")

    atalhos = [
        (panorama, "Último trimestre do SIDRA, com os subsetores industriais."),
        (historico, "Série anual do Ipeadata, no maior período disponível."),
        (internacional, "World Bank, a partir do CSV enviado pelo usuário."),
        (ods9, "Texto do Ipea, nuvem de palavras, frequência e corpus."),
        (api_dados, "Status da API FastAPI e envio de textos pelo POST."),
        (fontes, "Links oficiais, hierarquia das fontes e ressalvas."),
    ]

    for comeco in (0, 3):
        fatia = atalhos[comeco:comeco + 3]
        colunas = st.columns(len(fatia))
        for col, (pagina, descricao) in zip(colunas, fatia):
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
api_dados = st.Page("pages/6_API_e_dados.py", title="API e dados")

pg = st.navigation(
    {
        "Painel": [inicio, panorama, historico],
        "Comparações e contexto": [internacional, ods9],
        "Dados e API": [api_dados, fontes],
    }
)
pg.run()
