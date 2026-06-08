"""
Dashboard Nível 1 — Cesta Básica Brasil
TCC Engenharia de Software
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from themes import (
    TEMAS,
    css_tema,
    layout_plotly,
    legenda_responsiva,
    margens_grafico,
    obter_tema,
)

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PLOTLY = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
    "scrollZoom": True,
    "responsive": True,
}
DADOS_PATH = BASE_DIR / "data" / "processed" / "cesta_basica_processada.csv"
PROJECOES_PATH = BASE_DIR / "outputs" / "projecoes_2026_2030.csv"
METRICAS_PATH = BASE_DIR / "outputs" / "metricas_modelos.csv"

DATA_PROJECAO_INICIO = pd.Timestamp("2026-04-01")


@st.cache_data(show_spinner=False)
def carregar_dados() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(DADOS_PATH, parse_dates=["data"])
    projecoes = pd.read_csv(PROJECOES_PATH, parse_dates=["data"])
    metricas = pd.read_csv(METRICAS_PATH)
    return df, projecoes, metricas


def ultimo_mes(df: pd.DataFrame) -> pd.Timestamp:
    return df["data"].max()


def serie_capital(df: pd.DataFrame, capital: str) -> pd.DataFrame:
    if capital == "Média Nacional":
        media = (
            df.groupby("data", as_index=False)["custo"]
            .mean()
            .rename(columns={"custo": "custo"})
        )
        media["capital"] = "Média Nacional"
        return media.sort_values("data")
    return df[df["capital"] == capital].sort_values("data")


def ranking_ultimo_mes(df: pd.DataFrame, data_ref: pd.Timestamp) -> pd.DataFrame:
    snapshot = df[df["data"] == data_ref].copy()
    snapshot = snapshot.sort_values("custo", ascending=False).reset_index(drop=True)
    snapshot["posicao"] = snapshot.index + 1
    return snapshot


def filtrar_periodo(df: pd.DataFrame, inicio: pd.Timestamp, fim: pd.Timestamp) -> pd.DataFrame:
    return df[(df["data"] >= inicio) & (df["data"] <= fim)]


def grafico_comparacao(dfs: list[pd.DataFrame], titulo: str, tema: dict) -> go.Figure:
    fig = go.Figure()
    for i, serie in enumerate(dfs):
        nome = serie["capital"].iloc[0]
        cor = tema["comparacao"][i % len(tema["comparacao"])]
        fig.add_trace(
            go.Scatter(
                x=serie["data"],
                y=serie["custo"],
                mode="lines",
                name=nome,
                line=dict(color=cor, width=2.5),
            )
        )
    return layout_plotly(
        fig,
        tema,
        title=titulo,
        xaxis_title="Data",
        yaxis_title="Custo (R$)",
        hovermode="x unified",
        legend=legenda_responsiva(),
        height=400,
        margin=margens_grafico(),
    )


def cor_historico_capital(capital: str, tema: dict) -> str:
    if capital == "São Luís":
        return tema["sao_luis"]
    if capital == "Média Nacional":
        return tema["media"]
    return tema["primary"]


def projecao_dez_2030(projecoes: pd.DataFrame, capital: str, cenario: str) -> float | None:
    serie = projecoes[
        (projecoes["capital"] == capital) & (projecoes["cenario"] == cenario)
    ].sort_values("data")
    if serie.empty:
        return None
    return float(serie["custo_projetado"].iloc[-1])


def grafico_capital_com_projecao(
    historico: pd.DataFrame,
    projecoes: pd.DataFrame,
    capital: str,
    cenarios: list[str],
    tema: dict,
) -> go.Figure:
    fig = go.Figure()
    cor_hist = cor_historico_capital(capital, tema)

    fig.add_trace(
        go.Scatter(
            x=historico["data"],
            y=historico["custo"],
            mode="lines",
            name="Histórico",
            line=dict(color=cor_hist, width=2.5),
        )
    )

    proj_cap = projecoes[projecoes["capital"] == capital]
    for cenario in cenarios:
        serie = proj_cap[proj_cap["cenario"] == cenario].sort_values("data")
        if serie.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=serie["data"],
                y=serie["custo_projetado"],
                mode="lines",
                name=f"Cenário {cenario}",
                line=dict(
                    color=tema["cenarios"][cenario],
                    width=2,
                    dash="dash",
                ),
            )
        )

    fig.add_vline(
        x=DATA_PROJECAO_INICIO,
        line_dash="dot",
        line_color=tema["text_muted"],
        annotation_text="Projeções",
        annotation_position="top right",
        annotation_font_color=tema["text_muted"],
    )

    return layout_plotly(
        fig,
        tema,
        title=f"Evolução e projeção — {capital}",
        xaxis_title="Data",
        yaxis_title="Custo (R$)",
        hovermode="x unified",
        legend=legenda_responsiva(),
        height=420,
        margin=margens_grafico(),
    )


def grafico_metricas(metricas: pd.DataFrame, serie: str, tema: dict) -> go.Figure:
    dados = metricas[metricas["serie"] == serie].copy()
    dados["rotulo"] = dados["modelo"] + " — " + dados["metrica"]
    fig = px.bar(
        dados,
        x="rotulo",
        y="valor",
        color="modelo",
        title=f"Métricas de erro — {serie}",
        labels={"valor": "Valor", "rotulo": ""},
        color_discrete_map={"SARIMA": tema["media"], "Prophet": tema["sao_luis"]},
    )
    return layout_plotly(
        fig,
        tema,
        height=340,
        showlegend=False,
        xaxis_tickangle=-45,
        margin=margens_grafico(),
    )


def configurar_pagina() -> None:
    st.set_page_config(
        page_title="Cesta Básica Brasil",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def aplicar_tema(nome_tema: str) -> dict:
    tema = obter_tema(nome_tema)
    st.markdown(css_tema(tema), unsafe_allow_html=True)
    return tema


def render_hero(tema: dict) -> None:
    titulo_cor = tema["bg"] if tema["nome"] in ("Escuro", "Azul Institucional") else tema["text"]
    if tema["nome"] == "Claro (TCC)":
        titulo_cor = "#ffffff"
        subtitulo_cor = "#e8f3ec"
    elif tema["nome"] == "Alto Contraste":
        titulo_cor = tema["text"]
        subtitulo_cor = tema["text_muted"]
    else:
        subtitulo_cor = tema["bg"] if tema["nome"] == "Escuro" else "#e2e8f0"

    st.markdown(
        f"""
        <div class="dashboard-hero">
            <h1 style="color:{titulo_cor};">Cesta Básica Brasil</h1>
            <p style="color:{subtitulo_cor};">
                Pipeline de análise e projeção de preços — TCC Engenharia de Software
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="mobile-hint">Toque em <strong>☰</strong> no canto superior para filtros, temas e capitais.</div>',
        unsafe_allow_html=True,
    )


