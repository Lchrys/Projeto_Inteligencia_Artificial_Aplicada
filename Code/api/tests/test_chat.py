"""Testes da rota POST /chat (TP5), do cliente do painel, da mensagem do chat quando a API falha e da subida
automática da API junto com o painel.

Nenhum teste usa rede nem a chave de verdade: a OpenAI é simulada (`requests.post`) ou o assistente é
substituído por um falso. Cobrem a resposta 200, os códigos 422, 429, 502, 503 e 504, o cliente
(`conversar`) e a mensagem do chat quando a API está fora do ar ou devolve erro.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import requests
from fastapi.testclient import TestClient

from Code.api import _paths  # noqa: F401  (põe Scripts/ no sys.path, para importar cliente_api e chat_pagina)
from Code.api.main import app
from Code.api.models import MAX_CARACTERES_PERGUNTA, MAX_MENSAGENS_HISTORICO
from Code.modeling import assistente
from Code.modeling.assistente import ErroAssistente
import chat_pagina
import cliente_api

CONTEXTO = "### Série\nFonte: Ipeadata\nano,% do PIB\n2025,11.77\n2010,14.97\n1995,16.81"
PEDIDO = {
    "pergunta": "E em 2010?",
    "historico": [
        {"papel": "user", "conteudo": "Qual o valor em 1995?"},
        {"papel": "assistant", "conteudo": "Em 1995 foi 16,81%."},
    ],
    "contexto": CONTEXTO,
}
RESULTADO = {
    "resposta": "Em 2010 foi 14,97%.",
    "motor": "modelo-falso",
    "numeros_nao_verificados": [],
    "contas_conferidas": [],
    "fontes": ["Ipeadata"],
    "aviso": assistente.AVISO_CHAT,
}


def resposta_http(status: int, corpo=None, texto: str = "") -> mock.Mock:
    resposta = mock.Mock()
    resposta.status_code = status
    resposta.text = texto
    if corpo is None:
        resposta.json.side_effect = ValueError("sem JSON")
    else:
        resposta.json.return_value = corpo
    return resposta


class RotaChat(unittest.TestCase):
    def setUp(self) -> None:
        # raise_server_exceptions=False: o 500 chega como resposta HTTP, como para um cliente real.
        self.cliente = TestClient(app, raise_server_exceptions=False)

    def test_200_devolve_o_formato_prometido(self) -> None:
        with mock.patch.object(assistente, "responder", return_value=dict(RESULTADO)) as falso:
            resposta = self.cliente.post("/chat", json=PEDIDO)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), RESULTADO)
        falso.assert_called_once_with("E em 2010?", PEDIDO["historico"], CONTEXTO)

    def test_pergunta_sai_sem_espacos_nas_pontas(self) -> None:
        with mock.patch.object(assistente, "responder", return_value=dict(RESULTADO)) as falso:
            self.cliente.post("/chat", json={**PEDIDO, "pergunta": "  E em 2010?  "})
        self.assertEqual(falso.call_args.args[0], "E em 2010?")

    def test_historico_e_opcional(self) -> None:
        with mock.patch.object(assistente, "responder", return_value=dict(RESULTADO)) as falso:
            resposta = self.cliente.post("/chat", json={"pergunta": "Oi?", "contexto": CONTEXTO})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(falso.call_args.args[1], [])

    def test_de_ponta_a_ponta_com_a_openai_simulada(self) -> None:
        openai = resposta_http(200, {"choices": [{"message": {"content": "Em 2010 foi 14,97%."}}]})
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "chave-de-teste"}):
            with mock.patch.object(assistente.requests, "post", return_value=openai):
                resposta = self.cliente.post("/chat", json=PEDIDO)
        corpo = resposta.json()
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(corpo["resposta"], "Em 2010 foi 14,97%.")
        self.assertEqual(corpo["numeros_nao_verificados"], [])
        self.assertEqual(corpo["fontes"], ["Ipeadata"])

    def test_numero_fora_das_tabelas_vem_sinalizado(self) -> None:
        openai = resposta_http(200, {"choices": [{"message": {"content": "Em 2010 foi 99,99%."}}]})
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "chave-de-teste"}):
            with mock.patch.object(assistente.requests, "post", return_value=openai):
                corpo = self.cliente.post("/chat", json=PEDIDO).json()
        self.assertIn("99,99", corpo["numeros_nao_verificados"])

    def test_erros_do_assistente_viram_o_mesmo_status_http(self) -> None:
        for status in (429, 502, 503, 504):
            falha = ErroAssistente(status, f"mensagem {status}")
            with mock.patch.object(assistente, "responder", side_effect=falha):
                resposta = self.cliente.post("/chat", json=PEDIDO)
            self.assertEqual(resposta.status_code, status)
            self.assertEqual(resposta.json(), {"detail": f"mensagem {status}"})

    def test_503_sem_chave_de_verdade(self) -> None:
        with mock.patch.object(assistente, "carregar_chave", return_value=None):
            resposta = self.cliente.post("/chat", json=PEDIDO)
        self.assertEqual(resposta.status_code, 503)
        self.assertIn("Chave da OpenAI não configurada", resposta.json()["detail"])

    def test_422_entrada_fora_do_contrato(self) -> None:
        longo = "x" * (MAX_CARACTERES_PERGUNTA + 1)
        muitas = [{"papel": "user", "conteudo": "oi"}] * (MAX_MENSAGENS_HISTORICO + 1)
        casos = {
            "pergunta vazia": {**PEDIDO, "pergunta": ""},
            "pergunta só com espaços": {**PEDIDO, "pergunta": "   "},
            "pergunta longa": {**PEDIDO, "pergunta": longo},
            "sem contexto": {**PEDIDO, "contexto": ""},
            "papel inválido": {**PEDIDO, "historico": [{"papel": "system", "conteudo": "oi"}]},
            "fala vazia": {**PEDIDO, "historico": [{"papel": "user", "conteudo": ""}]},
            "histórico longo": {**PEDIDO, "historico": muitas},
            "campo extra": {**PEDIDO, "modelo": "gpt-x"},
            "campo extra na fala": {**PEDIDO, "historico": [{"papel": "user", "conteudo": "oi", "x": 1}]},
        }
        for nome, corpo in casos.items():
            with mock.patch.object(assistente, "responder", return_value=dict(RESULTADO)) as falso:
                resposta = self.cliente.post("/chat", json=corpo)
            self.assertEqual(resposta.status_code, 422, nome)
            falso.assert_not_called()

    def test_500_inesperado_vira_json_com_codigo(self) -> None:
        with mock.patch.object(assistente, "responder", side_effect=RuntimeError("falha interna")):
            resposta = self.cliente.post("/chat", json=PEDIDO)
        self.assertEqual(resposta.status_code, 500)
        self.assertNotIn("falha interna", resposta.text)

    def test_docs_listam_a_rota_e_os_erros(self) -> None:
        post = app.openapi()["paths"]["/chat"]["post"]
        self.assertEqual({"200", "422", "429", "500", "502", "503", "504"} - set(post["responses"]), set())


class ClienteConversar(unittest.TestCase):
    def test_sem_api_levanta_apiforadoar(self) -> None:
        with mock.patch.object(cliente_api.requests, "post", side_effect=requests.ConnectionError()):
            with self.assertRaises(cliente_api.ApiForaDoAr):
                cliente_api.conversar("oi?", [], CONTEXTO)

    def test_timeout_do_cliente_tambem_e_api_fora_do_ar(self) -> None:
        with mock.patch.object(cliente_api.requests, "post", side_effect=requests.Timeout()):
            with self.assertRaises(cliente_api.ApiForaDoAr):
                cliente_api.conversar("oi?", [], CONTEXTO)

    def test_200_devolve_o_corpo_e_envia_pergunta_historico_e_contexto(self) -> None:
        with mock.patch.object(cliente_api.requests, "post", return_value=resposta_http(200, RESULTADO)) as post:
            resultado = cliente_api.conversar("E em 2010?", PEDIDO["historico"], CONTEXTO)
        self.assertEqual(resultado, RESULTADO)
        self.assertEqual(post.call_args.kwargs["json"], PEDIDO)
        self.assertTrue(post.call_args.args[0].endswith("/chat"))

    def test_erro_levanta_erroapi_com_status_e_frase(self) -> None:
        resposta = resposta_http(429, {"detail": "Limite de uso esgotado."})
        with mock.patch.object(cliente_api.requests, "post", return_value=resposta):
            with self.assertRaises(cliente_api.ErroApi) as ctx:
                cliente_api.conversar("oi?", [], CONTEXTO)
        self.assertEqual((ctx.exception.status, ctx.exception.detalhe), (429, "Limite de uso esgotado."))

    def test_422_com_lista_vira_uma_frase(self) -> None:
        corpo = {"detail": [{"loc": ["body", "pergunta"], "msg": "String should have at most 500 characters"}]}
        with mock.patch.object(cliente_api.requests, "post", return_value=resposta_http(422, corpo)):
            with self.assertRaises(cliente_api.ErroApi) as ctx:
                cliente_api.conversar("oi?", [], CONTEXTO)
        self.assertEqual(ctx.exception.detalhe, "String should have at most 500 characters")

    def test_erro_sem_json_usa_o_texto(self) -> None:
        with mock.patch.object(cliente_api.requests, "post", return_value=resposta_http(502, texto="Bad Gateway")):
            with self.assertRaises(cliente_api.ErroApi) as ctx:
                cliente_api.conversar("oi?", [], CONTEXTO)
        self.assertEqual(ctx.exception.detalhe, "Bad Gateway")


class MensagemDoChat(unittest.TestCase):
    def test_erro_da_api_mostra_a_frase_do_detail(self) -> None:
        falha = cliente_api.ErroApi(429, "Limite de uso esgotado.")
        self.assertEqual(chat_pagina.mensagem_de_erro(falha), "Não consegui responder: Limite de uso esgotado.")

    def test_api_fora_do_ar_mostra_o_comando_para_subi_la(self) -> None:
        mensagem = chat_pagina.mensagem_de_erro(cliente_api.ApiForaDoAr())
        self.assertIn("a API não está no ar", mensagem)
        self.assertIn(cliente_api.COMANDO_UVICORN, mensagem)

    def test_o_chat_nao_chama_o_assistente_direto(self) -> None:
        # Só a API fala com a OpenAI: o módulo da página nem importa o assistente.
        self.assertFalse(hasattr(chat_pagina, "assistente"))


class SubidaAutomaticaDaApi(unittest.TestCase):
    """`subir_api_se_preciso`: o painel sobe a API junto, só se ela for local e ainda não estiver no ar."""

    def setUp(self) -> None:
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.disponivel = mock.Mock()  # no lugar do cache do Streamlit
        for alvo, valor in (
            ("LOG_API", Path(pasta.name) / "api.log"),
            ("api_disponivel", self.disponivel),
            ("url_api", lambda: "http://127.0.0.1:8000"),
        ):
            patcher = mock.patch.object(cliente_api, alvo, valor)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.sono = mock.patch.object(cliente_api.time, "sleep").start()
        self.saida = mock.patch.object(cliente_api.atexit, "register").start()
        self.addCleanup(mock.patch.stopall)

    def test_api_remota_nao_e_subida(self) -> None:
        with mock.patch.object(cliente_api, "url_api", lambda: "https://api.exemplo.com"):
            with mock.patch.object(cliente_api.subprocess, "Popen") as popen:
                self.assertIsNone(cliente_api.subir_api_se_preciso())
        popen.assert_not_called()

    def test_api_que_ja_esta_no_ar_nao_e_subida_de_novo(self) -> None:
        with mock.patch.object(cliente_api, "_api_responde", return_value=True):
            with mock.patch.object(cliente_api.subprocess, "Popen") as popen:
                self.assertIsNone(cliente_api.subir_api_se_preciso())
        popen.assert_not_called()

    def test_sobe_a_api_espera_ela_responder_e_a_encerra_com_o_painel(self) -> None:
        processo = mock.Mock()
        processo.poll.return_value = None
        with mock.patch.object(cliente_api, "_api_responde", side_effect=[False, False, True]):
            with mock.patch.object(cliente_api.subprocess, "Popen", return_value=processo) as popen:
                resultado = cliente_api.subir_api_se_preciso()
        self.assertIs(resultado, processo)
        comando = popen.call_args.args[0]
        self.assertEqual(comando[:3], [sys.executable, "-m", "uvicorn"])
        self.assertIn("Code.api.main:app", comando)
        self.assertEqual(comando[comando.index("--port") + 1], "8000")
        self.assertEqual(popen.call_args.kwargs["cwd"], cliente_api.RAIZ)
        self.saida.assert_called_once_with(processo.terminate)
        self.disponivel.clear.assert_called_once()

    def test_api_que_morre_na_subida_devolve_none(self) -> None:
        processo = mock.Mock()
        processo.poll.return_value = 1  # encerrou na hora: por exemplo, a porta estava ocupada
        with mock.patch.object(cliente_api, "_api_responde", return_value=False):
            with mock.patch.object(cliente_api.subprocess, "Popen", return_value=processo):
                self.assertIsNone(cliente_api.subir_api_se_preciso())

    def test_o_comando_mostrado_ao_usuario_usa_o_python_do_venv(self) -> None:
        self.assertTrue(cliente_api.COMANDO_UVICORN.startswith(".venv"))
        self.assertIn("uvicorn Code.api.main:app", cliente_api.COMANDO_UVICORN)


if __name__ == "__main__":
    unittest.main()
