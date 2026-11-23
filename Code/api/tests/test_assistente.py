"""Testes do assistente de chat (TP5): Code/modeling/assistente.py e os contextos de Scripts/contextos.py.

A OpenAI é substituída por funções falsas e `requests.post` é simulado: nenhum teste usa rede nem a
chave. Cobrem a montagem do contexto de cada página, a memória (limite de trocas), a checagem de números
fora do contexto e o mapeamento dos erros da OpenAI (401, 429, 5xx, tempo esgotado, sem internet).
"""

import unittest
from unittest import mock

import pandas as pd
import requests

from Code.api import _paths  # noqa: F401  (põe Scripts/ no sys.path, para importar nucleo e contextos)
from Code.modeling import assistente
from Code.modeling.assistente import ErroAssistente
import contextos
from nucleo import INDICADOR_WB


def falso(texto: str):
    """Substituto de _chamar_openai: devolve `texto` e guarda as mensagens recebidas."""
    chamadas = []

    def chamar(mensagens, modelo, chave):
        chamadas.append(mensagens)
        return texto

    chamar.chamadas = chamadas
    return chamar


def resposta_http(status: int, corpo: dict | None = None) -> mock.Mock:
    resposta = mock.Mock()
    resposta.status_code = status
    resposta.json.return_value = corpo if corpo is not None else {}
    return resposta


CONTEXTO = "### Série\nFonte: Ipeadata\nano,% do PIB\n1995,16.81\n2025,11.77"


class MontagemDoContexto(unittest.TestCase):
    def test_tabela_tem_titulo_fonte_nota_e_csv(self) -> None:
        quadro = pd.DataFrame({"ano": [1995, 2025], "valor": [16.8123, None]})
        texto = assistente.tabela_para_contexto("Série", quadro, "Ipeadata", nota="Preços correntes.")
        self.assertEqual(
            texto.splitlines(),
            [
                "### Série",
                "Fonte: Ipeadata",
                "Nota: Preços correntes.",
                "Resumo calculado (primeiro, último, mínimo e máximo de cada coluna, com o ano):",
                "valor: primeiro 16.81 (1995); último 16.81 (1995); mínimo 16.81 (1995); máximo 16.81 (1995)",
                "ano,valor",
                "1995,16.81",
                "2025,sem dado",
            ],
        )

    def test_fontes_do_contexto_sem_repeticao_e_na_ordem(self) -> None:
        contexto = "### A\nFonte: IBGE\nano,v\n1,2\n\n### B\nFonte: World Bank\n\n### C\nFonte: IBGE"
        self.assertEqual(assistente.fontes_do_contexto(contexto), ["IBGE", "World Bank"])
        self.assertEqual(assistente.fontes_do_contexto("sem tabelas"), [])

    def test_resposta_traz_as_fontes_das_tabelas_sem_depender_do_modelo(self) -> None:
        r = assistente.responder("e agora?", [], CONTEXTO, falso("Em 1995 era 16.81."))
        self.assertEqual(r["fontes"], ["Ipeadata"])

    def test_tabela_sem_nota_nao_tem_linha_de_nota(self) -> None:
        texto = assistente.tabela_para_contexto("T", pd.DataFrame({"a": [1]}), "Fonte X")
        self.assertNotIn("Nota:", texto)

    def test_selecao_na_tela_vai_no_topo_quando_existe(self) -> None:
        com = assistente.montar_contexto(["### T"], "anos de 1995 a 2025")
        sem = assistente.montar_contexto(["### T"])
        self.assertTrue(com.startswith("SELEÇÃO NA TELA: anos de 1995 a 2025"))
        self.assertEqual(sem, "### T")


class ResumoTemporal(unittest.TestCase):
    def test_primeiro_ultimo_minimo_e_maximo_com_o_ano(self) -> None:
        quadro = pd.DataFrame({"ano": [2025, 2024, 2023], "Brasil": [11.0, 12.5, 9.0], "China": [None, 25.0, 24.0]})
        linhas = assistente.resumo_temporal(quadro)
        self.assertIn("Brasil: primeiro 9.00 (2023); último 11.00 (2025); mínimo 9.00 (2023); máximo 12.50 (2024)", linhas)
        self.assertIn("China: primeiro 24.00 (2023); último 25.00 (2024); mínimo 24.00 (2023); máximo 25.00 (2024)", linhas)

    def test_tabela_sem_coluna_ano_nao_tem_resumo(self) -> None:
        self.assertEqual(assistente.resumo_temporal(pd.DataFrame({"setor": ["a"], "valor": [1.0]})), [])
        self.assertNotIn("Resumo calculado", assistente.tabela_para_contexto("T", pd.DataFrame({"setor": ["a"]}), "F"))

    def test_coluna_sem_nenhum_valor_e_ignorada(self) -> None:
        quadro = pd.DataFrame({"ano": [2024, 2023], "Brasil": [1.0, 2.0], "EUA": [None, None]})
        texto = " ".join(assistente.resumo_temporal(quadro))
        self.assertIn("Brasil:", texto)
        self.assertNotIn("EUA:", texto)


