from collections import Counter
from datetime import date
from pathlib import Path
import re

import pandas as pd
import requests
import ipeadatapy as ipea
import streamlit as st
from wordcloud import WordCloud

CODIGO_IPEA = "SCN10_VAITY10"
INDICADOR_WB = "NV.IND.MANF.ZS"
ANO_QUEBRA_SCN = 1995
INDICADORES_WB = {
    "NV.AGR.TOTL.ZS": "Agropecuária (% PIB)",
    "NV.IND.TOTL.ZS": "Indústria total (% PIB)",
    "NV.IND.MANF.ZS": "Transformação (% PIB)",
    "NV.SRV.TOTL.ZS": "Serviços (% PIB)",
    "NV.IND.MANF.KD.ZG": "Crescimento da transformação (%)",
    "TX.VAL.TECH.MF.ZS": "Exportações de alta tecnologia (% manufaturadas)",
}
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "monitor-desindustrializacao/0.1",
}
URL_SIDRA_TRIMESTRAL = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/1846/periodos/-1/"
    "variaveis/all?localidades=N1[1]&classificacao=11255[90707,90687,90691,90696]"
)
URL_SIDRA_SUBSETORES = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/1846/periodos/-1/"
    "variaveis/all?localidades=N1[1]&classificacao=11255[90693,90692,90694,90695]"
)
RAIZ = Path(__file__).resolve().parents[1]
ARQ_ODS9_CSV = RAIZ / "Data" / "raw" / "ods9_metas.csv"
ARQ_ODS9_TXT = RAIZ / "Data" / "raw" / "ods9_corpus.txt"
ARQ_WB_CSV = RAIZ / "Data" / "raw" / "world_bank_setorial.csv"
COLUNAS_DATABANK = ("Country Name", "Country Code", "Series Name", "Series Code")
DATA_CONSULTA = date.today().isoformat()
STOPWORDS_BASE = frozenset(
    {
        "a", "o", "as", "os", "um", "uma", "de", "da", "do", "das", "dos",
        "e", "em", "no", "na", "nos", "nas", "para", "por", "com", "sem",
        "que", "se", "ao", "aos", "à", "às", "ou", "como", "mais", "são",
        "ser", "foi", "pelo", "pela", "pelos", "pelas", "este", "esta",
        "sua", "seu", "suas", "seus", "entre", "até", "não", "também",
        "já", "ainda", "muito", "sobre", "outros", "outras", "esse",
        "essa", "forma", "meio", "além",
    }
)
STOPWORDS_CORPUS = STOPWORDS_BASE | frozenset(
    {
        "meta", "metas", "indicador", "indicadores", "brasil",
        "país", "países",
    }
)


@st.cache_data(ttl=3600, show_spinner="Consultando Ipeadata...")
def amostra_ipeadata(codigo: str) -> pd.DataFrame:
    return ipea.timeseries(codigo).reset_index()


def achatar_agregados(payload: list, rotulos_periodo: dict) -> pd.DataFrame:
    linhas = []
    for variavel in payload:
        for resultado in variavel.get("resultados", []):
            categorias = resultado.get("classificacoes", [{}])[0].get(
                "categoria", {}
            )
            d3c, d3n = next(iter(categorias.items()), ("", ""))
            for serie in resultado.get("series", []):
                local = serie.get("localidade", {})
                nivel = local.get("nivel", {})
                for periodo, valor in serie.get("serie", {}).items():
                    linhas.append(
                        {
                            "NC": nivel.get("id", ""),
                            "NN": nivel.get("nome", ""),
                            "MN": variavel.get("unidade", ""),
                            "D1C": local.get("id", ""),
                            "D1N": local.get("nome", ""),
                            "D2C": periodo,
                            "D2N": rotulos_periodo.get(periodo, periodo),
                            "D3C": d3c,
                            "D3N": d3n,
                            "V": valor,
                        }
                    )
    return pd.DataFrame(linhas)


@st.cache_data(ttl=3600, show_spinner="Consultando SIDRA...")
def rotulos_periodos_sidra(agregado: str = "1846") -> dict:
    resposta = requests.get(
        f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos",
        headers=HEADERS,
        timeout=30,
    )
    resposta.raise_for_status()
    return {item["id"]: item["literals"][0] for item in resposta.json()}


@st.cache_data(ttl=3600, show_spinner="Consultando SIDRA...")
def amostra_sidra(url: str) -> pd.DataFrame:
    resposta = requests.get(url, headers=HEADERS, timeout=30)
    resposta.raise_for_status()
    return achatar_agregados(resposta.json(), rotulos_periodos_sidra())


