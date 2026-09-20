import streamlit as st

from interface import configurar_pagina

configurar_pagina("Fontes e método")

st.title("Fontes e método")
st.caption(
    "Fontes oficiais previstas no Data Summary Report e referências "
    "do ODS 9 usadas no recorte do projeto."
)

fontes_extracao = [
    ("IBGE / SIDRA", "https://sidra.ibge.gov.br/", "Contas Nacionais"),
    ("API Sidra", "https://apisidra.ibge.gov.br/home/ajuda", "Contrato da API"),
    ("Ipeadata", "https://www.ipeadata.gov.br/", "Séries históricas"),
    (
        "DataBank",
        "https://databank.worldbank.org/source/world-development-indicators",
        "NV.IND.MANF.ZS (CSV)",
    ),
]
fontes_contexto = [
    ("ONU, ODS 9", "https://brasil.un.org/pt-br/sdgs/9", "Iniciativa e meta 9.2"),
    ("Ipea ODS 9", "https://www.ipea.gov.br/ods/ods9.html", "Indicadores nacionais"),
    ("Morceiro (2021)", "https://periodicos.fgv.br/bjpe/article/view/95029", "Validação cruzada"),
]

st.caption("Extração das séries (SIDRA e Ipeadata por API; World Bank por CSV)")
for col, (rotulo, url, nota) in zip(st.columns(4), fontes_extracao):
    with col:
        st.link_button(rotulo, url, width="stretch")
        st.caption(nota)

st.caption("ODS e literatura")
for col, (rotulo, url, nota) in zip(st.columns(3), fontes_contexto):
    with col:
        st.link_button(rotulo, url, width="stretch")
        st.caption(nota)

st.markdown("### Hierarquia das fontes")
st.markdown(
    """
- **Fonte principal:** Ipeadata (SCN10_VAITY10) e World Bank
  (NV.IND.MANF.ZS). São o indicador 9.2.1 da ONU em série anual longa.
- **Fonte de composição:** IBGE/SIDRA, tabela 1846. Foto do trimestre
  mais recente, para separar manufatura do agregado indústria.
- **Fonte de contexto:** página ODS 9 do Ipea. Texto, não série.
    """
)

st.markdown("### Ressalvas de método")
st.markdown(
    """
1. Ipeadata e World Bank não são evidência independente do IBGE: ambos
   compilam contas nacionais.
2. No SIDRA, indústria (90691) é o agregado; transformação (90693) é a
   manufatura.
3. As séries do SIDRA e do Ipeadata estão a preços correntes.
4. As séries medem o indicador da ONU; o texto do Ipea entra como
   ressalva oficial brasileira.
5. Só de 1995 em diante os níveis das Contas Nacionais brasileiras são
   comparáveis (Morceiro, 2021).
    """
)

st.markdown("### Referências")
st.markdown(
    "Citações completas em Docs/Referencias.md. A literatura entra na "
    "validação cruzada do Data Summary Report, fora dos gráficos."
)

st.caption(
    "O serviço de upload e download fica na página Comparação internacional: "
    "baixe o CSV de exemplo e envie-o no painel para filtrar, ver gráficos e "
    "baixar o recorte. A página Contexto ODS 9 lê o scraping já gravado em "
    "Data/raw/."
)
