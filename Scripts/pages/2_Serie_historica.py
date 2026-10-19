import pandas as pd
import streamlit as st

from cliente_api import obter, quadro, legenda_origem
from dados import ANO_QUEBRA_SCN, CODIGO_IPEA, data_consulta, serie_transformacao
from interface import (
    aviso_quebra,
    botao_download,
    configurar_pagina,
    grafico_linha,
    metrica_completude,
    sobre_os_dados,
)

configurar_pagina("Série histórica")

st.title("Série histórica")
st.caption(
    "Qual foi a trajetória da indústria de transformação no PIB brasileiro "
    "no maior período disponível."
)
sobre_os_dados(
    f"Ipeadata, série {CODIGO_IPEA} (PIB - indústria - transformação - "
    "preços correntes, % PIB), compilada do IBGE/SCN Anual via ipeadatapy. "
    "É o indicador 9.2.1 da ONU, não uma fonte independente do IBGE. "
    "A página consome GET /serie/transformacao quando a API está no ar."
)


def _fallback_serie() -> dict:
    return {"dados": serie_transformacao().to_dict(orient="records")}


try:
    payload, origem = obter("/serie/transformacao", fallback=_fallback_serie)
except Exception as exc:
    st.error(f"Falha no Ipeadata: {exc}")
    payload, origem = {"dados": []}, "leitura direta"

serie = quadro(payload)
if not serie.empty and "ano" in serie.columns:
    serie["ano"] = pd.to_numeric(serie["ano"], errors="coerce")
    serie["valor"] = pd.to_numeric(serie.get("valor"), errors="coerce")
    serie = serie.dropna(subset=["ano"]).sort_values("ano")

if not serie.empty:
    anos = serie["ano"].dropna()
    minimo, maximo = int(anos.min()), int(anos.max())
    inicio_padrao = (
        max(minimo, ANO_QUEBRA_SCN) if maximo >= ANO_QUEBRA_SCN else minimo
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
    anos_com_valor = serie.loc[serie["valor"].notna(), "ano"]
    serie = serie[
        (serie["ano"] >= intervalo[0]) & (serie["ano"] <= intervalo[1])
    ]
    if "valor" in serie.columns:
        grafico_linha(serie[["ano", "valor"]])
        metrica_completude(
            serie["valor"],
            anos=anos_com_valor,
            inicio=intervalo[0],
            fim=intervalo[1],
        )

legenda_origem(origem)

visivel = serie.copy()
if "ano" in visivel.columns:
    visivel["ano"] = visivel["ano"].astype("Int64").astype(str)
st.dataframe(visivel, hide_index=True, width="stretch")
botao_download(
    visivel,
    "ipeadata.csv",
    "dl_ipea",
    fonte="Ipeadata",
    codigo_serie=CODIGO_IPEA,
    data_extracao=data_consulta(),
)