def indice_capital_padrao(opcoes: list[str], preferida: str = "São Luís") -> int:
    return opcoes.index(preferida) if preferida in opcoes else 0


def capitais_comparacao_padrao(opcoes: list[str]) -> list[str]:
    preferidas = ["São Luís", "São Paulo", "Média Nacional"]
    selecionadas = [capital for capital in preferidas if capital in opcoes]
    if selecionadas:
        return selecionadas[:3]
    return opcoes[: min(3, len(opcoes))]


def render_sidebar(df: pd.DataFrame) -> dict:
    st.sidebar.header("Aparência")
    tema_nome = st.sidebar.selectbox(
        "Tema visual",
        list(TEMAS.keys()),
        index=0,
        help="Altera cores da interface e dos gráficos.",
    )

    st.sidebar.divider()
    st.sidebar.header("Filtros")
    modo = st.sidebar.radio("Modo", ["Explorar capital", "Comparar capitais"])

    regioes = ["Todas"] + sorted(df["regiao"].dropna().unique().tolist())
    regiao = st.sidebar.selectbox("Região", regioes)

    capitais_regiao = df["capital"].unique().tolist()
    if regiao != "Todas":
        capitais_regiao = sorted(df[df["regiao"] == regiao]["capital"].unique().tolist())

    opcoes_capital = sorted(capitais_regiao) + ["Média Nacional"]

    data_min = df["data"].min().date()
    data_max = df["data"].max().date()
    periodo = st.sidebar.slider(
        "Período histórico",
        min_value=data_min,
        max_value=data_max,
        value=(data_min, data_max),
        format="MM/YYYY",
    )

    cenarios = st.sidebar.multiselect(
        "Cenários de projeção",
        ["Otimista", "Moderado", "Conservador"],
        default=["Moderado", "Conservador"],
    )

    if modo == "Explorar capital":
        capital = st.sidebar.selectbox(
            "Capital",
            opcoes_capital,
            index=indice_capital_padrao(opcoes_capital),
            key=f"capital_{regiao}",
        )
        comparar = []
    else:
        capital = None
        comparar = st.sidebar.multiselect(
            "Capitais para comparar (até 3)",
            opcoes_capital,
            default=capitais_comparacao_padrao(opcoes_capital),
            max_selections=3,
            key=f"comparar_{regiao}",
        )

    return {
        "tema_nome": tema_nome,
        "modo": modo,
        "regiao": regiao,
        "capital": capital,
        "comparar": comparar,
        "periodo": periodo,
        "cenarios": cenarios,
    }


def render_kpis(df: pd.DataFrame, capital: str, data_ref: pd.Timestamp) -> None:
    serie = serie_capital(df, capital)
    ultimo = serie[serie["data"] == data_ref]
    if ultimo.empty:
        st.warning("Sem dados para o período selecionado.")
        return

    custo_atual = float(ultimo["custo"].iloc[0])
    variacao_anual = ultimo["variacao_anual_pct"].iloc[0] if "variacao_anual_pct" in ultimo else None

    ranking = ranking_ultimo_mes(df, data_ref)
    posicao = ranking[ranking["capital"] == capital]["posicao"]
    posicao_txt = f"{int(posicao.iloc[0])}º" if not posicao.empty and capital != "Média Nacional" else "—"

    media_nacional = float(df[df["data"] == data_ref]["custo"].mean())
    diff_media = custo_atual - media_nacional

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Custo atual", f"R$ {custo_atual:,.2f}")
    col2.metric(
        "Var. 12 meses",
        f"{variacao_anual:.1f}%" if pd.notna(variacao_anual) else "—",
    )
    col3.metric("Ranking", posicao_txt)
    col4.metric("vs média BR", f"R$ {diff_media:+,.2f}")


