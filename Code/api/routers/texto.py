"""Rota de processamento de texto com o modelo de linguagem local (TP4, Etapas 2 a 4).

POST /processar_texto recebe um texto e devolve o resumo gerado pelo modelo.

- O modelo é carregado UMA vez, quando a API sobe (carregar_na_subida, chamada pelo lifespan de main.py).
- A rota é `def`, não `async def`: a geração calcula na CPU e bloquearia o laço assíncrono.
- Códigos de erro desta rota:
    422 — entrada fora do contrato (texto curto, longo ou campo extra); vem do Pydantic.
    502 — o modelo devolveu um resumo vazio.
    503 — o modelo não carregou na subida da API.
    504 — a geração passou do tempo limite.
    500 — erro inesperado; vem da rede de segurança de erros.py.
"""

import concurrent.futures
import logging

from fastapi import APIRouter, HTTPException, status

from Code.api.erros import erro
from Code.api.models import AVISO_RESUMO, PedidoTexto, ResultadoResumo
from Code.modeling.resumidor import Resumidor, carregar, resumir

router = APIRouter(tags=["análise de texto"])
log = logging.getLogger("uvicorn.error")

# O modelo carregado mora aqui. Vazio se a carga falhou: a rota responde 503.
MODELOS: dict = {}

# Tempo máximo de espera por um resumo. Medido: 12 s a 38 s na máquina de referência.
TEMPO_LIMITE_SEGUNDOS = 120

# Uma geração de cada vez. A geração não pode ser interrompida no meio: se passar do
# tempo limite, a rota responde 504, mas a geração continua até terminar, e o pedido
# seguinte espera por ela.
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def carregar_na_subida() -> None:
    """Chamada UMA vez pelo lifespan. Se a carga falhar, a API sobe sem o modelo (503 só nesta rota)."""
    try:
        resumidor = carregar()
    except Exception as falha:  # noqa: BLE001 — fronteira entre o modelo e a API
        log.error(
            "Modelo de linguagem NÃO carregado — %s: %s. A rota /processar_texto vai responder 503.",
            type(falha).__name__,
            str(falha).splitlines()[0] if str(falha) else "",
        )
        return
    MODELOS["resumo"] = resumidor
    log.info("Modelo %s carregado em %.1f s.", resumidor.nome, resumidor.segundos_para_carregar)


def liberar_na_descida() -> None:
    MODELOS.clear()


@router.post(
    "/processar_texto",
    response_model=ResultadoResumo,
    responses={
        502: erro("O modelo devolveu um resumo vazio."),
        503: erro("O modelo de linguagem não foi carregado quando a API subiu."),
        504: erro("A geração do resumo passou do tempo limite."),
    },
    summary="Resumir um texto com o modelo de linguagem local",
    description=(
        "Gera um resumo em português com o modelo local. O campo `motor` diz qual modelo gerou o texto, "
        "e `aviso` lembra que o resumo precisa de revisão humana antes de ser usado como fato. "
        "Texto fora de 50 a 2.000 caracteres, ou com campo extra, responde 422."
    ),
)
def processar_texto(pedido: PedidoTexto) -> dict:
    resumidor: Resumidor | None = MODELOS.get("resumo")
    if resumidor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O modelo de linguagem não foi carregado quando a API subiu. "
                   "As outras rotas funcionam normalmente.",
        )

    futuro = _EXECUTOR.submit(resumir, pedido.texto, resumidor)
    try:
        resumo = futuro.result(timeout=TEMPO_LIMITE_SEGUNDOS)
    except concurrent.futures.TimeoutError as exc:
        log.warning("Resumo passou de %s s; a rota responde 504.", TEMPO_LIMITE_SEGUNDOS)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"A geração do resumo passou de {TEMPO_LIMITE_SEGUNDOS} s. Tente um texto mais curto; "
                   "se persistir, avise quem mantém a API.",
        ) from exc

    if not resumo.strip():
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="O modelo devolveu um resumo vazio. Tente reformular o texto; "
                   "se persistir, avise quem mantém a API.",
        )

    return {
        "tipo_analise": pedido.tipo_analise,
        "texto": pedido.texto,
        "resumo": resumo,
        "motor": resumidor.nome,
        "aviso": AVISO_RESUMO,
    }
