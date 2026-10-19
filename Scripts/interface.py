import altair as alt
import pandas as pd
import streamlit as st

from dados import ANO_QUEBRA_SCN
from nucleo import completude_anual


def configurar_pagina(titulo: str, layout: str = "centered") -> None:
    st.set_page_config(
        page_title=titulo,
        page_icon=":bar_chart:",
        layout=layout,
    )
    largura = "none" if layout == "wide" else "860px"
    st.markdown(
        f"""
        <style>
          .block-container {{ max-width: {largura}; padding-top: 2rem; }}
          h1 {{ font-size: 1.85rem; line-height: 1.25; margin-bottom: 0.25rem; }}
          h3 {{ margin-top: 1.6rem; margin-bottom: 0.6rem; }}
          div[data-testid="stLinkButton"] {{ width: 100%; }}
          div[data-testid="stLinkButton"] a {{
            width: 100%;
            min-height: 2.75rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-align: center;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.caption(
        "Participação da indústria de transformação no PIB "
        "(ODS 9, indicador 9.2.1)"
    )


def sobre_os_dados(texto: str) -> None:
    with st.expander("Sobre os dados"):
        st.markdown(texto)


def grafico_linha(
    quadro: pd.DataFrame,
    titulo_y: str = "% do PIB",
    marcar_quebra: bool = True,
    altura: int = 360,
) -> None:
    """Linha com eixo em % do PIB, tooltip e, se couber, marca em 1995."""
    dados = quadro.copy()
    if "ano" not in dados.columns and "date" not in dados.columns:
        dados = dados.reset_index()
        dados = dados.rename(columns={dados.columns[0]: "ano"})
    if "date" in dados.columns and "ano" not in dados.columns:
        dados = dados.rename(columns={"date": "ano"})
    if "valor" not in dados.columns:
        dados = dados.melt(id_vars=["ano"], var_name="serie", value_name="valor")
    dados["ano"] = pd.to_numeric(dados["ano"], errors="coerce")
    dados["valor"] = pd.to_numeric(dados["valor"], errors="coerce")
    dados = dados.dropna(subset=["ano", "valor"])
    if dados.empty:
        st.info("Sem valores para o gráfico.")
        return

    tem_serie = "serie" in dados.columns and dados["serie"].nunique() > 1
    encoding = {
        "x": alt.X("ano:Q", title="Ano", axis=alt.Axis(format="d")),
        "y": alt.Y("valor:Q", title=titulo_y),
        "tooltip": [
            alt.Tooltip("ano:Q", title="Ano", format="d"),
            alt.Tooltip("valor:Q", title=titulo_y, format=".1f"),
        ],
    }
    if tem_serie:
        encoding["color"] = alt.Color("serie:N", title="")
        encoding["tooltip"] = [
            alt.Tooltip("serie:N", title="Série"),
            *encoding["tooltip"],
        ]
    linhas = (
        alt.Chart(dados)
        .mark_line(point=True)
        .encode(**encoding)
        .properties(height=altura)
    )
    camadas = [linhas]
    if marcar_quebra:
        minimo, maximo = int(dados["ano"].min()), int(dados["ano"].max())
        if minimo <= ANO_QUEBRA_SCN <= maximo:
            marca = pd.DataFrame(
                {
                    "ano": [ANO_QUEBRA_SCN],
                    "rotulo": ["Mudança de referência do SCN"],
                }
            )
            camadas.append(
                alt.Chart(marca)
                .mark_rule(strokeDash=[4, 4], color="#922b21")
                .encode(x="ano:Q")
            )
            camadas.append(
                alt.Chart(marca)
                .mark_text(
                    align="left", dx=6, dy=-8, color="#922b21", fontSize=11
                )
                .encode(x="ano:Q", text="rotulo:N")
            )
    st.altair_chart(alt.layer(*camadas).configure_axis(grid=True), use_container_width=True)


def aviso_quebra(inicio: int, fim: int) -> None:
    if inicio < ANO_QUEBRA_SCN <= fim:
        st.warning(
            "O período escolhido atravessa "
            f"{ANO_QUEBRA_SCN}, ano em que as Contas Nacionais "
            "brasileiras mudaram de referência. Parte da queda da "
            "transformação nesse intervalo é revisão metodológica, "
            "não desindustrialização. Para comparar níveis, use "
            f"{ANO_QUEBRA_SCN} em diante."
        )


def metrica_completude(
    serie: pd.Series,
    anos=None,
    inicio: int | None = None,
    fim: int | None = None,
) -> None:
    if anos is not None and inicio is not None and fim is not None:
        taxa = completude_anual(anos, inicio, fim)
        if pd.isna(taxa):
            return
        st.metric("Completude do recorte", f"{taxa:.0%}")
        return
    if serie.empty:
        return
    valores = pd.to_numeric(serie, errors="coerce")
    st.metric("Completude do recorte", f"{1 - valores.isna().mean():.0%}")


def botao_download(
    df: pd.DataFrame,
    nome: str,
    chave: str,
    rotulo: str = "Baixar esta tabela (CSV)",
    fonte: str = "",
    codigo_serie: str = "",
    data_extracao: str = "",
) -> None:
    if df.empty:
        return
    saida = df.copy()
    if fonte:
        saida["fonte"] = fonte
    if codigo_serie:
        saida["codigo_serie"] = codigo_serie
    if data_extracao:
        saida["data_extracao"] = data_extracao
    st.download_button(
        rotulo,
        saida.to_csv(index=False).encode("utf-8"),
        file_name=nome,
        mime="text/csv",
        key=chave,
    )
