import pandas as pd
import streamlit as st

from cliente_api import (
    api_disponivel,
    enviar_arquivo,
    obter,
    quadro,
    legenda_origem,
)
from dados import (
    ARQ_WB_CSV,
    data_consulta,
    INDICADOR_WB,
    INDICADORES_WB,
    data_extracao_wb,
    transformar_pivot,
)
from interface import (
    aviso_quebra,
    botao_download,
    configurar_pagina,
    grafico_linha,
    metrica_completude,
    sobre_os_dados,
)
from nucleo import ler_databank

PAISES_PADRAO = ("BRA", "DEU", "CHN", "USA")
CHAVES_FILTRO = (
    "filtro_wb_paises",
    "filtro_wb_indicadores",
    "filtro_wb_anos",
    "filtro_wb_ano_barra",
    "filtro_wb_pais_composicao",
)

configurar_pagina("Comparação internacional", layout="wide")

if "wb_usuario" not in st.session_state:
    st.session_state.wb_usuario = pd.DataFrame()
if "wb_arquivo_id" not in st.session_state:
    st.session_state.wb_arquivo_id = None
if "wb_origem" not in st.session_state:
    st.session_state.wb_origem = None
if "wb_envio_id" not in st.session_state:
    st.session_state.wb_envio_id = None


def _limpar_filtros() -> None:
    for chave in CHAVES_FILTRO:
        st.session_state.pop(chave, None)


def _paises_padrao(opcoes: list[str]) -> list[str]:
    escolhidos = [codigo for codigo in PAISES_PADRAO if codigo in opcoes]
    return escolhidos or list(opcoes[:1])


def _titulo_eixo(modo: str) -> str:
    if modo == "Índice 100":
        return "Índice (base 100)"
    if modo == "Variação (p.p.)":
        return "Variação (p.p.)"
    return "% do PIB"


st.title("Comparação internacional")
st.caption(
    "Como a participação da indústria de transformação no PIB do Brasil "
    "se compara à de outras economias."
)
sobre_os_dados(
    "World Bank, World Development Indicators, exportado do DataBank "
    f"(`{INDICADOR_WB}` é o indicador 9.2.1). Baixe o CSV de exemplo em "
    "Data/raw/ e envie-o no campo abaixo: filtros, gráficos e tabela só "
    "aparecem depois do upload. Com a API no ar, o arquivo vai para "
    "POST /world-bank e os dados voltam de GET /world-bank/{id}. Sem a "
    "API, o painel lê o CSV direto. Crescimento da transformação e "
    "exportações de alta tecnologia medem dinamismo e complexidade, e "
    "podem subir mesmo com a participação no PIB em queda."
)

if data_extracao_wb():
    st.caption(
        f"O CSV de exemplo foi atualizado pelo World Bank em "
        f"{data_extracao_wb()} (rodapé do próprio export)."
    )

if ARQ_WB_CSV.exists():
    st.download_button(
        "Baixar o CSV de exemplo (formato DataBank)",
        ARQ_WB_CSV.read_bytes(),
        file_name=ARQ_WB_CSV.name,
        mime="text/csv",
        key="dl_wb_exemplo",
        help="Baixe e envie no campo abaixo para alimentar esta página.",
    )

enviado = st.file_uploader(
    "Enviar CSV do DataBank",
    type=["csv"],
    key="upload_wb",
    help="Envie o CSV de exemplo ou outro export do DataBank.",
)
if enviado is not None:
    chave = (enviado.name, enviado.size)
    if st.session_state.get("wb_arquivo_id") != chave:
        conteudo = enviado.getvalue()
        try:
            if api_disponivel():
                criado = enviar_arquivo("/world-bank", enviado.name, conteudo)
                if criado is None:
                    quadro_wb = ler_databank(conteudo)
                    origem = "leitura direta"
                    envio_id = None
                else:
                    envio_id = criado["id"]
                    payload, origem = obter(f"/world-bank/{envio_id}")
                    quadro_wb = quadro(payload)
                    if quadro_wb.empty:
                        quadro_wb = ler_databank(conteudo)
                        origem = "leitura direta"
            else:
                quadro_wb = ler_databank(conteudo)
                origem = "leitura direta"
                envio_id = None
            st.session_state.wb_usuario = quadro_wb
            st.session_state.wb_arquivo_id = chave
            st.session_state.wb_origem = origem
            st.session_state.wb_envio_id = envio_id
            _limpar_filtros()
            st.success(
                f"{len(st.session_state.wb_usuario)} observações "
                "carregadas nesta sessão."
            )
        except ValueError as exc:
            st.error(f"Não foi possível usar o arquivo: {exc}")
            st.session_state.wb_usuario = pd.DataFrame()
            st.session_state.wb_arquivo_id = None
            st.session_state.wb_origem = None
            st.session_state.wb_envio_id = None