class Memoria(unittest.TestCase):
    def setUp(self) -> None:
        patcher = mock.patch.object(assistente, "carregar_chave", return_value="chave-de-teste")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_so_as_ultimas_trocas_seguem_ao_modelo(self) -> None:
        historico = []
        for i in range(10):
            historico += [
                {"papel": "user", "conteudo": f"pergunta {i}"},
                {"papel": "assistant", "conteudo": f"resposta {i}"},
            ]
        chamar = falso("Ok.")
        assistente.responder("e em 2024?", historico, CONTEXTO, chamar)
        mensagens = chamar.chamadas[0]
        self.assertEqual(len(mensagens), 1 + 2 * assistente.MAX_TROCAS + 1)  # sistema + 6 trocas + pergunta
        self.assertEqual(mensagens[1]["content"], "pergunta 4")
        self.assertEqual(mensagens[-1]["content"], "e em 2024?")

    def test_o_contexto_da_pagina_vai_no_sistema_a_cada_turno(self) -> None:
        chamar = falso("Ok.")
        assistente.responder("oi?", [], CONTEXTO, chamar)
        sistema = chamar.chamadas[0][0]
        self.assertEqual(sistema["role"], "system")
        self.assertIn("1995,16.81", sistema["content"])
        self.assertIn("SOMENTE", sistema["content"])


class ChecagemDeNumeros(unittest.TestCase):
    def setUp(self) -> None:
        patcher = mock.patch.object(assistente, "carregar_chave", return_value="chave-de-teste")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_numeros_do_contexto_nao_sao_sinalizados(self) -> None:
        r = assistente.responder("e agora?", [], CONTEXTO, falso("Era 16.81% em 1995 e 11,77% em 2025."))
        self.assertEqual(r["numeros_nao_verificados"], [])

    def test_numero_inventado_e_sinalizado(self) -> None:
        r = assistente.responder("e agora?", [], CONTEXTO, falso("Caiu para 9,3% em 2025."))
        self.assertEqual(r["numeros_nao_verificados"], ["9,3"])

    def test_numero_dito_antes_pelo_assistente_nao_se_valida_sozinho(self) -> None:
        historico = [
            {"papel": "user", "conteudo": "Como está a indústria?"},
            {"papel": "assistant", "conteudo": "A participação caiu para 9,3% em 2025."},
        ]
        r = assistente.responder("Repita o valor.", historico, CONTEXTO, falso("Como disse, são 9,3%."))
        self.assertEqual(r["numeros_nao_verificados"], ["9,3"])

    def test_numero_em_formato_brasileiro_com_milhar_e_reconhecido(self) -> None:
        contexto = "periodo,valor\n4º trimestre 2025,3277790"
        r = assistente.responder("PIB?", [], contexto, falso("Foi de 3.277.790 milhões de R$."))
        self.assertEqual(r["numeros_nao_verificados"], [])

    def test_milhar_com_ponto_e_decimal_com_virgula_casa_com_o_contexto(self) -> None:
        """Resposta real: '712.716,0' (um grupo de milhar + vírgula decimal) é 712716.0 no contexto."""
        contexto = "setor,valor\nAgropecuária,712716.0\nTransformação,1549733.0"
        texto = "A transformação teve 1.549.733,0 milhões e a agropecuária, 712.716,0 milhões."
        r = assistente.responder("pesa mais?", [], contexto, falso(texto))
        self.assertEqual(r["numeros_nao_verificados"], [])

    def test_milhar_ambiguo_com_um_ponto_vale_nas_duas_leituras(self) -> None:
        r = assistente.responder("PIB?", [], "valor\n3277", falso("Foi de 3.277 milhões."))
        self.assertEqual(r["numeros_nao_verificados"], [])
        r = assistente.responder("PIB?", [], "valor\n3.277", falso("Foi de 3.277."))
        self.assertEqual(r["numeros_nao_verificados"], [])

    def test_numero_inventado_em_formato_brasileiro_continua_sinalizado(self) -> None:
        contexto = "setor,valor\nAgropecuária,712716.0"
        r = assistente.responder("e agora?", [], contexto, falso("A agropecuária teve 800.000,0 milhões."))
        self.assertEqual(r["numeros_nao_verificados"], ["800.000,0"])

    def test_valores_do_csv_separados_por_virgula_nao_se_fundem(self) -> None:
        """No CSV do contexto, '1995,16.81' são duas colunas (ano e valor), não o número 1995,16."""
        r = assistente.responder("e agora?", [], CONTEXTO, falso("Em 1995 era 16.81 e em 2025, 11.77."))
        self.assertEqual(r["numeros_nao_verificados"], [])

    def test_numero_que_o_usuario_escreveu_nao_e_sinalizado(self) -> None:
        r = assistente.responder("E se fosse 12,5%?", [], CONTEXTO, falso("Você citou 12,5%, que não está nos dados."))
        self.assertEqual(r["numeros_nao_verificados"], [])


