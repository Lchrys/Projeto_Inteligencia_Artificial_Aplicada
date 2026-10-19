"""Consulta a API FastAPI local e cai na leitura direta se ela não responder."""

from collections.abc import Callable
from typing import Any

import pandas as pd
import requests
import streamlit as st

PADRAO_API = "http://127.0.0.1:8000"
COMANDO_UVICORN = "uvicorn Code.api.main:app --reload"
ORIGEM_API = "API FastAPI"
ORIGEM_DIRETA = "leitura direta"


def url_api() -> str:
    try:
        valor = st.secrets.get("API_URL", PADRAO_API)
    except Exception:
        valor = PADRAO_API
    return str(valor).rstrip("/")


@st.cache_data(ttl=30)
def api_disponivel() -> bool:
    try:
        resposta = requests.get(f"{url_api()}/saude", timeout=2)
        return resposta.ok and resposta.json().get("status") == "ok"
    except (requests.RequestException, ValueError):
        return False


@st.cache_data(ttl=3600, show_spinner="Consultando a API...")
def _consultar_api(caminho: str, params_chave: tuple) -> dict:
    params = dict(params_chave) if params_chave else None
    resposta = requests.get(
        f"{url_api()}{caminho}", params=params, timeout=30
    )
    resposta.raise_for_status()
    return resposta.json()


def limpar_cache_api() -> None:
    _consultar_api.clear()


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
