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


def grafico_comparacao(
    dfs: list[pd.DataFrame],
    titulo: str,
    tema: dict,
    projecoes: pd.DataFrame | None = None,
    cenarios: list[str] | None = None,
) -> go.Figure:
    fig = go.Figure()
    paleta = (
        tema["comparacao"]
        + px.colors.qualitative.Alphabet
        + px.colors.qualitative.Dark24
        + px.colors.qualitative.Set3
    )
    cenarios = cenarios or []

    for i, serie in enumerate(dfs):
        capital = serie["capital"].iloc[0]
        cor = paleta[i % len(paleta)]

        fig.add_trace(
            go.Scatter(
                x=serie["data"],
                y=serie["custo"],
                mode="lines",
                name=capital,
                legendgroup=capital,
                line=dict(color=cor, width=2 if len(dfs) <= 5 else 1.5),
            )
        )

        if projecoes is not None and cenarios:
            for cenario in cenarios:
                proj = projecoes[
                    (projecoes["capital"] == capital) & (projecoes["cenario"] == cenario)
                ].sort_values("data")
                if proj.empty:
                    continue
                fig.add_trace(
                    go.Scatter(
                        x=proj["data"],
                        y=proj["custo_projetado"],
                        mode="lines",
                        name=f"{capital} — {cenario}",
                        legendgroup=capital,
                        showlegend=len(cenarios) == 1,
                        line=dict(color=cor, width=1.5, dash="dash"),
                    )
                )

    if cenarios and projecoes is not None:
        fig.add_vline(
            x=DATA_PROJECAO_INICIO,
            line_dash="dot",
            line_color=tema["text_muted"],
            annotation_text="Projeções",
            annotation_position="top right",
            annotation_font_color=tema["text_muted"],
        )

    altura = 480 if cenarios else (420 if len(dfs) <= 8 else 520)
    return layout_plotly(
        fig,
        tema,
        title=titulo,
        xaxis_title="Data",
        yaxis_title="Custo (R$)",
        hovermode="x unified",
        legend=legenda_responsiva(font_size=10 if len(dfs) > 8 else 11),
        height=altura,
        margin=margens_grafico(mobile_friendly=len(dfs) <= 12),
    )


def grafico_regiao_com_projecao(
    df: pd.DataFrame,
    projecoes: pd.DataFrame,
    capitais: list[str],
    cenarios: list[str],
    regiao: str,
    inicio: pd.Timestamp,
    fim: pd.Timestamp,
    tema: dict,
) -> go.Figure:
    """Gráfico com histórico e projeções de todas as capitais de uma região."""
    fig = go.Figure()
    paleta = (
        tema["comparacao"]
        + px.colors.qualitative.Alphabet
        + px.colors.qualitative.Dark24
    )

    for i, capital in enumerate(capitais):
        cor = paleta[i % len(paleta)]
        historico = filtrar_periodo(serie_capital(df, capital), inicio, fim)

        fig.add_trace(
            go.Scatter(
                x=historico["data"],
                y=historico["custo"],
                mode="lines",
                name=capital,
                legendgroup=capital,
                line=dict(color=cor, width=2.5),
            )
        )

        for cenario in cenarios:
            proj = projecoes[
                (projecoes["capital"] == capital) & (projecoes["cenario"] == cenario)
            ].sort_values("data")
            if proj.empty:
                continue
            fig.add_trace(
                go.Scatter(
                    x=proj["data"],
                    y=proj["custo_projetado"],
                    mode="lines",
                    name=f"{capital} — {cenario}",
                    legendgroup=capital,
                    showlegend=False,
                    line=dict(color=cor, width=1.5, dash="dash"),
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
        title=f"Evolução e projeção — região {regiao}",
        xaxis_title="Data",
        yaxis_title="Custo (R$)",
        hovermode="x unified",
        legend=legenda_responsiva(font_size=10),
        height=480,
        margin=margens_grafico(),
    )


def render_kpis_regiao(df: pd.DataFrame, regiao: str, data_ref: pd.Timestamp) -> None:
    snapshot = df[(df["data"] == data_ref) & (df["regiao"] == regiao)]
    if snapshot.empty:
        st.warning("Sem dados para a região selecionada.")
        return

    media_regiao = float(snapshot["custo"].mean())
    media_nacional = float(df[df["data"] == data_ref]["custo"].mean())
    mais_cara = snapshot.loc[snapshot["custo"].idxmax()]
    mais_barata = snapshot.loc[snapshot["custo"].idxmin()]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Capitais na região", str(len(snapshot)))
    col2.metric("Média regional", f"R$ {media_regiao:,.2f}")
    col3.metric("Mais cara", f"{mais_cara['capital']}")
    col4.metric("vs média BR", f"R$ {media_regiao - media_nacional:+,.2f}")
    st.caption(
        f"Faixa regional: R$ {mais_barata['custo']:,.2f} ({mais_barata['capital']}) "
        f"– R$ {mais_cara['custo']:,.2f} ({mais_cara['capital']})"
    )


def render_projecoes_regiao(
    projecoes: pd.DataFrame,
    capitais: list[str],
    cenarios: list[str],
) -> None:
    if not cenarios:
        return

    st.markdown('<p class="section-title">Projeção dez/2030 por capital</p>', unsafe_allow_html=True)
    linhas = []
    for capital in capitais:
        linha = {"Capital": capital}
        for cenario in cenarios:
            valor = projecao_dez_2030(projecoes, capital, cenario)
            linha[cenario] = round(valor, 2) if valor is not None else None
        linhas.append(linha)
    st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)


