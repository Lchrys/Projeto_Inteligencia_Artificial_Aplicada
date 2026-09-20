import pandas as pd
import requests
import streamlit as st

from dados import (
    DATA_CONSULTA,
    URL_SIDRA_SUBSETORES,
    URL_SIDRA_TRIMESTRAL,
    amostra_sidra,
)
from interface import botao_download, configurar_pagina

configurar_pagina("Panorama setorial")

st.title("Panorama setorial")
st.caption(
    "IBGE/SIDRA, Agregados v3, tabela 1846 (último trimestre). "
    "É a foto do trimestre mais recente, não a tendência: "
    "desindustrialização é um processo de décadas, visível na série "
    "longa do Ipeadata e do World Bank."
)

try:
    sidra_trimestral = amostra_sidra(URL_SIDRA_TRIMESTRAL)
    sidra_anual = amostra_sidra(URL_SIDRA_SUBSETORES)
except requests.RequestException as exc:
    st.error(f"Falha no SIDRA: {exc}")
    sidra_trimestral = pd.DataFrame()
    sidra_anual = pd.DataFrame()

aba_tri, aba_sub = st.tabs(["Trimestral", "Subsetores"])

with aba_tri:
    st.caption(
        "PIB, agropecuária, indústria e serviços a preços correntes. "
        "Agropecuária + indústria + serviços não somam o PIB a preços "
        "de mercado (faltam os impostos líquidos)."
    )
    st.dataframe(sidra_trimestral, hide_index=True, width="stretch")
    botao_download(
        sidra_trimestral,
        "sidra_trimestral.csv",
        "dl_sidra_tri",
        fonte="IBGE/SIDRA, tabela 1846",
        codigo_serie="1846; 90707,90687,90691,90696",
        data_extracao=DATA_CONSULTA,
    )

with aba_sub:
    st.caption(
        "Subsetores industriais: transformação (90693), extrativas, "
        "construção e eletricidade/gás/água. A abertura mostra quanto "
        "da indústria total é manufatura: o agregado pode se sustentar "
        "por extrativa ou construção enquanto a transformação recua."
    )
    st.dataframe(sidra_anual, hide_index=True, width="stretch")
    botao_download(
        sidra_anual,
        "sidra_subsetores.csv",
        "dl_sidra_sub",
        fonte="IBGE/SIDRA, tabela 1846",
        codigo_serie="1846; 90693,90692,90694,90695",
        data_extracao=DATA_CONSULTA,
    )