world_bank_base = st.session_state.wb_usuario
if enviado is not None:
    st.caption(f"Arquivo ativo: {enviado.name} (enviado nesta sessão).")
if st.session_state.wb_origem:
    if st.session_state.wb_envio_id:
        st.caption(f"Envio na API: `{st.session_state.wb_envio_id}`")
    legenda_origem(st.session_state.wb_origem)

escolhidos, indicadores = [], []
world_bank = pd.DataFrame()

if world_bank_base.empty:
    st.info(
        "Envie o CSV do DataBank para ver filtros, gráficos e a tabela. "
        "Use o botão acima para baixar o exemplo em Data/raw/."
    )
else:
    nomes_pais = dict(
        zip(world_bank_base["country.id"], world_bank_base["country.value"])
    )
    opcoes_pais = sorted(nomes_pais)
    nomes_indicador = dict(
        zip(
            world_bank_base["indicator.id"],
            world_bank_base["indicator.value"],
        )
    )
    opcoes_indicador = sorted(nomes_indicador)
    indicadores_padrao = (
        [INDICADOR_WB] if INDICADOR_WB in opcoes_indicador else opcoes_indicador[:1]
    )

    escolhidos = st.multiselect(
        "Países",
        opcoes_pais,
        default=_paises_padrao(opcoes_pais),
        format_func=lambda codigo: nomes_pais.get(codigo, codigo),
        key="filtro_wb_paises",
    )
    indicadores = st.multiselect(
        "Indicadores",
        opcoes_indicador,
        default=indicadores_padrao,
        format_func=lambda codigo: nomes_indicador.get(codigo, codigo),
        key="filtro_wb_indicadores",
    )

if (not escolhidos or not indicadores) and not world_bank_base.empty:
    st.info("Escolha ao menos um país e um indicador.")
elif escolhidos and indicadores:
    world_bank = world_bank_base[
        world_bank_base["country.id"].isin(escolhidos)
        & world_bank_base["indicator.id"].isin(indicadores)
    ].copy()

    if not world_bank.empty:
        anos = world_bank["date"].dropna()
        if not anos.empty:
            minimo, maximo = int(anos.min()), int(anos.max())
            if minimo == maximo:
                intervalo = (minimo, maximo)
                st.caption(f"Ano disponível: {minimo}")
            else:
                if "filtro_wb_anos" not in st.session_state:
                    st.session_state.filtro_wb_anos = (minimo, maximo)
                else:
                    inicio_ano, fim_ano = st.session_state.filtro_wb_anos
                    inicio_ano = min(max(int(inicio_ano), minimo), maximo)
                    fim_ano = min(max(int(fim_ano), minimo), maximo)
                    if inicio_ano > fim_ano:
                        inicio_ano, fim_ano = minimo, maximo
                    st.session_state.filtro_wb_anos = (inicio_ano, fim_ano)
                intervalo = st.slider(
                    "Anos (World Bank)",
                    min_value=minimo,
                    max_value=maximo,
                    format="%d",
                    key="filtro_wb_anos",
                )
            world_bank = world_bank[
                (world_bank["date"] >= intervalo[0])
                & (world_bank["date"] <= intervalo[1])
            ]
            aviso_quebra(intervalo[0], intervalo[1])

if world_bank.empty:
    if escolhidos and indicadores and not world_bank_base.empty:
        st.warning(
            "Não há série para essa combinação de país, indicador e período."
        )
