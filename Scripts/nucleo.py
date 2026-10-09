"""Carga e transformação das séries, sem dependência do Streamlit."""

from collections import Counter
from datetime import date
from pathlib import Path
import re
import uuid

import pandas as pd
import requests
import ipeadatapy as ipea

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
    "variaveis/all?localidades=N1[1]"
    "&classificacao=11255[90707,90705,90706,90687,90691,90696]"
)
CODIGOS_SIDRA = {
    "pib": "90707",
    "va": "90705",
    "impostos": "90706",
    "agro": "90687",
    "industria": "90691",
    "servicos": "90696",
    "transformacao": "90693",
    "extrativas": "90692",
    "construcao": "90694",
    "utilities": "90695",
}
TOLERANCIA_SOMA = 0.005
URL_SIDRA_SUBSETORES = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/1846/periodos/-1/"
    "variaveis/all?localidades=N1[1]&classificacao=11255[90693,90692,90694,90695]"
)
RAIZ = Path(__file__).resolve().parents[1]
ARQ_ODS9_CSV = RAIZ / "Data" / "raw" / "ods9_metas.csv"
ARQ_ODS9_TXT = RAIZ / "Data" / "raw" / "ods9_corpus.txt"
ARQ_WB_CSV = RAIZ / "Data" / "raw" / "world_bank_setorial.csv"
ARQ_DOCUMENTOS = RAIZ / "Data" / "processed" / "documentos.csv"
COLUNAS_DATABANK = ("Country Name", "Country Code", "Series Name", "Series Code")
COLUNAS_DOCUMENTOS = ("id", "fonte", "url", "data", "tipo", "titulo", "texto")
FONTE_IPEADATA = "Ipeadata, série SCN10_VAITY10 (IBGE/SCN Anual)"
FONTE_WB = "World Bank, World Development Indicators (DataBank)"
FONTE_ODS9 = "Ipea, página ODS 9"


def data_consulta() -> str:
    return date.today().isoformat()
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


def consultar_ipeadata(codigo: str) -> pd.DataFrame:
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


def rotulos_periodos_sidra(agregado: str = "1846") -> dict:
    resposta = requests.get(
        f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos",
        headers=HEADERS,
        timeout=30,
    )
    resposta.raise_for_status()
    return {item["id"]: item["literals"][0] for item in resposta.json()}


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


def data_extracao_wb(caminho: Path | None = None) -> str:
    """Lê o rodapé 'Last Updated' que o DataBank grava no fim do CSV."""
    arquivo = caminho or ARQ_WB_CSV
    if not arquivo.exists():
        return ""
    achado = re.search(
        r"Last Updated:\s*([\d/]+)",
        arquivo.read_text(encoding="utf-8", errors="ignore"),
    )
    return achado.group(1) if achado else ""


def transformar_pivot(pivot: pd.DataFrame, modo: str) -> pd.DataFrame:
    if pivot.empty:
        return pivot
    ordenado = pivot.sort_index()
    if modo == "Índice 100":
        base = ordenado.replace(0, pd.NA).bfill().iloc[0]
        return ordenado.divide(base) * 100
    if modo == "Variação (p.p.)":
        base = ordenado.bfill().iloc[0]
        return ordenado.subtract(base)
    return ordenado


def completude_anual(anos, inicio: int, fim: int) -> float:
    if fim < inicio:
        return float("nan")
    esperado = fim - inicio + 1
    serie = pd.to_numeric(pd.Series(anos), errors="coerce").dropna().astype(int)
    distintos = serie[(serie >= inicio) & (serie <= fim)].nunique()
    return distintos / esperado


def eixo_ano(quadro: pd.DataFrame) -> pd.DataFrame:
    saida = quadro.copy()
    saida.index = [str(int(ano)) for ano in saida.index]
    return saida


def tokens_corpus(texto: str, corpus_completo: bool = False) -> list[str]:
    stop = STOPWORDS_CORPUS if corpus_completo else STOPWORDS_BASE
    palavras = re.findall(r"[a-záàâãéêíóôõúç]+", texto.lower())
    return [p for p in palavras if p not in stop and len(p) > 3]


def carregar_ods9() -> pd.DataFrame:
    if not ARQ_ODS9_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(ARQ_ODS9_CSV)


def carregar_corpus_ods9() -> str:
    if not ARQ_ODS9_TXT.exists():
        return ""
    return ARQ_ODS9_TXT.read_text(encoding="utf-8")


def frequencia_palavras(
    texto: str, n: int = 15, corpus_completo: bool = False
) -> pd.Series:
    contagem = Counter(tokens_corpus(texto, corpus_completo))
    if not contagem:
        return pd.Series(dtype="int64")
    return pd.Series(dict(contagem.most_common(n)))


