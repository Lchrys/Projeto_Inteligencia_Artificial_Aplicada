"""Extrai as metas do ODS 9 na página do Ipea e grava CSV/TXT em Data/raw."""

from datetime import date
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://www.ipea.gov.br/ods/ods9.html"
HEADERS = {"User-Agent": "monitor-desindustrializacao/0.2 (projeto academico)"}
RAIZ = Path(__file__).resolve().parents[2]
SAIDA_CSV = RAIZ / "Data" / "raw" / "ods9_metas.csv"
SAIDA_TXT = RAIZ / "Data" / "raw" / "ods9_corpus.txt"


def limpar(texto: str) -> str:
    return " ".join(texto.split())


def apos_rotulo(elemento, rotulo: str) -> str:
    texto = limpar(elemento.get_text(" ", strip=True))
    baixo = texto.lower()
    alvo = rotulo.lower()
    if baixo.startswith(alvo):
        return texto[len(rotulo) :].strip(" :.-")
    pos = baixo.find(alvo)
    if pos >= 0:
        return texto[pos + len(rotulo) :].strip(" :.-")
    return texto


def secao_h4(container, titulo: str) -> str:
    if container is None:
        return ""
    h4 = container.find("h4", string=lambda t: t and titulo.lower() in t.lower())
    if not h4:
        return ""
    partes = []
    for irmao in h4.next_siblings:
        if getattr(irmao, "name", None) == "h4":
            break
        if getattr(irmao, "name", None) == "p":
            partes.append(irmao.get_text(" ", strip=True))
    return limpar(" ".join(partes))


def extrair_metas(sopa: BeautifulSoup) -> list[dict]:
    linhas = []
    for paragrafo in sopa.select("div.txt_ods > p"):
        negrito = paragrafo.find("strong")
        if not negrito:
            continue
        titulo = negrito.get_text(strip=True)
        if not titulo.startswith("Meta 9"):
            continue
        codigo = titulo.replace("Meta", "", 1).strip()
        lista = paragrafo.find_next_sibling("ul")
        if lista is None:
            continue

        onu = brasil = indicadores = ""
        for item in lista.find_all("li", recursive=False):
            rotulo = item.find("strong")
            if rotulo is None:
                continue
            nome = rotulo.get_text(strip=True)
            if nome.startswith("Nações Unidas"):
                onu = apos_rotulo(item, "Nações Unidas")
            elif nome.startswith("Brasil"):
                link = item.find("a", class_="br")
                brasil = (
                    limpar(link.get_text(" ", strip=True))
                    if link
                    else apos_rotulo(item, "Brasil")
                )
            elif nome.startswith("Indicadores"):
                indicadores = apos_rotulo(item, "Indicadores")

        detalhe = lista.find("div", class_="mais_conteudo")
        linhas.append(
            {
                "meta": codigo,
                "onu": onu,
                "brasil": brasil,
                "justificativa": secao_h4(detalhe, "Justificativa"),
                "conceitos": secao_h4(detalhe, "Conceitos"),
                "indicadores": indicadores,
                "fonte": URL,
                "data_extracao": date.today().isoformat(),
            }
        )
    return linhas


def main() -> None:
    resposta = requests.get(URL, headers=HEADERS, timeout=30)
    resposta.raise_for_status()
    resposta.encoding = resposta.apparent_encoding or "latin-1"
    sopa = BeautifulSoup(resposta.text, "html.parser")
    linhas = extrair_metas(sopa)
    if not linhas:
        raise SystemExit("Nenhuma meta encontrada. A página pode ter mudado.")

    tabela = pd.DataFrame(linhas)
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(SAIDA_CSV, index=False, encoding="utf-8")

    corpus = "\n\n".join(
        " ".join(
            str(linha[campo])
            for campo in ("meta", "onu", "brasil", "justificativa", "conceitos", "indicadores")
            if linha[campo]
        )
        for linha in linhas
    )
    SAIDA_TXT.write_text(corpus, encoding="utf-8")
    print(f"{len(tabela)} metas gravadas em {SAIDA_CSV}")
    print(f"Corpus gravado em {SAIDA_TXT}")


if __name__ == "__main__":
    main()
