"""
Módulo de transformação e engenharia de features dos dados da cesta básica.
"""

import pandas as pd
import numpy as np
from scipy import stats


def tratar_valores_ausentes(df: pd.DataFrame) -> pd.DataFrame:
    """Interpola valores ausentes de custo por capital (interpolação linear)."""
    df = df.copy()
    df = df.sort_values(["capital", "data"])

    df["custo"] = df.groupby("capital")["custo"].transform(
        lambda s: s.interpolate(method="linear", limit_direction="both")
    )
    return df


def calcular_variacoes(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula variação mensal (%) e anual (%) do custo por capital."""
    df = df.copy()
    df = df.sort_values(["capital", "data"])

    df["variacao_mensal_pct"] = df.groupby("capital")["custo"].pct_change() * 100
    df["variacao_anual_pct"] = df.groupby("capital")["custo"].pct_change(periods=12) * 100

    return df


def calcular_media_nacional(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula a média nacional de custo por mês."""
    media = (
        df.groupby("data")["custo"]
        .mean()
        .reset_index()
        .rename(columns={"custo": "media_nacional"})
    )
    return media


def identificar_outliers(df: pd.DataFrame, z_threshold: float = 3.0) -> pd.DataFrame:
    """Identifica outliers via z-score e adiciona flag booleana."""
    df = df.copy()

    def _zscore_flag(serie: pd.Series) -> pd.Series:
        if serie.std() == 0 or serie.isna().all():
            return pd.Series(False, index=serie.index)
        z = np.abs(stats.zscore(serie, nan_policy="omit"))
        return pd.Series(z > z_threshold, index=serie.index)

    df["outlier"] = df.groupby("capital")["custo"].transform(_zscore_flag)
    return df


def criar_features_modelagem(df: pd.DataFrame) -> pd.DataFrame:
    """Cria features de lag e médias móveis para modelagem preditiva."""
    df = df.copy()
    df = df.sort_values(["capital", "data"])

    df["lag_1"] = df.groupby("capital")["custo"].shift(1)
    df["lag_12"] = df.groupby("capital")["custo"].shift(12)
    df["rolling_mean_3"] = df.groupby("capital")["custo"].transform(
        lambda s: s.rolling(window=3, min_periods=1).mean()
    )
    df["rolling_mean_6"] = df.groupby("capital")["custo"].transform(
        lambda s: s.rolling(window=6, min_periods=1).mean()
    )

    return df


def transformar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline completo de transformação.
    Retorna DataFrame enriquecido com variações, outliers e features.
    """
    df = tratar_valores_ausentes(df)
    df = calcular_variacoes(df)
    df = identificar_outliers(df)
    df = criar_features_modelagem(df)
    return df


def obter_serie_agregada(df: pd.DataFrame, capital: str = None) -> pd.DataFrame:
    """
    Retorna série temporal agregada para uma capital ou média nacional.
    capital=None retorna a média nacional mensal.
    """
    if capital is None:
        media = calcular_media_nacional(df)
        media = media.rename(columns={"media_nacional": "custo"})
        media["capital"] = "Média Nacional"
        media["estado"] = "BR"
        media["regiao"] = "Nacional"
        return media.sort_values("data").reset_index(drop=True)

    return (
        df[df["capital"] == capital]
        .sort_values("data")
        .reset_index(drop=True)
    )