def descartar_rodape_databank(largo: pd.DataFrame) -> pd.DataFrame:
    if "Country Name" not in largo.columns:
        return largo
    nomes = largo["Country Name"].fillna("").astype(str).str.strip()
    return largo.loc[
        nomes.ne("")
        & ~nomes.str.startswith("Data from", na=False)
        & ~nomes.str.startswith("Last Updated", na=False)
    ].copy()


def carregar_world_bank(caminho: Path | None = None) -> pd.DataFrame:
    arquivo = caminho or ARQ_WB_CSV
    if not arquivo.exists():
        return pd.DataFrame()
    largo = descartar_rodape_databank(pd.read_csv(arquivo, dtype=str))
    if largo.empty:
        return pd.DataFrame()
    return achatar_databank(largo)


def coluna_valor_ipeadata(ipeadata: pd.DataFrame) -> str | None:
    if "VALUE ((% PIB))" in ipeadata.columns:
        return "VALUE ((% PIB))"
    if "VALUE" in ipeadata.columns:
        return "VALUE"
    return None


def normalizar_serie_transformacao(ipeadata: pd.DataFrame) -> pd.DataFrame:
    if ipeadata.empty or "YEAR" not in ipeadata.columns:
        return pd.DataFrame()
    coluna = coluna_valor_ipeadata(ipeadata)
    if coluna is None:
        return pd.DataFrame()
    serie = pd.DataFrame(
        {
            "ano": pd.to_numeric(ipeadata["YEAR"], errors="coerce"),
            "valor": pd.to_numeric(ipeadata[coluna], errors="coerce"),
        }
    )
    return serie.dropna().sort_values("ano")


def serie_transformacao() -> pd.DataFrame:
    return normalizar_serie_transformacao(consultar_ipeadata(CODIGO_IPEA))


def valor_sidra(quadro: pd.DataFrame, codigo: str) -> float | None:
    if quadro.empty or "D3C" not in quadro.columns or "V" not in quadro.columns:
        return None
    recorte = quadro[quadro["D3C"].astype(str) == str(codigo)]
    if recorte.empty:
        return None
    valores = pd.to_numeric(recorte["V"], errors="coerce").dropna()
    if valores.empty:
        return None
    return float(valores.iloc[0])


def _linha_participacao(
    nome: str, codigo: str, valor: float | None, pib: float | None, va: float | None
) -> dict:
    return {
        "setor": nome,
        "codigo": codigo,
        "valor_milhoes": valor,
        "pct_pib": None if pib in (None, 0) or valor is None else 100 * valor / pib,
        "pct_va": None if va in (None, 0) or valor is None else 100 * valor / va,
        "pct_industria": None,
    }


def participacao_setorial(
    trimestral: pd.DataFrame, subsetores: pd.DataFrame
) -> pd.DataFrame:
    pib = valor_sidra(trimestral, CODIGOS_SIDRA["pib"])
    va = valor_sidra(trimestral, CODIGOS_SIDRA["va"])
    linhas = [
        ("Agropecuária", CODIGOS_SIDRA["agro"], trimestral),
        ("Indústria", CODIGOS_SIDRA["industria"], trimestral),
        ("Serviços", CODIGOS_SIDRA["servicos"], trimestral),
        ("Transformação", CODIGOS_SIDRA["transformacao"], subsetores),
    ]
    saida = [
        _linha_participacao(nome, codigo, valor_sidra(fonte, codigo), pib, va)
        for nome, codigo, fonte in linhas
    ]
    return pd.DataFrame(saida)


def participacao_subsetores(
    trimestral: pd.DataFrame, subsetores: pd.DataFrame
) -> pd.DataFrame:
    pib = valor_sidra(trimestral, CODIGOS_SIDRA["pib"])
    industria = valor_sidra(trimestral, CODIGOS_SIDRA["industria"])
    itens = [
        ("Transformação", CODIGOS_SIDRA["transformacao"]),
        ("Extrativas", CODIGOS_SIDRA["extrativas"]),
        ("Construção", CODIGOS_SIDRA["construcao"]),
        ("Eletricidade, gás e água", CODIGOS_SIDRA["utilities"]),
    ]
    linhas = []
    for nome, codigo in itens:
        valor = valor_sidra(subsetores, codigo)
        linha = _linha_participacao(nome, codigo, valor, pib, None)
        if industria not in (None, 0) and valor is not None:
            linha["pct_industria"] = 100 * valor / industria
        linhas.append(linha)
    return pd.DataFrame(linhas)


