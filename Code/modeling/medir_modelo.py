"""Mede o modelo de resumo nos textos do corpus: tempo, memória e fidelidade numérica.

Banco de provas (montado aqui a partir do corpus já coletado):
  - justificativa de cada meta do ODS 9 com texto de pelo menos 150 caracteres;
  - resumo de cada referência de Data/raw/referencias_resumos.csv.

Fidelidade numérica: fração dos números do resumo que também aparecem no texto de origem.
Saída: Data/modeled/resumos_<modelo>.csv (um resumo por linha, com as medidas).

Rodar, da raiz do projeto, com o .venv ativo:
    python Code/modeling/medir_modelo.py
"""

import os
import re
import statistics
import time
from pathlib import Path

import pandas as pd
import psutil
import requests
from bs4 import BeautifulSoup

from resumidor import carregar, resumir

RAIZ = Path(__file__).resolve().parents[2]
META_CSV = RAIZ / "Data" / "raw" / "ods9_metas.csv"
REF_CSV = RAIZ / "Data" / "raw" / "referencias_resumos.csv"
MODELO = os.environ.get("MODELO_RESUMO", "Qwen/Qwen3-0.6B")
# Um arquivo por modelo, para uma medição não sobrescrever a outra.
# Ex.: Qwen/Qwen3-0.6B -> Data/modeled/resumos_qwen3_0_6b.csv
SAIDA = RAIZ / "Data" / "modeled" / f"resumos_{MODELO.split('/')[-1].lower().replace('.', '_').replace('-', '_')}.csv"
HEADERS_HTTP = {"User-Agent": "monitor-desindustrializacao/0.4 (projeto academico)"}
DOI_OREIRO = "10.1590/S0101-31572010000200003"
MIN_CARACTERES = 150
PADRAO_NUMERO = re.compile(r"\d+(?:[.,]\d+)?")
# Alertas automáticos: não decidem sozinhos, só apontam resumos para leitura humana.
MIN_CARACTERES_RESUMO = 80   # resumo menor que isso não é resumo
MAX_RAZAO_COPIA = 0.8        # resumo que quase repete o texto de origem


def alerta(caracteres_resumo: int, caracteres_origem: int) -> str:
    if caracteres_resumo < MIN_CARACTERES_RESUMO:
        return "curto"
    if caracteres_resumo / caracteres_origem > MAX_RAZAO_COPIA:
        return "copia_do_texto"
    return ""


def montar_banco() -> pd.DataFrame:
    metas = pd.read_csv(META_CSV)
    metas = metas[metas["justificativa"].fillna("").str.len() >= MIN_CARACTERES]
    linhas = [
        {"id": f"meta-{linha['meta']}", "origem": "ODS 9 (justificativa)", "texto": linha["justificativa"]}
        for _, linha in metas.iterrows()
    ]
    refs = pd.read_csv(REF_CSV)
    for _, linha in refs.iterrows():
        if linha["doi"] == DOI_OREIRO:
            # A introdução substitui o abstract em inglês. Fica só na memória: não é gravada no projeto.
            texto = introducao_scielo(linha["url"])
            origem = f"{linha['periodico']} ({linha['ano']}), introdução"
        else:
            texto = linha["resumo"]
            origem = f"{linha['periodico']} ({linha['ano']})"
        linhas.append({"id": f"ref-{linha['doi']}", "origem": origem, "texto": texto})
    return pd.DataFrame(linhas)


def introducao_scielo(url: str) -> str:
    """Lê os parágrafos entre 'INTRODUÇÃO' e o próximo título em maiúsculas, na página do SciELO."""
    resposta = requests.get(url, headers=HEADERS_HTTP, timeout=60)
    resposta.raise_for_status()
    sopa = BeautifulSoup(resposta.text, "html.parser")
    corpo = sopa.find("div", attrs={"data-anchor": "Text"})
    if corpo is None:
        raise SystemExit(f"Texto integral não encontrado em {url}.")
    paragrafos = [" ".join(p.get_text(" ", strip=True).split()) for p in corpo.find_all("p")]
    paragrafos = [p for p in paragrafos if p]

    def e_titulo(p: str) -> bool:
        return p == p.upper() and len(p) < 120 and any(c.isalpha() for c in p)

    inicio = next((i for i, p in enumerate(paragrafos) if p.upper() == "INTRODUÇÃO"), None)
    if inicio is None:
        raise SystemExit(f"Seção INTRODUÇÃO não encontrada em {url}.")
    trecho = []
    for p in paragrafos[inicio + 1:]:
        if e_titulo(p):
            break
        trecho.append(p)
    if not trecho:
        raise SystemExit(f"Introdução vazia em {url}.")
    return " ".join(trecho)


def numeros(texto: str) -> set[str]:
    return {n.replace(",", ".") for n in PADRAO_NUMERO.findall(str(texto))}


def fidelidade_numerica(resumo: str, origem: str) -> float | None:
    """Fração dos números do resumo que aparecem no texto de origem. None se o resumo não tem números."""
    nums_resumo = numeros(resumo)
    if not nums_resumo:
        return None
    return len(nums_resumo & numeros(origem)) / len(nums_resumo)


def main() -> None:
    banco = montar_banco()
    print(f"Banco de provas: {len(banco)} textos")

    processo = psutil.Process()
    memoria_antes = processo.memory_info().rss / 1024**3
    resumidor = carregar()
    memoria_modelo = processo.memory_info().rss / 1024**3
    print(f"{resumidor.nome} carregado em {resumidor.segundos_para_carregar} s "
          f"({memoria_modelo:.1f} GB de memória do processo; {memoria_antes:.1f} GB antes)")

    # Aquecimento: a primeira geração é mais lenta e não entra na medida.
    resumir(banco.loc[0, "texto"], resumidor)

    resultados = []
    for _, linha in banco.iterrows():
        inicio = time.perf_counter()
        resumo = resumir(linha["texto"], resumidor)
        segundos = round(time.perf_counter() - inicio, 1)
        memoria_pico = processo.memory_info().rss / 1024**3
        resultados.append({
            "id": linha["id"],
            "origem": linha["origem"],
            "caracteres_origem": len(linha["texto"]),
            "caracteres_resumo": len(resumo),
            "segundos": segundos,
            "memoria_gb": round(memoria_pico, 2),
            "fidelidade_numerica": fidelidade_numerica(resumo, linha["texto"]),
            "alerta": alerta(len(resumo), len(linha["texto"])),
            "resumo": resumo,
        })
        print(f"{linha['id']}: {segundos} s, {len(resumo)} caracteres")

    tabela = pd.DataFrame(resultados)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(SAIDA, index=False, encoding="utf-8")

    tempos = tabela["segundos"].tolist()
    com_numero = tabela["fidelidade_numerica"].dropna()
    print(f"\nTempo por texto: mediana {statistics.median(tempos)} s, pior {max(tempos)} s")
    print(f"Textos com número no resumo: {len(com_numero)} de {len(tabela)}")
    alertas = tabela.loc[tabela["alerta"].fillna("") != "", ["id", "alerta"]]
    print(f"Resumos com alerta: {len(alertas)} de {len(tabela)}")
    if len(alertas):
        print(alertas.to_string(index=False))
    if len(com_numero):
        print(f"Fidelidade numérica média: {com_numero.mean():.2f}")
    print(f"Medidas gravadas em {SAIDA}")


if __name__ == "__main__":
    main()
