"""Temas visuais do dashboard — Claro e Escuro."""

from __future__ import annotations

from typing import TypedDict


class Tema(TypedDict):
    nome: str
    primary: str
    primary_soft: str
    bg: str
    bg_secondary: str
    text: str
    text_muted: str
    card_bg: str
    card_border: str
    accent_light: str
    hero_title: str
    hero_subtitle: str
    hero_gradient: str
    shadow_sm: str
    shadow_md: str
    plotly_template: str
    grid: str
    destaque: str
    media: str
    comparacao: list[str]
    cenarios: dict[str, str]


TEMAS: dict[str, Tema] = {
    "Claro": {
        "nome": "Claro",
        "primary": "#166534",
        "primary_soft": "#dcfce7",
        "bg": "#f8faf9",
        "bg_secondary": "#ffffff",
        "text": "#0f172a",
        "text_muted": "#64748b",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "accent_light": "#ecfdf5",
        "hero_title": "#ffffff",
        "hero_subtitle": "rgba(255, 255, 255, 0.88)",
        "hero_gradient": "linear-gradient(135deg, #14532d 0%, #166534 45%, #059669 100%)",
        "shadow_sm": "0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04)",
        "shadow_md": "0 4px 16px rgba(15, 23, 42, 0.08), 0 2px 6px rgba(15, 23, 42, 0.04)",
        "plotly_template": "plotly_white",
        "grid": "#eef2f6",
        "destaque": "#166534",
        "media": "#1d4ed8",
        "comparacao": [
            "#166534",
            "#b91c1c",
            "#1d4ed8",
            "#7c3aed",
            "#b45309",
            "#0e7490",
            "#be185d",
        ],
        "cenarios": {
            "Otimista": "#059669",
            "Moderado": "#d97706",
            "Conservador": "#dc2626",
        },
    },
    "Escuro": {
        "nome": "Escuro",
        "primary": "#34d399",
        "primary_soft": "#064e3b",
        "bg": "#0c1017",
        "bg_secondary": "#131a24",
        "text": "#e8edf4",
        "text_muted": "#94a3b8",
        "card_bg": "#161f2c",
        "card_border": "#243044",
        "accent_light": "#0f2a22",
        "hero_title": "#ecfdf5",
        "hero_subtitle": "rgba(236, 253, 245, 0.78)",
        "hero_gradient": "linear-gradient(135deg, #0f172a 0%, #14532d 55%, #065f46 100%)",
        "shadow_sm": "0 1px 3px rgba(0, 0, 0, 0.35)",
        "shadow_md": "0 8px 24px rgba(0, 0, 0, 0.45)",
        "plotly_template": "plotly_dark",
        "grid": "#1e293b",
        "destaque": "#34d399",
        "media": "#60a5fa",
        "comparacao": [
            "#34d399",
            "#f87171",
            "#60a5fa",
            "#c084fc",
            "#fbbf24",
            "#22d3ee",
            "#f472b6",
        ],
        "cenarios": {
            "Otimista": "#34d399",
            "Moderado": "#fbbf24",
            "Conservador": "#f87171",
        },
    },
}


def obter_tema(nome: str) -> Tema:
    return TEMAS.get(nome, TEMAS["Claro"])