def conferir_somas(trimestral: pd.DataFrame) -> dict:
    pib = valor_sidra(trimestral, CODIGOS_SIDRA["pib"])
    va = valor_sidra(trimestral, CODIGOS_SIDRA["va"])
    impostos = valor_sidra(trimestral, CODIGOS_SIDRA["impostos"])
    agro = valor_sidra(trimestral, CODIGOS_SIDRA["agro"])
    industria = valor_sidra(trimestral, CODIGOS_SIDRA["industria"])
    servicos = valor_sidra(trimestral, CODIGOS_SIDRA["servicos"])
    soma_setores = (
        None
        if None in (agro, industria, servicos)
        else agro + industria + servicos
    )
    va_impostos = None if None in (va, impostos) else va + impostos

    def relativa(obtido, esperado) -> float | None:
        if obtido is None or esperado in (None, 0):
            return None
        return abs(obtido - esperado) / abs(esperado)

    diff_va = relativa(soma_setores, va)
    diff_pib = relativa(va_impostos, pib)
    ok_va = diff_va is not None and diff_va <= TOLERANCIA_SOMA
    ok_pib = diff_pib is not None and diff_pib <= TOLERANCIA_SOMA
    return {
        "soma_setores": soma_setores,
        "va": va,
        "impostos": impostos,
        "pib": pib,
        "diff_setores_va": diff_va,
        "diff_va_impostos_pib": diff_pib,
        "ok_setores_va": ok_va,
        "ok_va_impostos_pib": ok_pib,
        "ok": ok_va and ok_pib,
        "tolerancia": TOLERANCIA_SOMA,
    }


def recortar_serie(
    serie: pd.DataFrame, inicio: int | None = None, fim: int | None = None
) -> pd.DataFrame:
    recorte = serie
    if inicio is not None:
        recorte = recorte[recorte["ano"] >= inicio]
    if fim is not None:
        recorte = recorte[recorte["ano"] <= fim]
    return recorte


def filtrar_world_bank(
    quadro: pd.DataFrame,
    pais: str | None = None,
    indicador: str | None = None,
    inicio: int | None = None,
    fim: int | None = None,
) -> pd.DataFrame:
    recorte = quadro
    if pais:
        recorte = recorte[
            recorte["country.id"].astype(str).str.upper() == pais.upper()
        ]
    if indicador:
        recorte = recorte[
            recorte["indicator.id"].astype(str).str.upper() == indicador.upper()
        ]
    if inicio is not None:
        recorte = recorte[recorte["date"] >= inicio]
    if fim is not None:
        recorte = recorte[recorte["date"] <= fim]
    return recorte


def quadro_vazio_documentos() -> pd.DataFrame:
    return pd.DataFrame(columns=list(COLUNAS_DOCUMENTOS))


def carregar_documentos() -> pd.DataFrame:
    if not ARQ_DOCUMENTOS.exists():
        return quadro_vazio_documentos()
    lido = pd.read_csv(ARQ_DOCUMENTOS, dtype=str).fillna("")
    for coluna in COLUNAS_DOCUMENTOS:
        if coluna not in lido.columns:
            lido[coluna] = ""
    return lido.loc[:, list(COLUNAS_DOCUMENTOS)]


def gravar_documentos(quadro: pd.DataFrame) -> None:
    ARQ_DOCUMENTOS.parent.mkdir(parents=True, exist_ok=True)
    quadro.loc[:, list(COLUNAS_DOCUMENTOS)].to_csv(
        ARQ_DOCUMENTOS, index=False, encoding="utf-8"
    )


def anexar_documento(
    titulo: str,
    texto: str,
    fonte: str,
    data: str,
    url: str = "",
    tipo: str = "usuario",
) -> dict:
    linha = {
        "id": str(uuid.uuid4()),
        "fonte": fonte.strip(),
        "url": url.strip(),
        "data": data.strip(),
        "tipo": tipo.strip() or "usuario",
        "titulo": titulo.strip(),
        "texto": texto.strip(),
    }
    atual = carregar_documentos()
    atual = pd.concat([atual, pd.DataFrame([linha])], ignore_index=True)
    gravar_documentos(atual)
    return linha


def filtrar_documentos(
    quadro: pd.DataFrame, busca: str | None = None, limite: int | None = None
) -> pd.DataFrame:
    recorte = quadro
    if busca:
        termo = busca.casefold()
        mascara = (
            recorte["titulo"].fillna("").str.casefold().str.contains(termo, regex=False)
            | recorte["texto"].fillna("").str.casefold().str.contains(termo, regex=False)
            | recorte["fonte"].fillna("").str.casefold().str.contains(termo, regex=False)
        )
        recorte = recorte[mascara]
    if limite is not None:
        recorte = recorte.head(limite)
    return recorte


