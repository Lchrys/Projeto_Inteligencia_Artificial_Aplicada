"""Rota do chat com memória (TP5): o mesmo assistente que as páginas do painel usam.

POST /chat recebe a pergunta, o histórico da conversa e o contexto (as tabelas da página) e devolve a
resposta do assistente (Code/modeling/assistente.py), com os números conferidos pelo código.

- A rota é `def`, não `async def`: a chamada à OpenAI bloqueia até a resposta e travaria o laço assíncrono.
- O histórico não fica na API: o cliente o envia a cada pedido (a API não guarda conversa).
- A chave da OpenAI é lida do ambiente ou do `.env` da raiz, pelo próprio assistente. Nunca vai na resposta.
- Códigos de erro desta rota (os mesmos do assistente):
    422 — entrada fora do contrato (pergunta vazia ou longa, contexto vazio ou grande, campo extra).
    429 — limite de uso ou crédito da OpenAI esgotado.
    502 — a OpenAI recusou a chave, falhou, ficou sem internet ou devolveu resposta vazia.
    503 — a chave da OpenAI não está configurada.
    504 — a OpenAI não respondeu no tempo limite.
    500 — erro inesperado; vem da rede de segurança de erros.py.
"""

from fastapi import APIRouter, HTTPException

from Code.api.erros import erro
from Code.api.models import PedidoChat, RespostaChat
from Code.modeling import assistente

router = APIRouter(tags=["chat com IA"])


@router.post(
    "/chat",
    response_model=RespostaChat,
    responses={
        429: erro("Limite de uso ou crédito da OpenAI esgotado."),
        502: erro("A OpenAI recusou a chave, falhou, ficou sem internet ou devolveu resposta vazia."),
        503: erro("A chave da OpenAI não está configurada na máquina da API."),
        504: erro("A OpenAI não respondeu no tempo limite."),
    },
    summary="Perguntar aos dados de uma página, com memória da conversa",
    description=(
        "Responde só com as tabelas enviadas em `contexto`, usando `historico` para entender perguntas "
        "curtas como \"e em 2024?\". Os números da resposta são conferidos pelo código: o que não estiver nas "
        "tabelas, na pergunta ou numa conta com valores da própria resposta vem em `numeros_nao_verificados`. "
        "`fontes` traz a fonte de cada tabela. A resposta é gerada por modelo e precisa de revisão humana."
    ),
)
def chat(pedido: PedidoChat) -> dict:
    historico = [mensagem.model_dump() for mensagem in pedido.historico]
    try:
        return assistente.responder(pedido.pergunta, historico, pedido.contexto)
    except assistente.ErroAssistente as falha:
        raise HTTPException(status_code=falha.status, detail=falha.mensagem) from falha
