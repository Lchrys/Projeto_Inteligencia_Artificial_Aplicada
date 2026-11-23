import pandas as pd
import streamlit as st

from cliente_api import (
    COMANDO_UVICORN,
    api_disponivel,
    obter,
    quadro,
    url_api,
)
from dados import (
    URL_SIDRA_TRIMESTRAL,
    amostra_sidra,
    serie_transformacao,
)
from interface import configurar_pagina, sobre_os_dados
from nucleo import avaliar_criterios, conferir_somas

configurar_pagina("Fontes e método")

st.title("Fontes e método")
st.caption(
    "De onde vêm os números do painel, as ressalvas de método e a "
    "verificação dos critérios de sucesso, inclusive os do chat."
)
sobre_os_dados(
    "Hierarquia das fontes, ressalvas de método e fichas completas estão "
    "em Docs/Data_Summary_Report.md. Esta página só resume e verifica os "
    "critérios de sucesso do Project Charter."
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
Resumo. Detalhe em Docs/Data_Summary_Report.md:

- **Principal:** Ipeadata (SCN10_VAITY10) e World Bank (NV.IND.MANF.ZS) —
  indicador 9.2.1 em série anual.
- **Composição:** IBGE/SIDRA, tabela 1846 — foto dos últimos quatro
  trimestres, para separar manufatura do agregado indústria.
- **Contexto:** página ODS 9 do Ipea — texto, não série.
    """
)

st.markdown("### Ressalvas de método")
st.markdown(
    """
As cinco ressalvas (Ipeadata e World Bank compilam o IBGE; indústria ≠
transformação; preços correntes; redação ONU vs. Brasil; comparabilidade
só a partir de 1995) estão no Data Summary Report. O painel sinaliza a
quebra de 1995 nos gráficos.
    """
)

st.markdown("### Critérios de sucesso")
st.caption(
    "Verificação automática dos critérios do Project Charter. "
    "Itens que dependem de SIDRA, Ipeadata ou da API local podem ficar "
    "como 'não verificado' se a fonte não responder agora."
)


def _fallback_serie() -> dict:
    return {"dados": serie_transformacao().to_dict(orient="records")}


serie = pd.DataFrame()
try:
    payload, _origem = obter("/serie/transformacao", fallback=_fallback_serie)
    serie = quadro(payload)
except Exception:
    serie = pd.DataFrame()

somas = None
try:
    somas = conferir_somas(amostra_sidra(URL_SIDRA_TRIMESTRAL))
except Exception:
    somas = None

itens = avaliar_criterios(serie, somas, api_disponivel())
for item in itens:
    status = item["status"]
    if status == "atendido":
        st.success(f"{item['criterio']} — {status}. {item['detalhe']}")
    elif status == "não atendido":
        st.error(f"{item['criterio']} — {status}. {item['detalhe']}")
    else:
        st.info(f"{item['criterio']} — {status}. {item['detalhe']}")

st.markdown("### Critérios do chat com IA")
st.markdown(
    """
O chat no fim das páginas Panorama setorial, Série histórica e Comparação internacional responde só com o que a
página mostra. Como cada critério é conferido:

- **Memória:** a segunda pergunta usa o contexto da primeira (últimas 6 trocas). Testado no código e observado
  em 24 casos reais (`Data/modeled/chat_openai_casos.csv`).
- **Números só dos dados:** o código confere cada resposta e a página avisa o que não estiver nas tabelas nem
  for o resultado de uma conta com valores da resposta; as contas conferidas são exibidas. Coberto por teste
  automático.
- **Só dados da aplicação:** o contexto vem das tabelas da própria página, com os filtros aplicados; sem o CSV
  do DataBank enviado, a Comparação internacional não tem dados nem chat. Coberto por teste automático.
- **Fonte citada:** o código mostra, sob toda resposta, a fonte das tabelas enviadas ao modelo, sem depender de
  ele citá-la. Coberto por teste automático.
- **Falha da OpenAI ou da API:** mensagem clara no chat (503, 429, 502, 504), e, com a API fora do ar, o aviso com o
  comando para subi-la; a página não cai. Coberto por teste automático.

Funcionamento e chave da OpenAI: README, seção 4.
"""
)

st.markdown("### Referências")
st.markdown(
    "Citações completas em Docs/Referencias.md. A literatura entra na "
    "validação cruzada do Data Summary Report, fora dos gráficos."
)

st.markdown("### Informações técnicas (API local)")
base = url_api()
st.caption(f"URL da API: `{base}` (padrão local; sobrescreva com API_URL em secrets).")
if api_disponivel():
    st.success("API no ar.")
    st.link_button("Abrir /docs (Swagger)", f"{base}/docs")
else:
    st.warning(
        "A API não está no ar. O painel tenta subi-la sozinho ao abrir; se ela não respondeu, na raiz do "
        "repositório, em outro terminal, rode:\n\n"
        f"`{COMANDO_UVICORN}`\n\n"
        "Início, Série histórica, Comparação internacional e Corpus e resumos "
        "passam a ler os dados direto (SIDRA, Ipeadata, CSV enviado e Data/raw/)."
    )
st.markdown(
    """
O que cada página consome quando a API está no ar:

- **Início:** GET /fatos/resumo (números) e GET /serie/transformacao (gráfico).
- **Série histórica:** GET /serie/transformacao.
- **Comparação internacional:** POST /world-bank (CSV do DataBank) e GET /world-bank/{id}.
- **Corpus e resumos:** GET /ods9/metas.
- **Chat (Panorama setorial, Série histórica e Comparação internacional):** POST /chat (só funciona com a API no ar).
- **Panorama setorial:** SIDRA direto (não passa pela API).
"""
)