class ContasConferidas(unittest.TestCase):
    """O modelo pode calcular se mostrar os valores usados: o código refaz a conta e só então aceita."""

    CONTEXTO = "ano,% do PIB\n2011,13.86\n2010,14.97"

    def setUp(self) -> None:
        patcher = mock.patch.object(assistente, "carregar_chave", return_value="chave-de-teste")
        patcher.start()
        self.addCleanup(patcher.stop)

    def responder(self, texto: str) -> dict:
        return assistente.responder("qual a diferença?", [], self.CONTEXTO, falso(texto))

    def test_diferenca_certa_com_os_dois_valores_e_aceita_e_mostrada(self) -> None:
        r = self.responder("Foram 14,97% em 2010 e 13,86% em 2011: queda de 1,11 p.p.")
        self.assertEqual(r["numeros_nao_verificados"], [])
        self.assertEqual(r["contas_conferidas"], ["1,11 = 14,97 − 13,86"])

    def test_diferenca_errada_e_sinalizada(self) -> None:
        r = self.responder("Foram 14,97% em 2010 e 13,86% em 2011: queda de 1,2 p.p.")
        self.assertEqual(r["numeros_nao_verificados"], ["1,2"])
        self.assertEqual(r["contas_conferidas"], [])

    def test_variacao_percentual(self) -> None:
        r = self.responder("De 14,97 para 13,86 a variação foi de -7,41%.")
        self.assertEqual(r["numeros_nao_verificados"], [])
        self.assertEqual(r["contas_conferidas"], ["7,41 = (13,86 − 14,97) / 14,97 × 100"])

    def test_soma_e_razao(self) -> None:
        r = self.responder("Somando 14,97 e 13,86 dá 28,83; e 14,97 / 13,86 é 1,08.")
        self.assertEqual(r["numeros_nao_verificados"], [])
        self.assertEqual(len(r["contas_conferidas"]), 2)

    def test_conta_sem_mostrar_os_valores_usados_nao_e_aceita(self) -> None:
        """Só o resultado, sem os dois valores na resposta: não há como conferir, então é sinalizado."""
        r = self.responder("A diferença é de 1,11 p.p.")
        self.assertEqual(r["numeros_nao_verificados"], ["1,11"])

    def test_numero_inventado_que_nao_e_conta_continua_sinalizado(self) -> None:
        r = self.responder("Foram 14,97% em 2010 e 13,86% em 2011, e chegou a 9,3% depois.")
        self.assertEqual(r["numeros_nao_verificados"], ["9,3"])

    def test_um_valor_so_nao_forma_conta(self) -> None:
        r = self.responder("Em 2010 foi 14,97%, ou seja, 0,31 p.p. a menos.")
        self.assertEqual(r["numeros_nao_verificados"], ["0,31"])


