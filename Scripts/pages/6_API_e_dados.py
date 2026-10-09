import requests
import streamlit as st

from cliente_api import COMANDO_UVICORN, api_disponivel, limpar_cache_api, url_api
from interface import configurar_pagina

configurar_pagina("API e dados")

st.title("API e dados")
st.caption(
    "A API FastAPI local alimenta as páginas Início, Série histórica e "
    "Contexto ODS 9. Esta página mostra se o serviço está no ar e envia "
    "textos pelo POST /documentos. O Streamlit Community Cloud não sobe "
    "esta API: no deploy público as demais páginas caem na leitura direta. "
    "Documentação das rotas em Code/api/README.md e em /docs."
)

base = url_api()
st.caption(f"URL da API: `{base}` (padrão local; sobrescreva com API_URL em secrets).")

disponivel = api_disponivel()
if disponivel:
    st.success("API no ar.")
    st.link_button("Abrir /docs (Swagger)", f"{base}/docs")
else:
    st.warning(
        "A API não está no ar. Na raiz do repositório, em outro terminal, rode:\n\n"
        f"`{COMANDO_UVICORN}`\n\n"
        "Início, Série histórica e Contexto ODS 9 passam a ler os dados "
        "direto das fontes (SIDRA, Ipeadata e Data/raw/)."
    )

st.subheader("O que cada página consome")
st.markdown(
    """
- **Início:** GET /fatos/resumo (números) e GET /serie/transformacao (gráfico).
- **Série histórica:** GET /serie/transformacao.
- **Contexto ODS 9:** GET /ods9/metas e, na aba Corpus, GET /documentos.
- **Esta página:** POST /documentos (envio de texto para o corpus).
"""
)

st.subheader("Enviar documento (POST /documentos)")
if not disponivel:
    st.info("O envio só funciona com a API no ar.")
else:
    with st.form("form_documento"):
        titulo = st.text_input("Título")
        fonte = st.text_input("Fonte", value="Usuário")
        data = st.text_input("Data (AAAA-MM-DD)")
        url = st.text_input("URL (opcional)")
        texto = st.text_area("Texto")
        enviar = st.form_submit_button("Enviar")

    if enviar:
        if (
            not titulo.strip()
            or not texto.strip()
            or not fonte.strip()
            or not data.strip()
        ):
            st.error("Preencha título, texto, fonte e data.")
        else:
            corpo = {
                "titulo": titulo.strip(),
                "texto": texto.strip(),
                "fonte": fonte.strip(),
                "data": data.strip(),
                "url": url.strip(),
                "tipo": "usuario",
            }
            try:
                resposta = requests.post(
                    f"{base}/documentos", json=corpo, timeout=30
                )
                if resposta.status_code >= 400:
                    st.error(f"HTTP {resposta.status_code}: {resposta.text}")
                else:
                    limpar_cache_api()
                    st.success(
                        "Documento gravado em Data/processed/documentos.csv. "
                        "Ele aparece na aba Corpus da página Contexto ODS 9."
                    )
                    st.json(resposta.json())
            except requests.RequestException as exc:
                st.error(f"Falha no envio: {exc}")