def achatar_databank(largo: pd.DataFrame) -> pd.DataFrame:
    """Converte o CSV do DataBank (uma coluna por ano) em formato longo."""
    faltando = [c for c in COLUNAS_DATABANK if c not in largo.columns]
    if faltando:
        raise ValueError(
            "O arquivo não tem o formato do DataBank. Faltam as colunas: "
            + ", ".join(faltando)
        )
    colunas_ano = [c for c in largo.columns if re.fullmatch(r"\d{4}( \[YR\d{4}\])?", c)]
    if not colunas_ano:
        raise ValueError(
            "Nenhuma coluna de ano no padrão '1990 [YR1990]' foi encontrada."
        )

    longo = largo.melt(
        id_vars=list(COLUNAS_DATABANK),
        value_vars=colunas_ano,
        var_name="date",
        value_name="value",
    )
    longo["date"] = (
        longo["date"].str.slice(0, 4).astype(int).astype("Int64")
    )
    longo["value"] = pd.to_numeric(
        longo["value"].astype(str).str.strip().replace({"..": None, "": None}),
        errors="coerce",
    )
    # Participações (% do PIB) não são zero em nenhuma economia: no DataBank o
    # zero aparece onde o dado não existe, como no Brasil antes dos anos 1980.
    participacao = (
        longo["Series Code"].fillna("").str.endswith(".ZS")
    )
    longo.loc[participacao & (longo["value"] == 0), "value"] = pd.NA

    return pd.DataFrame(
        {
            "indicator.id": longo["Series Code"],
            "indicator.value": longo["Series Code"].map(
                lambda c: INDICADORES_WB.get(c, "")
            ).where(
                longo["Series Code"].isin(INDICADORES_WB), longo["Series Name"]
            ),
            "country.id": longo["Country Code"],
            "country.value": longo["Country Name"],
            "countryiso3code": longo["Country Code"],
            "date": longo["date"],
            "value": longo["value"],
        }
    ).dropna(subset=["indicator.id", "country.value"])


@st.cache_data
def data_extracao_wb() -> str:
    """Lê o rodapé 'Last Updated' que o DataBank grava no fim do CSV."""
    if not ARQ_WB_CSV.exists():
        return ""
    achado = re.search(
        r"Last Updated:\s*([\d/]+)",
        ARQ_WB_CSV.read_text(encoding="utf-8", errors="ignore"),
    )
    return achado.group(1) if achado else ""


def transformar_pivot(pivot: pd.DataFrame, modo: str) -> pd.DataFrame:
    if pivot.empty:
        return pivot
    ordenado = pivot.sort_index()
    if modo == "Índice 100":
        base = ordenado.iloc[0].replace(0, pd.NA)
        return ordenado.divide(base) * 100
    if modo == "Variação (p.p.)":
        return ordenado.subtract(ordenado.iloc[0])
    return ordenado


def eixo_ano(quadro: pd.DataFrame) -> pd.DataFrame:
    saida = quadro.copy()
    saida.index = [str(int(ano)) for ano in saida.index]
    return saida


def tokens_corpus(texto: str, corpus_completo: bool = False) -> list[str]:
    stop = STOPWORDS_CORPUS if corpus_completo else STOPWORDS_BASE
    palavras = re.findall(r"[a-záàâãéêíóôõúç]+", texto.lower())
    return [p for p in palavras if p not in stop and len(p) > 3]


@st.cache_data
def carregar_ods9() -> pd.DataFrame:
    if not ARQ_ODS9_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(ARQ_ODS9_CSV)


@st.cache_data
def carregar_corpus_ods9() -> str:
    if not ARQ_ODS9_TXT.exists():
        return ""
    return ARQ_ODS9_TXT.read_text(encoding="utf-8")


@st.cache_data
def frequencia_palavras(
    texto: str, n: int = 15, corpus_completo: bool = False
) -> pd.Series:
    contagem = Counter(tokens_corpus(texto, corpus_completo))
    if not contagem:
        return pd.Series(dtype="int64")
    return pd.Series(dict(contagem.most_common(n)))


@st.cache_data
def imagem_nuvem(texto: str, corpus_completo: bool = False):
    palavras = " ".join(tokens_corpus(texto, corpus_completo))
    if not palavras:
        return None
    cores = ("#1b4f72", "#922b21", "#1a5276", "#6c3483", "#196f3d", "#b03a2e")

    def cor_escura(word, font_size, position, orientation, random_state=None, **kwargs):
        if random_state is None:
            return cores[0]
        return cores[int(random_state.randint(0, len(cores) - 1))]

    nuvem = WordCloud(
        width=800,
        height=360,
        background_color="white",
        color_func=cor_escura,
    ).generate(palavras)
    return nuvem.to_array()
