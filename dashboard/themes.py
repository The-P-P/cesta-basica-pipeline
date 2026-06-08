"""Temas visuais do dashboard."""

from __future__ import annotations

from typing import TypedDict


class Tema(TypedDict):
    nome: str
    primary: str
    bg: str
    bg_secondary: str
    text: str
    text_muted: str
    card_bg: str
    card_border: str
    accent_light: str
    plotly_template: str
    grid: str
    sao_luis: str
    media: str
    comparacao: list[str]
    cenarios: dict[str, str]


TEMAS: dict[str, Tema] = {
    "Claro (TCC)": {
        "nome": "Claro (TCC)",
        "primary": "#1a5c38",
        "bg": "#ffffff",
        "bg_secondary": "#f0f4f1",
        "text": "#1a1a1a",
        "text_muted": "#5c6b63",
        "card_bg": "#f7faf8",
        "card_border": "#c8ddd0",
        "accent_light": "#e8f3ec",
        "plotly_template": "plotly_white",
        "grid": "#e2ebe6",
        "sao_luis": "#1a5c38",
        "media": "#2980b9",
        "comparacao": ["#1a5c38", "#c0392b", "#2980b9", "#8e44ad", "#d35400"],
        "cenarios": {
            "Otimista": "#27ae60",
            "Moderado": "#e67e22",
            "Conservador": "#c0392b",
        },
    },
    "Escuro": {
        "nome": "Escuro",
        "primary": "#3ddc84",
        "bg": "#0e1117",
        "bg_secondary": "#161b22",
        "text": "#f0f3f1",
        "text_muted": "#9aa8a0",
        "card_bg": "#1c2128",
        "card_border": "#30363d",
        "accent_light": "#1a2e24",
        "plotly_template": "plotly_dark",
        "grid": "#2d333b",
        "sao_luis": "#3ddc84",
        "media": "#58a6ff",
        "comparacao": ["#3ddc84", "#ff7b72", "#58a6ff", "#d2a8ff", "#ffa657"],
        "cenarios": {
            "Otimista": "#3fb950",
            "Moderado": "#d29922",
            "Conservador": "#f85149",
        },
    },
    "Azul Institucional": {
        "nome": "Azul Institucional",
        "primary": "#1e3a5f",
        "bg": "#f8fafc",
        "bg_secondary": "#eef2f7",
        "text": "#0f172a",
        "text_muted": "#64748b",
        "card_bg": "#ffffff",
        "card_border": "#cbd5e1",
        "accent_light": "#e8eef5",
        "plotly_template": "plotly_white",
        "grid": "#e2e8f0",
        "sao_luis": "#1e3a5f",
        "media": "#2563eb",
        "comparacao": ["#1e3a5f", "#dc2626", "#2563eb", "#7c3aed", "#ea580c"],
        "cenarios": {
            "Otimista": "#16a34a",
            "Moderado": "#d97706",
            "Conservador": "#dc2626",
        },
    },
    "Alto Contraste": {
        "nome": "Alto Contraste",
        "primary": "#000000",
        "bg": "#ffffff",
        "bg_secondary": "#f5f5f5",
        "text": "#000000",
        "text_muted": "#333333",
        "card_bg": "#ffffff",
        "card_border": "#000000",
        "accent_light": "#eeeeee",
        "plotly_template": "simple_white",
        "grid": "#cccccc",
        "sao_luis": "#000000",
        "media": "#0047ab",
        "comparacao": ["#000000", "#cc0000", "#0047ab", "#6600cc", "#cc6600"],
        "cenarios": {
            "Otimista": "#006600",
            "Moderado": "#cc6600",
            "Conservador": "#cc0000",
        },
    },
}


def obter_tema(nome: str) -> Tema:
    return TEMAS.get(nome, TEMAS["Claro (TCC)"])


