"""Testes da rota POST /processar_texto, com o modelo substituído por um falso.

Sem o lifespan (TestClient sem `with`), o modelo real não é carregado: os testes
controlam MODELOS e a função de resumo diretamente. Cobrem os códigos 422, 503, 502,
504 e 500 da Etapa 4, além da resposta 200 com o formato da Etapa 3.
"""

import time
import unittest
from unittest import mock

from fastapi.testclient import TestClient

from Code.api.main import app
from Code.api.models import AVISO_RESUMO
from Code.api.routers import texto as rota_texto
from Code.modeling.resumidor import Resumidor

TEXTO_VALIDO = (
    "A indústria de transformação perdeu participação no PIB brasileiro nas últimas "
    "décadas, segundo a série do Ipeadata, que acompanha a participação setorial."
)


def modelo_falso() -> Resumidor:
    return Resumidor(nome="modelo-falso", tokenizador=None, modelo=None, segundos_para_carregar=0.0)


class RotaProcessarTexto(unittest.TestCase):
    def setUp(self) -> None:
        # raise_server_exceptions=False: o 500 chega como resposta HTTP, como para um cliente real.
        self.cliente = TestClient(app, raise_server_exceptions=False)
        rota_texto.MODELOS.clear()

    def tearDown(self) -> None:
        rota_texto.MODELOS.clear()

    def test_422_texto_curto(self) -> None:
        resposta = self.cliente.post("/processar_texto", json={"texto": "curto"})
        self.assertEqual(resposta.status_code, 422)

    def test_422_campo_extra(self) -> None:
        resposta = self.cliente.post(
            "/processar_texto", json={"texto": TEXTO_VALIDO, "campo_extra": 1}
        )
        self.assertEqual(resposta.status_code, 422)

    def test_503_modelo_nao_carregado(self) -> None:
        resposta = self.cliente.post("/processar_texto", json={"texto": TEXTO_VALIDO})
        self.assertEqual(resposta.status_code, 503)
        self.assertIn("detail", resposta.json())

    def test_200_formato_da_resposta(self) -> None:
        rota_texto.MODELOS["resumo"] = modelo_falso()
        with mock.patch.object(rota_texto, "resumir", return_value="Resumo de teste."):
            resposta = self.cliente.post(
                "/processar_texto", json={"texto": f"   {TEXTO_VALIDO}   "}
            )
        self.assertEqual(resposta.status_code, 200)
        corpo = resposta.json()
        self.assertEqual(
            sorted(corpo), ["aviso", "motor", "resumo", "texto", "tipo_analise"]
        )
        self.assertEqual(corpo["texto"], TEXTO_VALIDO)
        self.assertEqual(corpo["aviso"], AVISO_RESUMO)
        self.assertEqual(corpo["motor"], "modelo-falso")

    def test_502_resumo_vazio(self) -> None:
        rota_texto.MODELOS["resumo"] = modelo_falso()
        with mock.patch.object(rota_texto, "resumir", return_value="   "):
            resposta = self.cliente.post("/processar_texto", json={"texto": TEXTO_VALIDO})
        self.assertEqual(resposta.status_code, 502)
        self.assertIn("vazio", resposta.json()["detail"])

    def test_504_tempo_excedido(self) -> None:
        rota_texto.MODELOS["resumo"] = modelo_falso()

        def geracao_lenta(_texto, _resumidor):
            time.sleep(2)
            return "tarde demais"

        with mock.patch.object(rota_texto, "resumir", side_effect=geracao_lenta), \
             mock.patch.object(rota_texto, "TEMPO_LIMITE_SEGUNDOS", 0.2):
            resposta = self.cliente.post("/processar_texto", json={"texto": TEXTO_VALIDO})
        self.assertEqual(resposta.status_code, 504)
        self.assertIn("passou", resposta.json()["detail"])

    def test_500_erro_inesperado_com_codigo(self) -> None:
        rota_texto.MODELOS["resumo"] = modelo_falso()
        with mock.patch.object(rota_texto, "resumir", side_effect=RuntimeError("falha interna")):
            resposta = self.cliente.post("/processar_texto", json={"texto": TEXTO_VALIDO})
        self.assertEqual(resposta.status_code, 500)
        detalhe = resposta.json()["detail"]
        self.assertIn("código", detalhe)
        self.assertNotIn("falha interna", detalhe)  # o cliente não vê o traceback nem a mensagem crua


if __name__ == "__main__":
    unittest.main()