class ErrosDoAssistente(unittest.TestCase):
    def test_sem_chave_vira_503(self) -> None:
        with mock.patch.object(assistente, "carregar_chave", return_value=None):
            with self.assertRaises(ErroAssistente) as ctx:
                assistente.responder("oi?", [], CONTEXTO, falso("x"))
        self.assertEqual(ctx.exception.status, 503)

    def test_resposta_vazia_vira_502(self) -> None:
        with mock.patch.object(assistente, "carregar_chave", return_value="chave-de-teste"):
            with self.assertRaises(ErroAssistente) as ctx:
                assistente.responder("oi?", [], CONTEXTO, falso("   "))
        self.assertEqual(ctx.exception.status, 502)

    def test_erros_da_openai_viram_o_status_certo(self) -> None:
        casos = [
            (resposta_http(401), 502),
            (resposta_http(429), 429),
            (resposta_http(500), 502),
            (resposta_http(200, {"sem": "choices"}), 502),
        ]
        for resposta, esperado in casos:
            with mock.patch.object(requests, "post", return_value=resposta):
                with self.assertRaises(ErroAssistente) as ctx:
                    assistente._chamar_openai([{"role": "user", "content": "oi"}], "m", "chave")
            self.assertEqual(ctx.exception.status, esperado, resposta.status_code)

    def test_tempo_esgotado_vira_504_e_sem_internet_vira_502(self) -> None:
        for excecao, esperado in ((requests.Timeout(), 504), (requests.ConnectionError(), 502)):
            with mock.patch.object(requests, "post", side_effect=excecao):
                with self.assertRaises(ErroAssistente) as ctx:
                    assistente._chamar_openai([{"role": "user", "content": "oi"}], "m", "chave")
            self.assertEqual(ctx.exception.status, esperado)

    def test_resposta_valida_da_openai(self) -> None:
        corpo = {"choices": [{"message": {"content": "Olá."}}]}
        with mock.patch.object(requests, "post", return_value=resposta_http(200, corpo)):
            self.assertEqual(assistente._chamar_openai([{"role": "user", "content": "oi"}], "m", "chave"), "Olá.")

    def test_a_chave_nao_aparece_nas_mensagens_de_erro(self) -> None:
        with mock.patch.object(requests, "post", return_value=resposta_http(401)):
            with self.assertRaises(ErroAssistente) as ctx:
                assistente._chamar_openai([{"role": "user", "content": "oi"}], "m", "SEGREDO-123")
        self.assertNotIn("SEGREDO-123", ctx.exception.mensagem)


class ExibicaoDoChat(unittest.TestCase):
    def test_cifrao_e_escapado_para_o_streamlit_nao_ler_formula(self) -> None:
        import chat_pagina

        texto = "milhões de R$ 1.549.733 e de R$ 712.716"
        self.assertEqual(chat_pagina.texto_para_exibir(texto), "milhões de R\\$ 1.549.733 e de R\\$ 712.716")
        self.assertEqual(chat_pagina.texto_para_exibir("sem cifrão"), "sem cifrão")


def sidra_falso() -> tuple:
    """Quadros no formato da SIDRA (D2C/D2N período, D3C código, D3N nome, V valor) com números redondos."""
    def linhas(valores: dict) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"D2C": "202601", "D2N": "1º trimestre 2026", "D3C": cod, "D3N": f"setor {cod}", "V": str(v)}
                for cod, v in valores.items()
            ]
        )

    trimestral = linhas({"90707": 100, "90705": 90, "90706": 10, "90687": 10, "90691": 30, "90696": 50})
    subsetores = linhas({"90693": 15, "90692": 5, "90694": 6, "90695": 4})
    return trimestral, subsetores


def csv_enviado() -> pd.DataFrame:
    """CSV do DataBank em formato longo: dois indicadores, três países, anos com buracos."""
    linhas = []
    for indicador, nome, valores in (
        ("NV.AGR.TOTL.ZS", "Agropecuária (% PIB)", {("BRA", 2023): 5.0, ("BRA", 2024): 5.5}),
        (
            INDICADOR_WB,
            "Transformação (% PIB)",
            {("BRA", 2023): 12.0, ("BRA", 2024): 12.11, ("CHN", 2024): 24.84, ("USA", 2023): 10.5},
        ),
    ):
        for (codigo, ano), valor in valores.items():
            linhas.append(
                {
                    "indicator.id": indicador,
                    "indicator.value": nome,
                    "country.id": codigo,
                    "country.value": {"BRA": "Brazil", "CHN": "China", "USA": "United States"}[codigo],
                    "date": ano,
                    "value": valor,
                }
            )
    return pd.DataFrame(linhas)