def css_tema(tema: Tema) -> str:
    return f"""
    <style>
        .stApp {{
            background-color: {tema["bg"]};
            color: {tema["text"]};
        }}
        [data-testid="stSidebar"] {{
            background-color: {tema["bg_secondary"]};
            border-right: 1px solid {tema["card_border"]};
        }}
        [data-testid="stSidebar"] * {{
            color: {tema["text"]} !important;
        }}
        [data-testid="stMetric"] {{
            background-color: {tema["card_bg"]};
            border: 1px solid {tema["card_border"]};
            border-radius: 10px;
            padding: 12px 16px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }}
        [data-testid="stMetricLabel"] {{
            color: {tema["text_muted"]} !important;
        }}
        [data-testid="stMetricValue"] {{
            color: {tema["primary"]} !important;
        }}
        .dashboard-hero {{
            background: linear-gradient(135deg, {tema["primary"]} 0%, {tema["accent_light"]} 100%);
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid {tema["card_border"]};
        }}
        .dashboard-hero h1 {{
            color: {tema["bg"] if tema["nome"] != "Alto Contraste" else tema["text"]};
            margin: 0;
            font-size: 1.75rem;
        }}
        .dashboard-hero p {{
            color: {tema["bg"] if tema["nome"] not in ("Alto Contraste", "Claro (TCC)") else tema["text_muted"]};
            margin: 0.35rem 0 0 0;
            opacity: 0.92;
        }}
        div[data-testid="stExpander"] {{
            border: 1px solid {tema["card_border"]};
            border-radius: 10px;
            background-color: {tema["card_bg"]};
        }}
        .stButton > button[kind="primary"] {{
            background-color: {tema["primary"]};
            border-color: {tema["primary"]};
        }}
        .mobile-hint {{
            display: none;
            background-color: {tema["accent_light"]};
            color: {tema["text"]};
            border: 1px solid {tema["card_border"]};
            border-radius: 8px;
            padding: 0.65rem 0.9rem;
            margin-bottom: 1rem;
            font-size: 0.9rem;
            text-align: center;
        }}
        .section-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: {tema["text"]};
            margin: 0.5rem 0 0.75rem 0;
        }}
        .caption-mobile {{
            color: {tema["text_muted"]};
            font-size: 0.85rem;
            line-height: 1.4;
            margin-bottom: 0.5rem;
        }}

        /* --- Mobile / tablet --- */
        @media (max-width: 768px) {{
            .mobile-hint {{
                display: block;
            }}
            .dashboard-hero {{
                padding: 0.9rem 1rem;
                margin-bottom: 1rem;
                border-radius: 10px;
            }}
            .dashboard-hero h1 {{
                font-size: 1.35rem;
                line-height: 1.25;
            }}
            .dashboard-hero p {{
                font-size: 0.82rem;
                line-height: 1.35;
            }}
            section[data-testid="stMain"] .block-container {{
                padding-top: 0.75rem;
                padding-left: 0.75rem;
                padding-right: 0.75rem;
                max-width: 100%;
            }}
            section[data-testid="stMain"] div[data-testid="stHorizontalBlock"] {{
                gap: 0.5rem;
                flex-wrap: wrap !important;
            }}
            section[data-testid="stMain"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
                width: calc(50% - 0.25rem) !important;
                flex: 1 1 calc(50% - 0.25rem) !important;
                min-width: calc(50% - 0.25rem) !important;
            }}
            [data-testid="stMetric"] {{
                padding: 10px 12px;
                margin-bottom: 0.25rem;
            }}
            [data-testid="stMetricLabel"] {{
                font-size: 0.78rem !important;
                white-space: normal !important;
                line-height: 1.2 !important;
            }}
            [data-testid="stMetricValue"] {{
                font-size: 1.15rem !important;
            }}
            div[data-testid="stPlotlyChart"] {{
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }}
            div[data-testid="stDataFrame"] {{
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }}
            div[data-testid="stExpander"] {{
                font-size: 0.92rem;
            }}
            [data-testid="stSidebar"] {{
                min-width: min(85vw, 300px) !important;
            }}
        }}

        @media (max-width: 480px) {{
            section[data-testid="stMain"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }}
            .dashboard-hero h1 {{
                font-size: 1.2rem;
            }}
            [data-testid="stMetricValue"] {{
                font-size: 1.05rem !important;
            }}
        }}
    </style>
    """


def _mesclar_dict(base: dict, extra: dict) -> dict:
    resultado = base.copy()
    for chave, valor in extra.items():
        if isinstance(valor, dict) and isinstance(resultado.get(chave), dict):
            resultado[chave] = {**resultado[chave], **valor}
        else:
            resultado[chave] = valor
    return resultado


def legenda_responsiva(font_size: int = 11) -> dict:
    """Legenda abaixo do gráfico — melhor em telas estreitas."""
    return {
        "orientation": "h",
        "yanchor": "top",
        "y": -0.28,
        "xanchor": "center",
        "x": 0.5,
        "font": {"size": font_size},
    }


def margens_grafico(mobile_friendly: bool = True) -> dict:
    if mobile_friendly:
        return dict(t=48, b=100, l=48, r=16)
    return dict(t=60, b=40, l=60, r=24)


def layout_plotly(fig, tema: Tema, **kwargs):
    """Aplica estilo do tema em um gráfico Plotly."""
    legend = _mesclar_dict(
        {"font": {"color": tema["text"]}},
        kwargs.pop("legend", {}),
    )
    xaxis = _mesclar_dict(
        {
            "gridcolor": tema["grid"],
            "linecolor": tema["card_border"],
            "zerolinecolor": tema["grid"],
        },
        kwargs.pop("xaxis", {}),
    )
    yaxis = _mesclar_dict(
        {
            "gridcolor": tema["grid"],
            "linecolor": tema["card_border"],
            "zerolinecolor": tema["grid"],
        },
        kwargs.pop("yaxis", {}),
    )

    fig.update_layout(
        template=tema["plotly_template"],
        paper_bgcolor=tema["bg"],
        plot_bgcolor=tema["card_bg"],
        font=dict(color=tema["text"]),
        title_font=dict(color=tema["text"]),
        legend=legend,
        xaxis=xaxis,
        yaxis=yaxis,
        **kwargs,
    )
    return fig