def css_tema(tema: Tema) -> str:
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}

        .stApp {{
            background: {tema["bg"]};
            color: {tema["text"]};
        }}

        section[data-testid="stMain"] .block-container {{
            padding-top: 1.5rem;
            max-width: 1200px;
        }}

        [data-testid="stSidebar"] {{
            background: {tema["bg_secondary"]};
            border-right: 1px solid {tema["card_border"]};
            box-shadow: {tema["shadow_sm"]};
        }}

        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1.25rem;
        }}

        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {{
            color: {tema["text"]} !important;
        }}

        [data-testid="stSidebar"] hr {{
            border-color: {tema["card_border"]};
            opacity: 0.7;
        }}

        [data-testid="stMetric"] {{
            background: {tema["card_bg"]};
            border: 1px solid {tema["card_border"]};
            border-radius: 14px;
            padding: 14px 18px;
            box-shadow: {tema["shadow_sm"]};
            transition: box-shadow 0.2s ease, transform 0.2s ease;
        }}

        [data-testid="stMetric"]:hover {{
            box-shadow: {tema["shadow_md"]};
        }}

        [data-testid="stMetricLabel"] {{
            color: {tema["text_muted"]} !important;
            font-size: 0.82rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.01em;
        }}

        [data-testid="stMetricValue"] {{
            color: {tema["primary"]} !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }}

        .dashboard-hero {{
            background: {tema["hero_gradient"]};
            border-radius: 16px;
            padding: 1.6rem 1.85rem;
            margin-bottom: 1.75rem;
            border: 1px solid rgba(255, 255, 255, 0.12);
            box-shadow: {tema["shadow_md"]};
            position: relative;
            overflow: hidden;
        }}

        .dashboard-hero::before {{
            content: "";
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 85% 15%, rgba(255,255,255,0.14) 0%, transparent 55%);
            pointer-events: none;
        }}

        .dashboard-hero h1 {{
            color: {tema["hero_title"]};
            margin: 0;
            font-size: 1.85rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            position: relative;
        }}

        .dashboard-hero p {{
            color: {tema["hero_subtitle"]};
            margin: 0.45rem 0 0 0;
            font-size: 0.95rem;
            font-weight: 400;
            position: relative;
        }}

        .section-title {{
            font-size: 1.05rem;
            font-weight: 600;
            color: {tema["text"]};
            letter-spacing: -0.01em;
            margin: 1.25rem 0 0.65rem 0;
            padding-bottom: 0.35rem;
            border-bottom: 2px solid {tema["primary_soft"] if tema["nome"] == "Claro" else tema["card_border"]};
            display: inline-block;
        }}

        .caption-mobile,
        .stCaption {{
            color: {tema["text_muted"]} !important;
            font-size: 0.875rem !important;
            line-height: 1.5;
        }}

        div[data-testid="stExpander"] {{
            border: 1px solid {tema["card_border"]};
            border-radius: 14px;
            background: {tema["card_bg"]};
            box-shadow: {tema["shadow_sm"]};
            overflow: hidden;
        }}

        div[data-testid="stPlotlyChart"] {{
            background: {tema["card_bg"]};
            border: 1px solid {tema["card_border"]};
            border-radius: 14px;
            padding: 0.35rem;
            box-shadow: {tema["shadow_sm"]};
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid {tema["card_border"]};
            border-radius: 14px;
            overflow: hidden;
            box-shadow: {tema["shadow_sm"]};
        }}

        .stButton > button {{
            border-radius: 10px;
            font-weight: 500;
            transition: all 0.15s ease;
        }}

        .stButton > button[kind="primary"],
        .stButton > button[kind="secondary"] {{
            border-color: {tema["card_border"]};
        }}

        .stButton > button:hover {{
            border-color: {tema["primary"]};
            color: {tema["primary"]};
        }}

        div[data-testid="stAlert"] {{
            border-radius: 12px;
            border: 1px solid {tema["card_border"]};
        }}

        .mobile-hint {{
            display: none;
            background: {tema["accent_light"]};
            color: {tema["text"]};
            border: 1px solid {tema["card_border"]};
            border-radius: 12px;
            padding: 0.7rem 1rem;
            margin-bottom: 1rem;
            font-size: 0.875rem;
            text-align: center;
        }}

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {{
            border-radius: 10px !important;
            border-color: {tema["card_border"]} !important;
            background-color: {tema["card_bg"]} !important;
        }}

        .stRadio > div {{
            gap: 0.5rem;
        }}

        .stRadio label {{
            font-weight: 500 !important;
        }}

        @media (max-width: 768px) {{
            .mobile-hint {{
                display: block;
            }}
            .dashboard-hero {{
                padding: 1.1rem 1.2rem;
                margin-bottom: 1.25rem;
                border-radius: 14px;
            }}
            .dashboard-hero h1 {{
                font-size: 1.4rem;
            }}
            .dashboard-hero p {{
                font-size: 0.85rem;
            }}
            section[data-testid="stMain"] .block-container {{
                padding-top: 0.85rem;
                padding-left: 0.85rem;
                padding-right: 0.85rem;
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
            }}
            [data-testid="stMetricLabel"] {{
                font-size: 0.78rem !important;
            }}
            [data-testid="stMetricValue"] {{
                font-size: 1.1rem !important;
            }}
            div[data-testid="stPlotlyChart"],
            div[data-testid="stDataFrame"] {{
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
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
                font-size: 1.25rem;
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
        return dict(t=52, b=100, l=52, r=20)
    return dict(t=64, b=48, l=64, r=28)


def layout_plotly(fig, tema: Tema, **kwargs):
    """Aplica estilo do tema em um gráfico Plotly."""
    legend = _mesclar_dict(
        {"font": {"color": tema["text"], "family": "Inter, sans-serif"}},
        kwargs.pop("legend", {}),
    )
    xaxis = _mesclar_dict(
        {
            "gridcolor": tema["grid"],
            "linecolor": tema["card_border"],
            "zerolinecolor": tema["grid"],
            "tickfont": {"color": tema["text_muted"]},
            "titlefont": {"color": tema["text"]},
        },
        kwargs.pop("xaxis", {}),
    )
    yaxis = _mesclar_dict(
        {
            "gridcolor": tema["grid"],
            "linecolor": tema["card_border"],
            "zerolinecolor": tema["grid"],
            "tickfont": {"color": tema["text_muted"]},
            "titlefont": {"color": tema["text"]},
        },
        kwargs.pop("yaxis", {}),
    )

    fig.update_layout(
        template=tema["plotly_template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=tema["text"], family="Inter, sans-serif"),
        title_font=dict(color=tema["text"], size=16, family="Inter, sans-serif"),
        legend=legend,
        xaxis=xaxis,
        yaxis=yaxis,
        **kwargs,
    )
    return fig