class ContextosPorPagina(unittest.TestCase):
    def test_serie_traz_todos_os_anos_divididos_na_mudanca_de_1995(self) -> None:
        serie = pd.DataFrame({"ano": [1980, 1995, 2004, 2025], "valor": [33.2, 16.81, 17.79, 11.77]})
        contexto = contextos.contexto_serie(serie, (1995, 2025))
        for linha in ("1980,33.2", "1995,16.81", "2004,17.79", "2025,11.77"):
            self.assertIn(linha, contexto)
        self.assertEqual(contexto.count("### "), 1)  # uma tabela só: a busca de um ano fica num lugar
        self.assertIn("NÃO comparáveis entre antes e depois de 1995", contexto)
        self.assertIn("com o ano) de 1995 em diante:", contexto)
        self.assertIn("com o ano) antes de 1995", contexto)
        self.assertIn("SELEÇÃO NA TELA: o gráfico mostra os anos de 1995 a 2025", contexto)
        self.assertNotIn("SELEÇÃO NA TELA", contextos.contexto_serie(serie))

    def test_serie_vai_do_ano_mais_recente_ao_mais_antigo_com_resumo_por_parte(self) -> None:
        """O máximo 'desde 1995' (17.79) não se confunde com o de antes da mudança de referência (33.2)."""
        serie = pd.DataFrame({"ano": [1980, 1995, 2004, 2025], "valor": [33.2, 16.81, 17.79, 11.77]})
        contexto = contextos.contexto_serie(serie)
        self.assertLess(contexto.index("2025,11.77"), contexto.index("2004,17.79"))
        self.assertLess(contexto.index("2004,17.79"), contexto.index("1995,16.81"))
        self.assertIn("% do PIB: primeiro 16.81 (1995); último 11.77 (2025); mínimo 11.77 (2025); máximo 17.79 (2004)", contexto)
        self.assertIn("% do PIB: primeiro 33.20 (1980); último 33.20 (1980); mínimo 33.20 (1980); máximo 33.20 (1980)", contexto)

    def test_serie_sem_anos_antigos_nao_tem_tabela_de_antes_de_1995(self) -> None:
        serie = pd.DataFrame({"ano": [1995, 2025], "valor": [16.81, 11.77]})
        self.assertNotIn("antes de 1995", contextos.contexto_serie(serie))

    def test_panorama_traz_os_percentuais_do_painel_e_os_valores_trimestrais(self) -> None:
        trimestral, subsetores = sidra_falso()
        contexto = contextos.contexto_panorama(trimestral, subsetores)
        self.assertIn("Serviços,90696,50.0,50.0", contexto)  # 50 de 100 = 50% do PIB
        self.assertIn("Indústria,90691,30.0,30.0", contexto)
        self.assertIn("Transformação (dos quais: subsetor da indústria),90693,15.0,15.0", contexto)
        self.assertIn("Transformação,90693,15.0,50.0,15.0", contexto)  # 15 de 30 = 50% da indústria
        self.assertIn("1º trimestre 2026,setor 90691,30", contexto)  # valor trimestral, como veio da SIDRA
        self.assertIn("SELEÇÃO NA TELA: acumulado de 1º trimestre 2026 a 1º trimestre 2026", contexto)
        self.assertIn("não um quarto setor", contexto)

    def test_comparacao_tem_uma_tabela_por_indicador_com_paises_em_colunas(self) -> None:
        contexto = contextos.contexto_comparacao(csv_enviado(), "países: Brazil; anos de 2023 a 2024")
        self.assertIn("### Transformação (% PIB) (NV.IND.MANF.ZS)", contexto)
        self.assertIn("### Agropecuária (% PIB) (NV.AGR.TOTL.ZS)", contexto)
        self.assertIn("ano,Brazil,China,United States", contexto)
        self.assertIn("2023,12.0,sem dado,10.5", contexto)  # a China não tem 2023: escrito "sem dado"
        self.assertIn("2024,12.11,24.84,sem dado", contexto)  # os EUA não têm 2024
        self.assertLess(contexto.index("2024,12.11"), contexto.index("2023,12.0"))  # mais recente primeiro
        self.assertIn("Brazil: primeiro 12.00 (2023); último 12.11 (2024); mínimo 12.00 (2023); máximo 12.11 (2024)", contexto)
        self.assertIn("CSV enviado pelo usuário", contexto)
        self.assertIn("SELEÇÃO NA TELA: países: Brazil; anos de 2023 a 2024", contexto)

    def test_comparacao_poe_o_indicador_da_meta_primeiro(self) -> None:
        contexto = contextos.contexto_comparacao(csv_enviado())
        self.assertLess(contexto.index("NV.IND.MANF.ZS"), contexto.index("NV.AGR.TOTL.ZS"))

    def test_o_assistente_nao_recebe_dado_que_a_pagina_nao_mostra(self) -> None:
        """O contexto da comparação vem só do CSV enviado: nada de outro país ou ano aparece."""
        contexto = contextos.contexto_comparacao(csv_enviado())
        self.assertNotIn("Germany", contexto)
        self.assertNotIn("1960", contexto)


if __name__ == "__main__":
    unittest.main()
