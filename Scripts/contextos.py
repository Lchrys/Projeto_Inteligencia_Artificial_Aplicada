"""Contexto do assistente em cada página (TP5): as tabelas que a página mostra, em texto.

Cada função devolve o CONTEXTO inteiro de uma página, montado com as mesmas funções e tabelas que a
própria página usa (nucleo.py). O assistente (Code/modeling/assistente.py) só lê esse texto, então
vê exatamente o que o usuário vê: nenhum dado que não esteja na aplicação e nenhum resumo escolhido
de antemão. Sem Streamlit, para testar sem a interface.
"""

import sys

import pandas as pd

from nucleo import (
    ANO_QUEBRA_SCN,
    FONTE_IPEADATA,
    FONTE_WB,
    INDICADOR_WB,
    RAIZ,
    participacao_setorial,
    participacao_subsetores,
    participacao_transformacao,
    periodos_sidra,
    tabela_sidra_legivel,
)

if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from Code.modeling.assistente import montar_contexto, tabela_para_contexto  # noqa: E402

FONTE_SIDRA = "IBGE, SIDRA, tabela 1846 (Contas Nacionais Trimestrais)"


def _tabela_com_quebra(titulo: str, quadro: pd.DataFrame, fonte: str, nota: str) -> str:
    """Tabela com coluna "ano", do ano mais recente ao mais antigo, com resumo antes e depois de 1995.

    Na mudança de referência das Contas Nacionais (1995) os níveis deixam de ser comparáveis: de 1995 em
    diante valem entre si; antes, não (Data_Summary_Report.md). A tabela é uma só, para a busca de um
    ano ficar num lugar; o resumo calculado é dado separadamente para cada parte.
    """
    quadro = quadro.sort_values("ano", ascending=False)
    depois = quadro[quadro["ano"] >= ANO_QUEBRA_SCN]
    antes = quadro[quadro["ano"] < ANO_QUEBRA_SCN]
    nota_quebra = (
        f"Níveis NÃO comparáveis entre antes e depois de {ANO_QUEBRA_SCN}: houve mudanças de referência das "
        "Contas Nacionais (1989-90 e 1994-95), então uma queda que atravessa esse ano não é só "
        "desindustrialização."
    )
    resumos = {f"de {ANO_QUEBRA_SCN} em diante": depois}
    if not antes.empty:
        resumos[f"antes de {ANO_QUEBRA_SCN} (níveis não comparáveis com os de depois)"] = antes
    return tabela_para_contexto(
        titulo, quadro, fonte, nota=f"{nota} {nota_quebra}" if not antes.empty else nota, resumos=resumos
    )


def contexto_serie(serie: pd.DataFrame, intervalo: tuple[int, int] | None = None) -> str:
    """Série histórica: todos os anos do Ipeadata e, como seleção, o intervalo que o gráfico mostra."""
    base = serie[["ano", "valor"]].astype({"ano": int}).rename(columns={"valor": "% do PIB"})
    tabelas = [
        _tabela_com_quebra(
            "Participação da indústria de transformação no PIB do Brasil, todos os anos",
            base,
            FONTE_IPEADATA,
            "Preços correntes. O último ano pode ser preliminar.",
        )
    ]
    selecao = f"o gráfico mostra os anos de {intervalo[0]} a {intervalo[1]}" if intervalo else ""
    return montar_contexto(tabelas, selecao)


def contexto_panorama(trimestral: pd.DataFrame, subsetores: pd.DataFrame) -> str:
    """Panorama setorial: as contas do painel (acumulado de quatro trimestres) e os valores da SIDRA."""
    setores = participacao_setorial(trimestral)
    transformacao = participacao_transformacao(trimestral, subsetores)
    composicao = setores[["setor", "codigo", "valor_milhoes", "pct_pib"]].copy()
    composicao.loc[len(composicao)] = [
        "Transformação (dos quais: subsetor da indústria)",
        transformacao["codigo"],
        transformacao["valor_milhoes"],
        transformacao["pct_pib"],
    ]
    composicao.columns = ["setor", "codigo", "valor (milhões de R$)", "% do PIB"]

    industria = participacao_subsetores(trimestral, subsetores)[
        ["setor", "codigo", "valor_milhoes", "pct_industria", "pct_pib"]
    ]
    industria.columns = ["subsetor", "codigo", "valor (milhões de R$)", "% da indústria", "% do PIB"]

    trimestrais = pd.concat(
        [
            tabela_sidra_legivel(quadro)[["periodo", "setor", "valor"]]
            for quadro in (trimestral, subsetores)
            if not quadro.empty
        ],
        ignore_index=True,
    )
    trimestrais["valor"] = pd.to_numeric(trimestrais["valor"], errors="coerce")
    trimestrais = trimestrais.rename(columns={"valor": "valor (milhões de R$)"})

    janela = periodos_sidra(trimestral)
    tabelas = [
        tabela_para_contexto(
            "Composição do PIB por setor, acumulado dos últimos quatro trimestres",
            composicao,
            FONTE_SIDRA,
            nota=(
                "Preços correntes. Agropecuária, indústria, serviços e impostos líquidos somam o PIB a "
                "preços de mercado. A transformação é subsetor da indústria, não um quarto setor. É o "
                "acumulado de quatro trimestres, não uma série histórica."
            ),
        ),
        tabela_para_contexto(
            "Subsetores da indústria, acumulado dos últimos quatro trimestres",
            industria,
            FONTE_SIDRA,
            nota="% da indústria é a fatia de cada subsetor na indústria total (código 90691).",
        ),
        tabela_para_contexto(
            "Valores trimestrais dos setores e subsetores",
            trimestrais,
            FONTE_SIDRA,
            nota="Cada linha é um trimestre. Os valores acumulados acima somam estes quatro trimestres.",
        ),
    ]
    selecao = (
        f"acumulado de {janela['rotulo_inicio']} a {janela['rotulo_fim']}" if janela["inicio"] else ""
    )
    return montar_contexto(tabelas, selecao)


def contexto_comparacao(wb: pd.DataFrame, selecao: str = "") -> str:
    """Comparação internacional: o CSV do DataBank que o usuário enviou, uma tabela por indicador.

    Cada tabela tem um ano por linha e um país por coluna ("sem dado" = o país não divulgou o ano).
    """
    ordem = sorted(wb["indicator.id"].unique(), key=lambda i: (i != INDICADOR_WB, i))
    tabelas = []
    for indicador in ordem:
        parte = wb[wb["indicator.id"] == indicador]
        nome = str(parte["indicator.value"].iloc[0])
        larga = parte.pivot_table(index="date", columns="country.value", values="value", aggfunc="first")
        larga = larga.dropna(how="all").sort_index()
        larga.index = larga.index.astype(int)
        larga.index.name = "ano"
        tabelas.append(
            _tabela_com_quebra(
                f"{nome} ({indicador})",
                larga.reset_index(),
                f"{FONTE_WB}, CSV enviado pelo usuário",
                'Um país por coluna; "sem dado" = o país não divulgou o ano.',
            )
        )
    return montar_contexto(tabelas, selecao)