def render_projecoes_resumo(
    projecoes: pd.DataFrame,
    capital: str,
    cenarios: list[str],
) -> None:
    if not cenarios:
        return

    st.markdown('<p class="section-title">Projeção dez/2030</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="caption-mobile">Inflação composta a partir do último valor histórico.</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(cenarios))
    for col, cenario in zip(cols, cenarios):
        valor = projecao_dez_2030(projecoes, capital, cenario)
        col.metric(
            cenario,
            f"R$ {valor:,.2f}" if valor is not None else "—",
        )


def main() -> None:
    configurar_pagina()

    if not DADOS_PATH.exists():
        st.error(
            "Dados não encontrados. Execute o pipeline antes de abrir o dashboard:\n\n"
            "`python -c \"from src.load import executar_pipeline; executar_pipeline()\"`"
        )
        st.stop()

    df, projecoes, metricas = carregar_dados()
    filtros = render_sidebar(df)
    tema = aplicar_tema(filtros["tema_nome"])

    inicio = pd.Timestamp(filtros["periodo"][0])
    fim = pd.Timestamp(filtros["periodo"][1])
    df_periodo = filtrar_periodo(df, inicio, fim)
    data_ref = min(ultimo_mes(df_periodo), fim)

    render_hero(tema)

    if filtros["modo"] == "Explorar capital":
        capital = filtros["capital"]
        render_kpis(df_periodo, capital, data_ref)

        historico = filtrar_periodo(serie_capital(df, capital), inicio, fim)
        render_projecoes_resumo(projecoes, capital, filtros["cenarios"])

        st.markdown('<p class="section-title">Gráfico histórico e cenários</p>', unsafe_allow_html=True)
        st.plotly_chart(
            grafico_capital_com_projecao(
                historico,
                projecoes,
                capital,
                filtros["cenarios"],
                tema,
            ),
            use_container_width=True,
            config=CONFIG_PLOTLY,
        )

        serie_metrica = "São Luís" if capital == "São Luís" else "Média Nacional" if capital == "Média Nacional" else None
        if serie_metrica:
            st.markdown('<p class="section-title">Validação dos modelos</p>', unsafe_allow_html=True)
            st.plotly_chart(
                grafico_metricas(metricas, serie_metrica, tema),
                use_container_width=True,
                config=CONFIG_PLOTLY,
            )

    else:
        if not filtros["comparar"]:
            st.warning("Selecione ao menos uma capital para comparar.")
            st.stop()

        series = [
            filtrar_periodo(serie_capital(df, cap), inicio, fim)
            for cap in filtros["comparar"]
        ]
        st.markdown('<p class="section-title">Comparativo entre capitais</p>', unsafe_allow_html=True)
        st.plotly_chart(
            grafico_comparacao(series, "Comparativo de custo entre capitais", tema),
            use_container_width=True,
            config=CONFIG_PLOTLY,
        )

        st.markdown('<p class="section-title">Resumo do período</p>', unsafe_allow_html=True)
        resumo = []
        for cap in filtros["comparar"]:
            serie = serie_capital(df_periodo, cap)
            ultimo = serie[serie["data"] == data_ref]
            if ultimo.empty:
                continue
            var_anual = None
            if "variacao_anual_pct" in ultimo.columns:
                valor = ultimo["variacao_anual_pct"].iloc[0]
                if pd.notna(valor):
                    var_anual = round(float(valor), 2)
            resumo.append(
                {
                    "Capital": cap,
                    "Custo (R$)": round(float(ultimo["custo"].iloc[0]), 2),
                    "Var. 12 meses (%)": var_anual,
                }
            )
        st.dataframe(pd.DataFrame(resumo), use_container_width=True, hide_index=True)

    with st.expander("Metodologia e fontes"):
        st.markdown(
            """
            - **Fonte:** dados DIEESE (reais) com histórico híbrido calibrado quando necessário.
            - **Projeções (27 capitais + média nacional):** partem do último custo observado e aplicam
              inflação anual composta de 3% (Otimista), 4,5% (Moderado) e 6% (Conservador),
              com leve ajuste de sazonalidade mensal.
            - **Validação:** SARIMA e Prophet comparam previsões no período de teste (métricas disponíveis
              para São Luís e Média Nacional).
            - **Limitação:** projeções são estimativas de cenário, não previsões garantidas.
            - **Atualização:** execute o pipeline localmente para regenerar os CSVs em `outputs/`.
            """
        )


if __name__ == "__main__":
    main()
