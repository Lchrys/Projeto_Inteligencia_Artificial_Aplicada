import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from cliente_api import obter, quadro, legenda_origem
from dados import (
    COLUNAS_DOCUMENTOS,
    data_consulta,
    carregar_corpus_ods9,
    carregar_ods9,
    frequencia_palavras,
    imagem_nuvem,
)
from interface import botao_download, configurar_pagina
from nucleo import carregar_documentos, documentos_ods9, filtrar_documentos

configurar_pagina("Contexto ODS 9")

st.title("Contexto ODS 9")
st.caption(
    "Ipea, página ODS 9, extração com Beautiful Soup "
    "(script Code/data_acquisition/scrape_ods9.py). Os arquivos "
    "estão em Data/raw/. O indicador 9.2.1 (valor adicionado da "
    "indústria em proporção do PIB) é o recorte numérico deste painel. "
    "As metas vêm de GET /ods9/metas quando a API está no ar. A aba "
    "Corpus reúne essas metas e os documentos enviados por POST /documentos."
)

aba_meta, aba_corpus = st.tabs(["Meta", "Corpus"])


def _fallback_metas() -> dict:
    return {"dados": carregar_ods9().to_dict(orient="records")}


def _fallback_documentos() -> dict:
    return {"dados": carregar_documentos().to_dict(orient="records")}


with aba_meta:
    payload, origem = obter("/ods9/metas", fallback=_fallback_metas)
    ods9 = quadro(payload)
    corpus = carregar_corpus_ods9()
    if ods9.empty:
        st.warning(
            "Arquivo Data/raw/ods9_metas.csv não encontrado. "
            "Rode: python Code/data_acquisition/scrape_ods9.py"
        )
    else:
        opcoes = ods9["meta"].astype(str).tolist()
        padrao = opcoes.index("9.2") if "9.2" in opcoes else 0
        escolha = st.selectbox(
            "Meta do ODS 9", opcoes, index=padrao, key="meta_ods9"
        )
        linha = ods9[ods9["meta"].astype(str) == escolha].iloc[0]
        st.markdown(f"**ONU:** {linha['onu']}")
        st.markdown(f"**Brasil:** {linha['brasil']}")
        st.markdown(f"**Indicadores:** {linha['indicadores']}")
        if escolha == "9.2":
            st.info(
                "O indicador 9.2.1 é o mesmo conceito das séries oficiais "
                "deste painel (IBGE/SIDRA, Ipeadata e World Bank "
                "NV.IND.MANF.ZS). A redação da ONU pede aumentar a "
                "participação da indústria no PIB e no emprego; a redação "
                "brasileira trocou esse foco por produtividade e "
                "complexidade tecnológica, com o argumento de que o baixo "
                "dinamismo não vem da mudança estrutural entre indústria e "
                "serviços. As duas leituras convivem no painel: a série "
                "mede o indicador da ONU, e o texto ao lado é a ressalva "
                "oficial brasileira."
            )
        if corpus:
            st.download_button(
                "Baixar o texto extraído (TXT)",
                corpus.encode("utf-8"),
                file_name="ods9_corpus.txt",
                mime="text/plain",
                key="dl_ods9_txt",
            )
        st.markdown("#### Nuvem de palavras e frequência")
        escopo_nuvem = st.radio(
            "Texto da nuvem",
            ("Meta selecionada", "ODS 9 completo"),
            horizontal=True,
            key="escopo_nuvem_ods9",
        )
        corpus_completo = escopo_nuvem == "ODS 9 completo"
        if corpus_completo:
            texto_nuvem = corpus
            st.caption(
                "Calculadas sobre o texto de todas as metas do ODS 9 "
                "(9.1 a 9.c). Termos de infraestrutura, crédito e "
                "tecnologia vêm do restante do objetivo."
            )
        else:
            texto_nuvem = " ".join(
                str(linha[campo])
                for campo in ("onu", "brasil", "justificativa", "conceitos")
                if campo in linha.index
                and pd.notna(linha[campo])
                and str(linha[campo]).strip()
            )
            st.caption(
                f"Calculadas sobre a meta {escolha} (redação da ONU, "
                "redação brasileira, justificativa e conceitos)."
            )
        if not texto_nuvem.strip():
            st.warning("Não há texto suficiente para a nuvem neste recorte.")
        else:
            arr = imagem_nuvem(texto_nuvem, corpus_completo)
            if arr is not None:
                fig, ax = plt.subplots()
                ax.imshow(arr, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
                plt.close(fig)
            freq = frequencia_palavras(
                texto_nuvem, corpus_completo=corpus_completo
            )
            if not freq.empty:
                st.bar_chart(freq)
        legenda_origem(origem)

with aba_corpus:
    payload_docs, origem_docs = obter(
        "/documentos", fallback=_fallback_documentos
    )
    enviados = quadro(payload_docs)
    metas_docs = documentos_ods9()
    if enviados.empty:
        quadro_corpus = metas_docs
    else:
        quadro_corpus = pd.concat([metas_docs, enviados], ignore_index=True)
    if quadro_corpus.empty:
        st.warning(
            "Não há textos para exibir. Confirme Data/raw/ods9_metas.csv "
            "ou envie um documento pela página API e dados."
        )
    else:
        fontes = sorted(
            quadro_corpus["fonte"].dropna().astype(str).unique()
        )
        escolhidas = st.multiselect(
            "Fonte", fontes, default=fontes, key="corpus_fontes"
        )
        termo = st.text_input("Busca no título ou no texto", key="corpus_busca")
        recorte = quadro_corpus[
            quadro_corpus["fonte"].astype(str).isin(escolhidas)
        ].copy()
        recorte = filtrar_documentos(recorte, busca=termo.strip() or None)
        st.metric("Documentos no recorte", len(recorte))
        if recorte.empty:
            st.info("Nenhum documento com esses filtros.")
        else:
            visivel = recorte.loc[
                :, [c for c in COLUNAS_DOCUMENTOS if c in recorte.columns]
            ]
            st.dataframe(visivel, hide_index=True, width="stretch")
            botao_download(
                visivel,
                "corpus_textual.csv",
                "dl_corpus",
                "Baixar recorte (CSV)",
                fonte="Metas ODS 9 (Ipea) e documentos enviados pela API",
                codigo_serie="ods9; documentos",
                data_extracao=data_consulta(),
            )
            texto = " ".join(recorte["texto"].fillna("").astype(str))
            if texto.strip():
                st.subheader("Frequência de palavras")
                freq = frequencia_palavras(texto)
                if not freq.empty:
                    st.bar_chart(freq)
                else:
                    st.caption(
                        "Não há palavras suficientes depois das stopwords."
                    )
        st.caption(
            "Metas do ODS 9 vêm do arquivo extraído; documentos enviados "
            "vêm de GET /documentos quando a API está no ar."
        )
        legenda_origem(origem_docs)