def cor_historico_capital(capital: str, tema: dict) -> str:
    if capital == "Média Nacional":
        return tema["media"]
    return tema["destaque"]


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
        color_discrete_map={"SARIMA": tema["media"], "Prophet": tema["destaque"]},
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


def obter_todas_capitais(df: pd.DataFrame) -> list[str]:
    """Retorna todas as capitais disponíveis nos dados, ordenadas alfabeticamente."""
    return sorted(df["capital"].dropna().unique().tolist())


def obter_opcoes_capitais(df: pd.DataFrame) -> list[str]:
    """Capitais + média nacional agregada."""
    return obter_todas_capitais(df) + ["Média Nacional"]


def capitais_por_regiao(df: pd.DataFrame, regiao: str) -> list[str]:
    if regiao == "Todas":
        return obter_todas_capitais(df)
    return sorted(df[df["regiao"] == regiao]["capital"].dropna().unique().tolist())


def indice_capital_padrao(opcoes: list[str], preferida: str = "Média Nacional") -> int:
    return opcoes.index(preferida) if preferida in opcoes else 0


def capitais_comparacao_padrao(opcoes: list[str]) -> list[str]:
    preferidas = ["São Paulo", "Brasília", "Média Nacional"]
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
    regiao = st.sidebar.selectbox(
        "Região",
        regioes,
        help="Com uma região selecionada, o gráfico exibe todas as capitais dela.",
    )

    opcoes_capital = obter_opcoes_capitais(df)
    n_capitais = len(obter_todas_capitais(df))
    st.sidebar.caption(f"{n_capitais} capitais + média nacional disponíveis")

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
        if regiao == "Todas":
            capital = st.sidebar.selectbox(
                "Capital",
                opcoes_capital,
                index=indice_capital_padrao(opcoes_capital),
                key="capital_todas",
            )
        else:
            capital = None
            capitais_regiao = capitais_por_regiao(df, regiao)
            st.sidebar.info(
                f"Exibindo **{len(capitais_regiao)} capitais** da região **{regiao}** no gráfico."
            )
        comparar = []
    else:
        capital = None
        comparar_key = f"comparar_{regiao}"

        if comparar_key not in st.session_state:
            if regiao != "Todas":
                st.session_state[comparar_key] = capitais_por_regiao(df, regiao)
            else:
                st.session_state[comparar_key] = capitais_comparacao_padrao(opcoes_capital)

        col_todas, col_regiao, col_limpar = st.sidebar.columns(3)
        if col_todas.button("Todas", use_container_width=True):
            st.session_state[comparar_key] = opcoes_capital
        if col_regiao.button("Região", use_container_width=True):
            st.session_state[comparar_key] = capitais_por_regiao(df, regiao)
        if col_limpar.button("Limpar", use_container_width=True):
            st.session_state[comparar_key] = []

        comparar = st.sidebar.multiselect(
            "Capitais para comparar",
            opcoes_capital,
            key=comparar_key,
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


def render_ranking_todas_capitais(
    df: pd.DataFrame,
    data_ref: pd.Timestamp,
    regiao: str,
) -> None:
    ranking = ranking_ultimo_mes(df, data_ref)
    if regiao != "Todas":
        ranking = (
            ranking[ranking["regiao"] == regiao]
            .sort_values("custo", ascending=False)
            .reset_index(drop=True)
        )
        ranking["posicao"] = ranking.index + 1

    media_nacional = float(df[df["data"] == data_ref]["custo"].mean())
    tabela = ranking[["posicao", "capital", "estado", "regiao", "custo"]].copy()
    tabela["custo"] = tabela["custo"].round(2)
    tabela["vs média BR (R$)"] = (tabela["custo"] - media_nacional).round(2)
    tabela.columns = ["Pos.", "Capital", "UF", "Região", "Custo (R$)", "vs média BR (R$)"]

    titulo = (
        "Ranking de todas as capitais"
        if regiao == "Todas"
        else f"Ranking — região {regiao}"
    )
    st.markdown(f'<p class="section-title">{titulo}</p>', unsafe_allow_html=True)
    st.dataframe(tabela, use_container_width=True, hide_index=True)


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
        if filtros["regiao"] != "Todas":
            regiao = filtros["regiao"]
            capitais_regiao = capitais_por_regiao(df, regiao)
            render_kpis_regiao(df_periodo, regiao, data_ref)
            render_projecoes_regiao(projecoes, capitais_regiao, filtros["cenarios"])

            st.markdown(
                '<p class="section-title">Gráfico histórico e cenários — região</p>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(
                grafico_regiao_com_projecao(
                    df,
                    projecoes,
                    capitais_regiao,
                    filtros["cenarios"],
                    regiao,
                    inicio,
                    fim,
                    tema,
                ),
                use_container_width=True,
                config=CONFIG_PLOTLY,
            )
        else:
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

            serie_metrica = "Média Nacional" if capital == "Média Nacional" else None
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
        if filtros["cenarios"]:
            st.caption(
                "Linhas sólidas: histórico. Linhas tracejadas: projeções dos cenários selecionados."
            )
        st.plotly_chart(
            grafico_comparacao(
                series,
                "Comparativo de custo entre capitais",
                tema,
                projecoes=projecoes,
                cenarios=filtros["cenarios"],
            ),
            use_container_width=True,
            config=CONFIG_PLOTLY,
        )

        if filtros["cenarios"]:
            render_projecoes_regiao(projecoes, filtros["comparar"], filtros["cenarios"])

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

    render_ranking_todas_capitais(df_periodo, data_ref, filtros["regiao"])

    with st.expander("Metodologia e fontes"):
        st.markdown(
            """
            - **Fonte:** dados DIEESE (reais) com histórico híbrido calibrado quando necessário.
            - **Projeções (27 capitais + média nacional):** partem do último custo observado e aplicam
              inflação anual composta de 3% (Otimista), 4,5% (Moderado) e 6% (Conservador),
              com leve ajuste de sazonalidade mensal.
            - **Validação:** SARIMA e Prophet comparam previsões no período de teste (métricas disponíveis
              para a média nacional agregada).
            - **Limitação:** projeções são estimativas de cenário, não previsões garantidas.
            - **Atualização:** execute o pipeline localmente para regenerar os CSVs em `outputs/`.
            """
        )


if __name__ == "__main__":
    main()
