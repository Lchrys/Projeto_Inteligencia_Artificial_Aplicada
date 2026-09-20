import pandas as pd
import streamlit as st

from dados import ANO_QUEBRA_SCN, CODIGO_IPEA, DATA_CONSULTA, amostra_ipeadata, eixo_ano
from interface import aviso_quebra, botao_download, configurar_pagina, metrica_completude

configurar_pagina("Série histórica")

st.title("Série histórica")
st.caption(
    "Ipeadata, extração via ipeadatapy (OData4 ValoresSerie). "
    f"Série {CODIGO_IPEA}: PIB - indústria - transformação - "
    "preços correntes (% PIB), IBGE/SCN Anual. É a série principal do "
    "painel, no maior período disponível: mesmo conceito do indicador "
    "9.2.1 da ONU. Não é fonte independente do IBGE: o Ipeadata "
    "compila o próprio SCN, em frequência anual."
)

try:
    ipeadata = amostra_ipeadata(CODIGO_IPEA)
except Exception as exc:
    st.error(f"Falha no Ipeadata: {exc}")
    ipeadata = pd.DataFrame()

if not ipeadata.empty and "YEAR" in ipeadata.columns:
    anos = pd.to_numeric(ipeadata["YEAR"], errors="coerce").dropna()
    if not anos.empty:
        minimo, maximo = int(anos.min()), int(anos.max())
        inicio_padrao = (
            max(minimo, ANO_QUEBRA_SCN)
            if maximo >= ANO_QUEBRA_SCN
            else minimo
        )
        if inicio_padrao > maximo:
            inicio_padrao = minimo
        intervalo = st.slider(
            "Anos (Ipeadata)",
            min_value=minimo,
            max_value=maximo,
            value=(inicio_padrao, maximo),
            format="%d",
            key="filtro_ipea",
        )
        st.caption(
            "A série completa continua disponível no slider. "
            f"Só de {ANO_QUEBRA_SCN} em diante os níveis são comparáveis."
        )
        aviso_quebra(intervalo[0], intervalo[1])
        ipeadata = ipeadata[
            (ipeadata["YEAR"] >= intervalo[0])
            & (ipeadata["YEAR"] <= intervalo[1])
        ]
    if "VALUE ((% PIB))" in ipeadata.columns:
        grafico = ipeadata.set_index("YEAR")[["VALUE ((% PIB))"]]
        st.line_chart(eixo_ano(grafico))
        metrica_completude(ipeadata["VALUE ((% PIB))"])
    elif "VALUE" in ipeadata.columns:
        st.line_chart(eixo_ano(ipeadata.set_index("YEAR")[["VALUE"]]))
        metrica_completude(ipeadata["VALUE"])

visivel = ipeadata.copy()
if "YEAR" in visivel.columns:
    visivel["YEAR"] = visivel["YEAR"].astype("Int64").astype(str)
st.dataframe(visivel, hide_index=True, width="stretch")
botao_download(
    visivel,
    "ipeadata.csv",
    "dl_ipea",
    fonte="Ipeadata",
    codigo_serie=CODIGO_IPEA,
    data_extracao=DATA_CONSULTA,
)