def documentos_ods9() -> pd.DataFrame:
    metas = carregar_ods9()
    if metas.empty:
        return quadro_vazio_documentos()
    linhas = []
    for _, linha in metas.iterrows():
        partes = [
            str(linha.get(campo, "") or "")
            for campo in ("onu", "brasil", "justificativa", "conceitos", "indicadores")
        ]
        linhas.append(
            {
                "id": f"ods9-{linha.get('meta', '')}",
                "fonte": FONTE_ODS9,
                "url": str(linha.get("fonte", "") or ""),
                "data": str(linha.get("data_extracao", "") or ""),
                "tipo": "ods9",
                "titulo": f"Meta {linha.get('meta', '')}",
                "texto": " ".join(parte for parte in partes if parte.strip()),
            }
        )
    return pd.DataFrame(linhas, columns=list(COLUNAS_DOCUMENTOS))


def corpus_textual() -> pd.DataFrame:
    return pd.concat(
        [documentos_ods9(), carregar_documentos()],
        ignore_index=True,
    )


def ranking_transformacao(wb: pd.DataFrame) -> dict:
    universo = (
        "economias do CSV de exemplo do DataBank "
        "(Data/raw/world_bank_setorial.csv)"
    )
    base = wb[
        (wb["indicator.id"] == INDICADOR_WB)
        & (wb["date"] >= ANO_QUEBRA_SCN)
    ]
    if base.empty:
        return {}
    paises_arquivo = sorted(
        base["country.value"].dropna().astype(str).unique()
    )
    brasil = base[base["country.id"].astype(str).str.upper() == "BRA"].dropna(
        subset=["value", "date"]
    )
    if brasil.empty:
        return {}
    ano = int(brasil["date"].max())
    com_data = base.dropna(subset=["date"]).copy()
    com_data["date"] = pd.to_numeric(com_data["date"], errors="coerce")
    no_ano = com_data[com_data["date"] == ano].copy()
    com_valor = no_ano.dropna(subset=["value"]).sort_values(
        "value", ascending=False
    )
    nomes_com_valor = [
        str(nome) for nome in com_valor["country.value"].dropna().astype(str)
    ]
    sem_valor = sorted(set(paises_arquivo) - set(nomes_com_valor))
    posicao = None
    valor_brasil = None
    ordem = []
    for i, linha in enumerate(com_valor.to_dict("records"), start=1):
        codigo = str(linha.get("country.id", ""))
        valor = round(float(linha["value"]), 2)
        ordem.append(
            {
                "posicao": i,
                "pais": str(linha.get("country.value", "")),
                "codigo": codigo,
                "valor": valor,
            }
        )
        if codigo.upper() == "BRA":
            posicao = i
            valor_brasil = valor
    return {
        "ano": ano,
        "indicador": INDICADOR_WB,
        "universo": universo,
        "paises_no_arquivo": len(paises_arquivo),
        "paises_com_valor_no_ano": len(ordem),
        "paises_sem_valor_no_ano": sem_valor,
        "posicao_brasil": posicao,
        "valor_brasil": valor_brasil,
        "n_paises": len(ordem),
        "paises": ordem,
        "nota": (
            "Posição entre as economias do CSV de exemplo no último ano "
            "com valor do Brasil, não um ranking mundial."
        ),
    }


def fatos_resumo(serie: pd.DataFrame | None = None) -> dict:
    if serie is None:
        serie = serie_transformacao()
    resultado = {
        "fonte_serie": FONTE_IPEADATA,
        "codigo_serie": CODIGO_IPEA,
        "ano_quebra": ANO_QUEBRA_SCN,
        "data_consulta": data_consulta(),
        "unidade": "% do PIB (preços correntes)",
    }
    if serie.empty:
        resultado["serie"] = None
        resultado["ranking"] = None
        return resultado

    ultimo = serie.iloc[-1]
    comparavel = serie[serie["ano"] >= ANO_QUEBRA_SCN]
    if comparavel.empty:
        comparavel = serie
    base = serie[serie["ano"] == ANO_QUEBRA_SCN]
    ano_maximo = int(comparavel.loc[comparavel["valor"].idxmax(), "ano"])
    resultado["serie"] = {
        "ultimo_ano": int(ultimo["ano"]),
        "ultimo_valor": round(float(ultimo["valor"]), 2),
        "maximo": round(float(comparavel["valor"].max()), 2),
        "ano_maximo": ano_maximo,
    }
    if not base.empty:
        valor_base = float(base.iloc[0]["valor"])
        resultado["serie"]["valor_1995"] = round(valor_base, 2)
        resultado["serie"]["variacao_desde_1995"] = round(
            float(ultimo["valor"]) - valor_base, 2
        )

    try:
        wb = carregar_world_bank()
        resultado["ranking"] = ranking_transformacao(wb) or None
        resultado["fonte_ranking"] = FONTE_WB
        resultado["data_atualizacao_wb"] = data_extracao_wb() or None
    except (ValueError, OSError, pd.errors.ParserError):
        resultado["ranking"] = None
    return resultado
