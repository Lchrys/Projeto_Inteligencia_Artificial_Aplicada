"""Consulta a API FastAPI local e cai na leitura direta se ela não responder.

Ao abrir o painel, `garantir_api` sobe a API junto, se ela for local e ainda não estiver no ar.
"""

import atexit
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd
import requests
import streamlit as st

PADRAO_API = "http://127.0.0.1:8000"
COMANDO_UVICORN = r".venv\Scripts\python.exe -m uvicorn Code.api.main:app --reload"
RAIZ = Path(__file__).resolve().parents[1]
# Saída da API que o painel sobe sozinho (para ver o motivo se ela não subir).
LOG_API = Path(tempfile.gettempdir()) / "monitor_api.log"
HOSTS_LOCAIS = ("127.0.0.1", "localhost")
# A API carrega o modelo local na subida (cerca de 20 s); a folga cobre uma máquina mais lenta.
ESPERA_SUBIDA_API = 90
ORIGEM_API = "API FastAPI"
ORIGEM_DIRETA = "leitura direta"
# A OpenAI tem 60 s de limite (assistente.py); a folga cobre a ida e a volta pela API.
TEMPO_LIMITE_CHAT = 90


def url_api() -> str:
    try:
        valor = st.secrets.get("API_URL", PADRAO_API)
    except Exception:
        valor = PADRAO_API
    return str(valor).rstrip("/")


def _api_responde() -> bool:
    """Pergunta a /saude agora, sem cache."""
    try:
        resposta = requests.get(f"{url_api()}/saude", timeout=2)
        return resposta.ok and resposta.json().get("status") == "ok"
    except (requests.RequestException, ValueError):
        return False


@st.cache_data(ttl=30)
def api_disponivel() -> bool:
    return _api_responde()


def subir_api_se_preciso() -> subprocess.Popen | None:
    """Sobe a API FastAPI junto com o painel, se ela for local e ainda não estiver no ar.

    Devolve o processo criado, ou None se nada foi feito (API remota, API já no ar) ou se a API não subiu
    (a porta pode estar ocupada; o motivo fica em LOG_API). Espera até ESPERA_SUBIDA_API segundos pela
    resposta de /saude. O processo termina quando o painel termina; se o painel for encerrado à força, a
    API pode continuar rodando, e a próxima abertura do painel a reaproveita.
    """
    url = urlparse(url_api())
    if url.hostname not in HOSTS_LOCAIS or _api_responde():
        return None
    with open(LOG_API, "ab") as log:  # o processo filho fica com a própria cópia do arquivo
        processo = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "Code.api.main:app", "--host", "127.0.0.1", "--port", str(url.port or 80)],
            cwd=RAIZ,
            stdout=log,
            stderr=log,
        )
    atexit.register(processo.terminate)
    for _ in range(ESPERA_SUBIDA_API):
        if processo.poll() is not None or _api_responde():
            break
        time.sleep(1)
    api_disponivel.clear()
    return processo if processo.poll() is None else None


# Uma vez por servidor do painel: as páginas chamam `garantir_api()` sem custo depois da primeira.
garantir_api = st.cache_resource(show_spinner=False)(subir_api_se_preciso)


@st.cache_data(ttl=3600, show_spinner="Consultando a API...")
def _consultar_api(caminho: str, params_chave: tuple) -> dict:
    params = dict(params_chave) if params_chave else None
    resposta = requests.get(
        f"{url_api()}{caminho}", params=params, timeout=30
    )
    resposta.raise_for_status()
    return resposta.json()


def enviar_arquivo(
    caminho: str, nome: str, conteudo: bytes
) -> dict | None:
    """POST multipart. Devolve None se a API não responder; ValueError em 4xx."""
    try:
        resposta = requests.post(
            f"{url_api()}{caminho}",
            files={"arquivo": (nome, conteudo, "text/csv")},
            timeout=30,
        )
    except requests.RequestException:
        return None
    if resposta.status_code >= 400:
        detalhe = resposta.text
        try:
            corpo = resposta.json()
            detalhe = str(corpo.get("detail", detalhe))
        except ValueError:
            pass
        raise ValueError(detalhe)
    return resposta.json()


def analisar_texto(texto: str) -> dict | None:
    """POST /processar_texto (resumo com o modelo local). Devolve None se a API não responder.

    Em 4xx e 5xx levanta ValueError com a mensagem do `detail`. O 422 do FastAPI
    traz uma lista de problemas; ela vira uma frase.
    """
    try:
        resposta = requests.post(
            f"{url_api()}/processar_texto",
            json={"texto": texto},
            timeout=180,
        )
    except requests.RequestException:
        return None
    if resposta.status_code >= 400:
        try:
            detalhe = resposta.json().get("detail", resposta.text)
        except ValueError:
            detalhe = resposta.text
        if isinstance(detalhe, list):
            detalhe = " ".join(
                str(item.get("msg", item)) if isinstance(item, dict) else str(item)
                for item in detalhe
            )
        raise ValueError(str(detalhe))
    return resposta.json()


class ErroApi(Exception):
    """A API respondeu com erro (4xx ou 5xx): guarda o status e a frase do `detail`."""

    def __init__(self, status: int, detalhe: str):
        super().__init__(detalhe)
        self.status = status
        self.detalhe = detalhe


class ApiForaDoAr(Exception):
    """A API não respondeu: está fora do ar ou a conexão caiu."""


def conversar(pergunta: str, historico: list[dict], contexto: str) -> dict:
    """POST /chat (chat com memória). O chat só funciona pela API.

    Levanta ApiForaDoAr se a API não responder. Em 4xx e 5xx levanta ErroApi com o status e a frase do
    `detail`; o 422 do FastAPI traz uma lista de problemas, que vira uma frase. O histórico vai inteiro
    a cada pedido: a API não guarda conversa.
    """
    try:
        resposta = requests.post(
            f"{url_api()}/chat",
            json={"pergunta": pergunta, "historico": historico, "contexto": contexto},
            timeout=TEMPO_LIMITE_CHAT,
        )
    except requests.RequestException as exc:
        raise ApiForaDoAr() from exc
    if resposta.status_code >= 400:
        try:
            detalhe = resposta.json().get("detail", resposta.text)
        except ValueError:
            detalhe = resposta.text
        if isinstance(detalhe, list):
            detalhe = " ".join(
                str(item.get("msg", item)) if isinstance(item, dict) else str(item)
                for item in detalhe
            )
        raise ErroApi(resposta.status_code, str(detalhe))
    return resposta.json()


def _params_chave(params: dict | None) -> tuple:
    if not params:
        return ()
    limpos = {chave: valor for chave, valor in params.items() if valor is not None}
    return tuple(sorted(limpos.items()))


def obter(
    caminho: str,
    params: dict | None = None,
    fallback: Callable[[], Any] | None = None,
) -> tuple[Any, str]:
    """Devolve (dados, origem). Origem é 'API FastAPI' ou 'leitura direta'."""
    if api_disponivel():
        try:
            return _consultar_api(caminho, _params_chave(params)), ORIGEM_API
        except (requests.RequestException, ValueError):
            pass
    if fallback is None:
        return None, ORIGEM_DIRETA
    return fallback(), ORIGEM_DIRETA


def quadro(dados: Any) -> pd.DataFrame:
    if isinstance(dados, pd.DataFrame):
        return dados
    if not isinstance(dados, dict):
        return pd.DataFrame()
    linhas = dados.get("dados")
    if not linhas:
        return pd.DataFrame()
    return pd.DataFrame(linhas)


def legenda_origem(origem: str) -> None:
    st.caption(f"Origem: {origem}")
