"""Extrai título, autores, ano, periódico e resumo das referências sobre desindustrialização.

As páginas dos periódicos (SciELO, Springer, FGV) trazem os metadados no padrão citation_*.
As URLs vêm de Data/raw/referencias_urls.txt, uma por linha, curadas à mão.
Não lê PDFs nem o texto integral: só o resumo publicado na página do periódico.

Se o site responder com bloqueio (403, 429), o script para e não troca o identificador.
"""

import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "monitor-desindustrializacao/0.4 (projeto academico)"}
PAUSA_SEGUNDOS = 2
STATUS_PARAR = {403, 429}
RAIZ = Path(__file__).resolve().parents[2]
ENTRADA_URLS = RAIZ / "Data" / "raw" / "referencias_urls.txt"
SAIDA_CSV = RAIZ / "Data" / "raw" / "referencias_resumos.csv"
LICENCAS_POR_DOMINIO = {
    # Verificado na página do artigo: selo CC BY-NC 4.0.
    "scielo.br": "CC BY-NC 4.0 (selo na página do artigo)",
    # Página sem cláusula de reuso; 'Reprints and permissions' leva ao Copyright Clearance Center.
    # Ausência de cláusula não é permissão: reuso só com citação.
    "springer.com": "sem licença aberta; reuso sujeito a permissão do editor (Copyright Clearance Center); usar só com citação",
    # Página sem licença declarada.
    "fgv.br": "sem licença declarada na página; usar só com citação",
}


def licenca_do(url: str) -> str:
    for dominio, texto in LICENCAS_POR_DOMINIO.items():
        if dominio in url:
            return texto
    return "sem licença declarada; usar só com citação"


def limpar(texto: str) -> str:
    return " ".join(texto.split())


def ler_urls() -> list[str]:
    if not ENTRADA_URLS.exists():
        raise SystemExit(f"Lista de URLs não encontrada: {ENTRADA_URLS}")
    linhas = ENTRADA_URLS.read_text(encoding="utf-8").splitlines()
    return [linha.strip() for linha in linhas if linha.strip().startswith("http")]


def obter(url: str) -> requests.Response:
    resposta = requests.get(url, headers=HEADERS, timeout=60)
    if resposta.status_code in STATUS_PARAR:
        raise SystemExit(
            f"Site respondeu {resposta.status_code} em {url}. Parei sem contornar o bloqueio."
        )
    resposta.raise_for_status()
    return resposta


def meta_todas(sopa: BeautifulSoup, nome: str) -> list[str]:
    return [limpar(m["content"]) for m in sopa.find_all("meta", attrs={"name": nome}) if m.get("content")]


def meta_uma(sopa: BeautifulSoup, nome: str) -> str:
    valores = meta_todas(sopa, nome)
    return valores[0] if valores else ""


def achar_resumo(sopa: BeautifulSoup) -> str:
    """Prefere o resumo em português (DC.Description com lang=pt), depois citation_abstract,
    e por último o bloco com título 'Resumo' ou 'Abstract'."""
    for meta in sopa.find_all("meta", attrs={"name": "DC.Description"}):
        idioma_meta = meta.get("lang") or meta.get("xml:lang") or ""
        if idioma_meta.lower().startswith("pt") and meta.get("content"):
            return limpar(meta["content"])
    resumo = meta_uma(sopa, "citation_abstract")
    if resumo:
        return resumo
    for cabecalho in sopa.find_all(["h2", "h3", "h4", "strong", "div"]):
        texto = limpar(cabecalho.get_text(" ", strip=True))
        if texto.lower() in ("resumo", "abstract"):
            proximo = cabecalho.find_next("p")
            if proximo:
                return limpar(proximo.get_text(" ", strip=True))
    return ""


PERIODICO_PT = {
    # SciELO devolve o título em inglês; o nome em português segue Docs/Referencias.md.
    "10.1590/S0101-31572010000200003": "Revista de Economia Política",
    "10.1590/0101-31572021-3195": "Revista de Economia Política",
}

PALAVRAS_PT = (" de ", " que ", " da ", " do ", " para ", " uma ")
PALAVRAS_EN = (" the ", " of ", " and ", " which ", " with ", " is ")


def idioma_do_texto(texto: str) -> str:
    """Heurística simples: conta palavras funcionais em português e em inglês."""
    minusculo = f" {texto.lower()} "
    pt = sum(minusculo.count(p) for p in PALAVRAS_PT)
    en = sum(minusculo.count(p) for p in PALAVRAS_EN)
    if pt == en == 0:
        return "desconhecido"
    return "pt" if pt > en else "en"


def extrair_referencia(url: str, html: str) -> dict:
    sopa = BeautifulSoup(html, "html.parser")
    doi = meta_uma(sopa, "citation_doi")
    periodico = PERIODICO_PT.get(doi, meta_uma(sopa, "citation_journal_title"))
    resumo = achar_resumo(sopa)
    return {
        "url": url,
        "titulo": meta_uma(sopa, "citation_title"),
        "autores": "; ".join(meta_todas(sopa, "citation_author")),
        "ano": (meta_uma(sopa, "citation_publication_date") or meta_uma(sopa, "citation_date"))[:4],
        "periodico": periodico,
        "doi": doi,
        "resumo": resumo,
        "idioma_resumo": idioma_do_texto(resumo),
        "data_coleta": date.today().isoformat(),
        "licenca": licenca_do(url),
    }


def main() -> None:
    linhas = []
    for url in ler_urls():
        resposta = obter(url)
        resposta.encoding = resposta.apparent_encoding or "utf-8"
        referencia = extrair_referencia(url, resposta.text)
        if not referencia["resumo"]:
            raise SystemExit(f"Resumo não encontrado em {url}. A estrutura da página pode ter mudado.")
        linhas.append(referencia)
        time.sleep(PAUSA_SEGUNDOS)

    tabela = pd.DataFrame(linhas)
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(SAIDA_CSV, index=False, encoding="utf-8")
    print(f"{len(tabela)} referências gravadas em {SAIDA_CSV}")


if __name__ == "__main__":
    main()
