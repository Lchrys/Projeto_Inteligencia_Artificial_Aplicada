"""Chat com memória que cada página do painel mostra no fim (TP5).

`chat_da_pagina` recebe o contexto da página (as tabelas que ela mostra, ver contextos.py) e o envia, com a
pergunta e o histórico, à rota POST /chat da API FastAPI (Code/api/routers/chat.py), que chama o assistente
(Code/modeling/assistente.py). O painel sobe a API sozinho ao abrir (cliente_api.garantir_api); o chat só funciona
com ela no ar, e, se ela não subir, a página mostra o comando para subi-la à mão. O histórico fica em `st.session_state`, separado por página, e só vive na sessão do usuário. A
chave da OpenAI fica no `.env` da máquina da API.
"""

import streamlit as st

from cliente_api import COMANDO_UVICORN, LOG_API, ApiForaDoAr, ErroApi, api_disponivel, conversar

LIMITE_PERGUNTA = 500


def texto_para_exibir(texto: str) -> str:
    """Escapa o "$": o Streamlit lê `$...$` como fórmula e engole o texto entre dois "R$"."""
    return texto.replace("$", "\\$")


def mensagem_de_erro(falha: Exception) -> str:
    """A frase que o chat mostra quando a API não devolve uma resposta."""
    if isinstance(falha, ErroApi):
        return f"Não consegui responder: {falha.detalhe}"
    return (
        "Não consegui responder: a API não está no ar. Em outro terminal, na raiz do projeto, rode "
        f"`{COMANDO_UVICORN}` e pergunte de novo."
    )


def chat_da_pagina(chave: str, contexto: str, sugestoes: tuple[str, ...] = ()) -> None:
    """Desenha o chat da página `chave` (um histórico por página) com o `contexto` dado ao modelo."""
    historico: list[dict] = st.session_state.setdefault(f"chat_{chave}", [])

    st.divider()
    st.subheader("Pergunte aos dados desta página")
    if not api_disponivel():
        st.warning(
            "O chat usa a API do projeto. O painel a sobe sozinho ao abrir, mas ela não respondeu (a porta pode "
            f"estar ocupada; veja `{LOG_API}`). Em outro terminal, na raiz do projeto, rode o comando abaixo e "
            "recarregue a página (o painel confere a API a cada 30 s):"
        )
        st.code(COMANDO_UVICORN, language=None)
        return
    st.caption(
        "O assistente (modelo da OpenAI) lembra a conversa e responde só com o que esta página mostra, "
        "com os filtros aplicados: para perguntar sobre outro ano, país ou indicador, mude o filtro. "
        "Ele pode errar: confira os números antes de usar como fato."
    )

    def perguntar(pergunta: str) -> None:
        anteriores = [{"papel": m["papel"], "conteudo": m["conteudo"]} for m in historico if not m.get("erro")]
        historico.append({"papel": "user", "conteudo": pergunta})
        try:
            with st.spinner("Consultando o assistente..."):
                resultado = conversar(pergunta, anteriores, contexto)
        except (ErroApi, ApiForaDoAr) as falha:
            historico.append({"papel": "assistant", "conteudo": mensagem_de_erro(falha), "erro": True})
            return
        historico.append(
            {
                "papel": "assistant",
                "conteudo": resultado["resposta"],
                "motor": resultado["motor"],
                "nao_verificados": resultado["numeros_nao_verificados"],
                "contas": resultado["contas_conferidas"],
                "fontes": resultado["fontes"],
            }
        )

    if historico and st.button("Nova conversa", key=f"nova_{chave}"):
        historico.clear()
        st.rerun()

    if not historico:
        for i, sugestao in enumerate(sugestoes):
            if st.button(sugestao, key=f"sugestao_{chave}_{i}", width="stretch"):
                perguntar(sugestao)
                st.rerun()

    for mensagem in historico:
        with st.chat_message(mensagem["papel"]):
            st.write(texto_para_exibir(mensagem["conteudo"]))
            if mensagem["papel"] == "assistant" and not mensagem.get("erro"):
                if mensagem.get("contas"):
                    st.caption("Conta conferida pelo código: " + "; ".join(mensagem["contas"]))
                if mensagem["nao_verificados"]:
                    st.warning(
                        "O assistente citou números que não estão nas tabelas desta página (nem são o resultado "
                        "de uma conta com valores da própria resposta): "
                        + ", ".join(mensagem["nao_verificados"])
                        + ". Pode ser só formatação ou um erro dele. Confira nas tabelas antes de usar."
                    )
                st.caption("Fonte das tabelas: " + "; ".join(mensagem["fontes"]))
                st.caption(f"Modelo: {mensagem['motor']} | gerado por IA, confira nas tabelas de origem.")

    pergunta = st.chat_input("Pergunte sobre os dados desta página", max_chars=LIMITE_PERGUNTA, key=f"entrada_{chave}")
    if pergunta:
        perguntar(pergunta.strip())
        st.rerun()

    with st.expander("Dados que o assistente recebe"):
        st.caption("Exatamente este texto vai ao modelo a cada pergunta, junto com o histórico recente.")
        st.code(contexto, language=None)
