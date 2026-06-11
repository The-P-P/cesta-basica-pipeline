"""
Módulo de Análise Exploratória de Dados (EDA) com visualizações para slides.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose

from transform import calcular_media_nacional

# Configuração visual acadêmica
plt.style.use("seaborn-v0_8-whitegrid")

# Paleta consistente
COR_DESTAQUE = "#2980b9"
COR_SAO_PAULO = "#c0392b"
COR_MEDIA_NACIONAL = "#2980b9"
COR_BAR_EXTREMO = "#1a5c38"

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs" / "graficos"
DPI = 150
FONTE_DADOS = "Fonte: DIEESE (dados reais até mar/2026)"


def _configurar_figura(figsize=(14, 8)):
    """Configura figura com estilo acadêmico."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    return fig, ax


def _salvar_figura(fig, nome_arquivo: str):
    """Salva figura em PNG de alta resolução."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    caminho = OUTPUT_DIR / nome_arquivo
    fig.savefig(caminho, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Gráfico salvo: {caminho}")
    return caminho


def grafico_evolucao_historica(df: pd.DataFrame) -> Path:
    """
    Gráfico 1 — Evolução histórica nacional (2020-2026).
    Destaque: Média Nacional (azul) e São Paulo (vermelho) como referência.
    """
    fig, ax = _configurar_figura((16, 9))
    media_nacional = calcular_media_nacional(df)

    # Todas as capitais em cinza claro
    for capital in df["capital"].unique():
        if capital != "São Paulo":
            serie = df[df["capital"] == capital]
            ax.plot(serie["data"], serie["custo"], color="gray", alpha=0.3, linewidth=0.8)

    # Destaques
    sp = df[df["capital"] == "São Paulo"]
    ax.plot(sp["data"], sp["custo"], color=COR_SAO_PAULO, linewidth=2.5, label="São Paulo")
    ax.plot(
        media_nacional["data"],
        media_nacional["media_nacional"],
        color=COR_MEDIA_NACIONAL,
        linewidth=2.5,
        linestyle="-",
        label="Média Nacional",
    )

    ax.set_title(
        "Evolução do Custo da Cesta Básica no Brasil (2020–2026)",
        fontsize=16,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Data", fontsize=12)
    ax.set_ylabel("Custo (R$)", fontsize=12)

    # Em modo híbrido, marca início dos dados reais
    if "fonte_dado" in df.columns and (df["fonte_dado"] == "real_dieese").any():
        data_inicio_real = df.loc[df["fonte_dado"] == "real_dieese", "data"].min()
        ax.axvline(data_inicio_real, color="#34495e", linestyle=":", linewidth=1.6, alpha=0.8)
        ax.text(
            data_inicio_real,
            ax.get_ylim()[1] * 0.98,
            " Início dos dados reais",
            fontsize=10,
            color="#34495e",
            va="top",
        )

    ax.legend(loc="upper left", fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    fig.text(0.12, 0.02, FONTE_DADOS, fontsize=9, color="gray")

    return _salvar_figura(fig, "01_evolucao_historica_nacional.png")


def grafico_heatmap_capitais(df: pd.DataFrame) -> Path:
    """
    Gráfico 2 — Heatmap por capital e ano.
    """
    fig, ax = _configurar_figura((14, 12))

    df_copy = df.copy()
    df_copy["ano"] = df_copy["data"].dt.year

    # Custo médio por capital e ano
    pivot = df_copy.groupby(["capital", "ano"])["custo"].mean().unstack()

    # Ordenar capitais por custo médio geral
    ordem = pivot.mean(axis=1).sort_values(ascending=False).index
    pivot = pivot.loc[ordem]

    sns.heatmap(
        pivot,
        cmap="YlOrRd",
        annot=True,
        fmt=".0f",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Custo Médio (R$)"},
    )

    ax.set_title(
        "Variação do Custo da Cesta Básica por Capital (R$)",
        fontsize=16,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Ano", fontsize=12)
    ax.set_ylabel("Capital", fontsize=12)
    fig.text(0.12, 0.02, FONTE_DADOS, fontsize=9, color="gray")

    return _salvar_figura(fig, "02_heatmap_capitais.png")


def grafico_decomposicao_media_nacional(df: pd.DataFrame) -> Path:
    """
    Gráfico 3 — Decomposição da série temporal da média nacional.
    """
    media_nacional = calcular_media_nacional(df)
    serie = media_nacional.set_index("data")["media_nacional"].asfreq("MS")

    decomp = seasonal_decompose(serie, model="additive", period=12)

    fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
    fig.patch.set_facecolor("white")

    componentes = [
        (decomp.observed, "Série Original", COR_DESTAQUE),
        (decomp.trend, "Tendência", COR_MEDIA_NACIONAL),
        (decomp.seasonal, "Sazonalidade", "#e67e22"),
        (decomp.resid, "Resíduo", "#7f8c8d"),
    ]

    for ax, (comp, titulo, cor) in zip(axes, componentes):
        ax.plot(comp.index, comp.values, color=cor, linewidth=1.5)
        ax.set_ylabel(titulo, fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor("white")

    axes[0].set_title(
        "Decomposição da Série Temporal — Média Nacional",
        fontsize=16,
        fontweight="bold",
        pad=15,
    )
    axes[-1].set_xlabel("Data", fontsize=12)
    fig.text(0.12, 0.02, FONTE_DADOS, fontsize=9, color="gray")
    plt.tight_layout()

    return _salvar_figura(fig, "03_decomposicao_media_nacional.png")


def grafico_boxplot_regional(df: pd.DataFrame) -> Path:
    """
    Gráfico 4 — Boxplot comparativo por região.
    """
    fig, ax = _configurar_figura((14, 8))

    ordem_regioes = ["Norte", "Nordeste", "Centro-Oeste", "Sul", "Sudeste"]
    cores_regioes = {
        "Norte": "#3498db",
        "Nordeste": "#16a085",
        "Centro-Oeste": "#9b59b6",
        "Sul": "#2ecc71",
        "Sudeste": COR_SAO_PAULO,
    }

    palette = [cores_regioes.get(r, "gray") for r in ordem_regioes]

    sns.boxplot(
        data=df,
        x="regiao",
        y="custo",
        order=ordem_regioes,
        palette=palette,
        ax=ax,
        width=0.6,
    )

    # Marcar média nacional no período
    media_geral = df["custo"].mean()
    ax.axhline(
        media_geral,
        color=COR_MEDIA_NACIONAL,
        linestyle="--",
        linewidth=1.5,
        label=f"Média nacional (R$ {media_geral:,.0f})".replace(",", "."),
    )

    ax.set_title(
        "Distribuição de Preços por Região (2020–2026)",
        fontsize=16,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Região", fontsize=12)
    ax.set_ylabel("Custo (R$)", fontsize=12)
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")
    fig.text(0.12, 0.02, FONTE_DADOS, fontsize=9, color="gray")

    return _salvar_figura(fig, "04_boxplot_regional.png")


def grafico_ranking_capitais(df: pd.DataFrame) -> Path:
    """
    Gráfico 5 — Ranking horizontal de capitais no último mês disponível.
    """
    fig, ax = _configurar_figura((14, 12))

    data_ref = df["data"].max()
    mes_ref = df[df["data"] == data_ref]
    ranking = mes_ref.sort_values("custo", ascending=True)
    label_mes = data_ref.strftime("%b/%Y")

    media_ref = ranking["custo"].mean()
    cores = [
        COR_BAR_EXTREMO if abs(c - media_ref) == abs(ranking["custo"] - media_ref).min()
        else "#95a5a6"
        for c in ranking["custo"]
    ]

    bars = ax.barh(ranking["capital"], ranking["custo"], color=cores, edgecolor="white")

    # Anotar valores nas barras
    for bar, valor in zip(bars, ranking["custo"]):
        ax.text(
            bar.get_width() + 5,
            bar.get_y() + bar.get_height() / 2,
            f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            va="center",
            fontsize=9,
        )

    ax.axvline(
        media_ref,
        color=COR_MEDIA_NACIONAL,
        linestyle="--",
        linewidth=1.5,
        label=f"Média nacional (R$ {media_ref:,.2f})".replace(",", "X").replace(".", ",").replace("X", "."),
    )

    ax.set_title(
        f"Custo da Cesta Básica por Capital — {label_mes}",
        fontsize=16,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Custo (R$)", fontsize=12)
    ax.set_ylabel("Capital", fontsize=12)
    ax.grid(True, alpha=0.3, axis="x")

    patch_media = mpatches.Patch(color=COR_MEDIA_NACIONAL, label="Referência: média nacional")
    patch_outras = mpatches.Patch(color="#95a5a6", label="Demais capitais")
    ax.legend(handles=[patch_media, patch_outras], loc="lower right")
    fig.text(0.12, 0.02, FONTE_DADOS, fontsize=9, color="gray")

    return _salvar_figura(fig, "05_ranking_capitais_marco2026.png")


def executar_eda(df: pd.DataFrame) -> dict:
    """
    Executa todos os gráficos de EDA e retorna caminhos dos arquivos gerados.
    """
    caminhos = {
        "evolucao": grafico_evolucao_historica(df),
        "heatmap": grafico_heatmap_capitais(df),
        "decomposicao": grafico_decomposicao_media_nacional(df),
        "boxplot": grafico_boxplot_regional(df),
        "ranking": grafico_ranking_capitais(df),
    }
    print(f"\nEDA concluída: {len(caminhos)} gráficos gerados.")
    return caminhos