else:
    modo_grafico = st.radio(
        "Gráfico",
        ("Evolução", "Comparação num ano", "Composição setorial"),
        horizontal=True,
        key="filtro_wb_grafico",
    )
    if modo_grafico == "Composição setorial":
        modo_valor = "Valor original"
        st.caption(
            "Composição só em % do PIB. Índice 100 e variação em pontos "
            "percentuais não se aplicam a um empilhamento de séries."
        )
    else:
        modo_valor = st.radio(
            "Transformação",
            ("Valor original", "Índice 100", "Variação (p.p.)"),
            horizontal=True,
            key="filtro_wb_transformacao",
        )
        st.caption(
            "Índice 100 e variação em pontos percentuais valem para a "
            "evolução, porque dependem da série no tempo. A base é o "
            "primeiro ano com valor de cada série."
        )
    util = world_bank.dropna(subset=["value", "date"])
    if util.empty:
        st.warning("Os registros existem, mas os valores estão vazios.")
    elif modo_grafico == "Evolução":
        if len(indicadores) == 1:
            pivot = util.pivot_table(
                index="date",
                columns="country.value",
                values="value",
                aggfunc="mean",
            )
        elif len(escolhidos) == 1:
            pivot = util.pivot_table(
                index="date",
                columns="indicator.value",
                values="value",
                aggfunc="mean",
            )
        else:
            st.caption(
                "Vários países e indicadores: um gráfico por indicador."
            )
            pivot = pd.DataFrame()
            for codigo in indicadores:
                recorte = util[util["indicator.id"] == codigo]
                parte = recorte.pivot_table(
                    index="date",
                    columns="country.value",
                    values="value",
                    aggfunc="mean",
                )
                parte = transformar_pivot(parte, modo_valor)
                if parte.empty or parte.dropna(how="all").empty:
                    st.warning(
                        "Sem valores para "
                        f"{INDICADORES_WB.get(codigo, codigo)}."
                    )
                    continue
                st.markdown(f"**{INDICADORES_WB.get(codigo, codigo)}**")
                parte.index.name = "ano"
                grafico_linha(
                    parte,
                    titulo_y=_titulo_eixo(modo_valor),
                    altura=420,
                )
        if not pivot.empty:
            pivot = transformar_pivot(pivot, modo_valor)
            pivot.index.name = "ano"
            grafico_linha(
                pivot, titulo_y=_titulo_eixo(modo_valor), altura=420
            )
    elif modo_grafico == "Comparação num ano":
        anos_bar = sorted(util["date"].dropna().unique())
        if "filtro_wb_ano_barra" not in st.session_state:
            st.session_state.filtro_wb_ano_barra = int(anos_bar[-1])
        if st.session_state.filtro_wb_ano_barra not in anos_bar:
            st.session_state.filtro_wb_ano_barra = int(anos_bar[-1])
        ano_bar = st.selectbox(
            "Ano da comparação",
            [int(ano) for ano in anos_bar],
            key="filtro_wb_ano_barra",
        )
        recorte = util[util["date"].astype(int) == ano_bar]
        barras = recorte.pivot_table(
            index="country.value",
            columns="indicator.value",
            values="value",
            aggfunc="mean",
        )
        if barras.empty or barras.dropna(how="all").empty:
            st.warning("Sem valores para o ano escolhido.")
        else:
            st.bar_chart(barras)
    else:
        nomes_comp = [
            INDICADORES_WB.get(codigo, codigo) for codigo in indicadores
        ]
        composicao = util[util["indicator.id"].isin(indicadores)]
        if composicao.empty:
            st.warning(
                "Não há valores para a composição com os indicadores escolhidos."
            )
        else:
            paises_comp = sorted(composicao["country.value"].dropna().unique())
            if "filtro_wb_pais_composicao" not in st.session_state:
                st.session_state.filtro_wb_pais_composicao = paises_comp[0]
            if st.session_state.filtro_wb_pais_composicao not in paises_comp:
                st.session_state.filtro_wb_pais_composicao = paises_comp[0]
            pais_comp = st.selectbox(
                "País da composição",
                paises_comp,
                key="filtro_wb_pais_composicao",
            )
            area = composicao[composicao["country.value"] == pais_comp]
            area = area.pivot_table(
                index="date",
                columns="indicator.value",
                values="value",
                aggfunc="mean",
            )
            area = area.reindex(columns=nomes_comp)
            if (
                "NV.IND.TOTL.ZS" in indicadores
                and "NV.IND.MANF.ZS" in indicadores
            ):
                st.caption(
                    "A transformação já entra na indústria total; "
                    "empilhar as duas conta a manufatura duas vezes."
                )
            if area.empty or area.dropna(how="all").empty:
                st.warning(f"Sem valores setoriais para {pais_comp}.")
            else:
                area.index = [str(int(ano)) for ano in area.index]
                st.area_chart(area, stack=True)

    visivel = world_bank.drop(columns=["decimal"], errors="ignore").copy()
    if "date" in visivel.columns:
        visivel["date"] = visivel["date"].astype("Int64").astype(str)
    if "value" in world_bank.columns:
        metrica_completude(world_bank["value"])
    st.dataframe(visivel, hide_index=True, width="stretch")
    if "indicator.id" in visivel.columns:
        codigos_wb = ", ".join(
            sorted(visivel["indicator.id"].dropna().astype(str).unique())
        )
    else:
        codigos_wb = INDICADOR_WB
    botao_download(
        visivel,
        "world_bank_filtrado.csv",
        "dl_wb",
        "Baixar recorte filtrado (CSV)",
        fonte="World Bank, World Development Indicators (DataBank)",
        codigo_serie=codigos_wb,
        data_extracao=data_consulta(),
    )

if not world_bank_base.empty:
    if st.button("Limpar CSV da sessão"):
        st.session_state.wb_usuario = pd.DataFrame()
        st.session_state.wb_arquivo_id = (
            (enviado.name, enviado.size) if enviado is not None else None
        )
        st.session_state.wb_origem = None
        st.session_state.wb_envio_id = None
        _limpar_filtros()
        st.rerun()
