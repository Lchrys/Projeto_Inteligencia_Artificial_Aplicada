"""Teste de integração com o modelo de linguagem REAL (Qwen3-0.6B, na CPU).

Carrega o modelo como a API faz na subida (lifespan) e chama a rota de verdade.
É lento (alguns minutos), por isso só roda quando a variável RODAR_MODELO_REAL=1 está definida:

    RODAR_MODELO_REAL=1 python -m unittest Code.api.tests.test_modelo_real -v

O modelo precisa estar baixado (python Code/modeling/baixar_modelo.py). A carga é feita
com local_files_only, então o teste não usa internet.
"""

import os
import re
import time
import unittest

from fastapi.testclient import TestClient

from Code.api.main import app
from Code.api.models import AVISO_RESUMO
from Code.api.routers.texto import TEMPO_LIMITE_SEGUNDOS

TEXTO = (
    "A indústria de transformação perdeu participação no PIB brasileiro nas últimas "
    "décadas. Segundo a série do Ipeadata, a participação caiu de cerca de 25% do PIB "
    "em 1985 para pouco mais de 11% em 2025, o que caracteriza a desindustrialização."
)
PADRAO_NUMERO = re.compile(r"\d+(?:[.,]\d+)?")


@unittest.skipUnless(os.environ.get("RODAR_MODELO_REAL") == "1", "defina RODAR_MODELO_REAL=1 para rodar")
class RotaComModeloReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Entrar no `with` executa o lifespan: o modelo real é carregado uma vez, como na API.
        cls.contexto = TestClient(app, raise_server_exceptions=False)
        cls.cliente = cls.contexto.__enter__()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.contexto.__exit__(None, None, None)

    def test_modelo_carregou_na_subida(self) -> None:
        resposta = self.cliente.post("/processar_texto", json={"texto": TEXTO})
        self.assertNotEqual(resposta.status_code, 503, "o modelo não carregou na subida da API")

    def test_resumo_real_no_formato_da_resposta(self) -> None:
        inicio = time.perf_counter()
        resposta = self.cliente.post("/processar_texto", json={"texto": TEXTO})
        duracao = time.perf_counter() - inicio

        self.assertEqual(resposta.status_code, 200)
        corpo = resposta.json()
        self.assertEqual(
            sorted(corpo), ["aviso", "motor", "resumo", "texto", "tipo_analise"]
        )
        self.assertEqual(corpo["motor"], "Qwen/Qwen3-0.6B")
        self.assertEqual(corpo["aviso"], AVISO_RESUMO)
        self.assertTrue(corpo["resumo"].strip(), "o resumo veio vazio")
        self.assertFalse(
            corpo["resumo"].lower().startswith("resumo:"),
            "o rótulo 'Resumo:' não foi removido",
        )
        self.assertLess(duracao, TEMPO_LIMITE_SEGUNDOS, "a geração passou do limite")

    def test_resumo_nao_repete_so_o_titulo(self) -> None:
        resposta = self.cliente.post("/processar_texto", json={"texto": TEXTO})
        resumo = resposta.json()["resumo"]
        self.assertGreater(len(resumo), 80, "resumo curto demais: pode ter repetido só o título")

    def test_numeros_do_resumo_estao_no_texto(self) -> None:
        resposta = self.cliente.post("/processar_texto", json={"texto": TEXTO})
        resumo = resposta.json()["resumo"]
        numeros_resumo = {n.replace(",", ".") for n in PADRAO_NUMERO.findall(resumo)}
        numeros_texto = {n.replace(",", ".") for n in PADRAO_NUMERO.findall(TEXTO)}
        inventados = numeros_resumo - numeros_texto
        self.assertFalse(inventados, f"números que não estão no texto de origem: {inventados}")


if __name__ == "__main__":
    unittest.main()
