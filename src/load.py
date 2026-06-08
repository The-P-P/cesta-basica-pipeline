"""
Módulo de persistência dos dados (SQLite + CSV).
"""

import sqlite3
from pathlib import Path

import pandas as pd

from extract import load_data
from transform import transformar, calcular_media_nacional


# Caminhos padrão relativos à raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DB_PATH = DATA_PROCESSED / "cesta_basica.db"
CSV_PATH = DATA_PROCESSED / "cesta_basica_processada.csv"
MEDIA_NACIONAL_CSV = DATA_PROCESSED / "media_nacional.csv"


def salvar_csv(df: pd.DataFrame, caminho: Path = CSV_PATH) -> Path:
    """Salva DataFrame em CSV."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8-sig")
    return caminho


def salvar_sqlite(df: pd.DataFrame, caminho: Path = DB_PATH, tabela: str = "cesta_basica") -> Path:
    """Persiste DataFrame em banco SQLite."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(caminho) as conn:
        df.to_sql(tabela, conn, if_exists="replace", index=False)
    return caminho


def carregar_csv(caminho: Path = CSV_PATH) -> pd.DataFrame:
    """Carrega dados processados do CSV."""
    df = pd.read_csv(caminho, parse_dates=["data"])
    return df


def carregar_sqlite(caminho: Path = DB_PATH, tabela: str = "cesta_basica") -> pd.DataFrame:
    """Carrega dados processados do SQLite."""
    with sqlite3.connect(caminho) as conn:
        df = pd.read_sql(f"SELECT * FROM {tabela}", conn, parse_dates=["data"])
    return df


def executar_pipeline() -> pd.DataFrame:
    """
    Executa ETL completo: extração, transformação e persistência.
    Retorna DataFrame processado.
    """
    # Extração
    df_raw = load_data()

    # Salvar dados brutos
    if "fonte_dado" in df_raw.columns:
        if (df_raw["fonte_dado"] == "real_dieese").all():
            nome_raw = "cesta_basica_real.csv"
        elif (df_raw["fonte_dado"] == "simulado").all():
            nome_raw = "cesta_basica_simulada.csv"
        else:
            nome_raw = "cesta_basica_hibrida.csv"
    else:
        nome_raw = "cesta_basica_simulada.csv"

    raw_path = BASE_DIR / "data" / "raw" / nome_raw
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    df_raw.to_csv(raw_path, index=False, encoding="utf-8-sig")

    # Transformação
    df_processed = transformar(df_raw)

    # Média nacional
    media_nacional = calcular_media_nacional(df_processed)
    salvar_csv(media_nacional, MEDIA_NACIONAL_CSV)

    # Persistência
    salvar_csv(df_processed)
    salvar_sqlite(df_processed)

    print(f"Dados salvos em: {CSV_PATH}")
    print(f"Banco SQLite: {DB_PATH}")
    print(f"Registros processados: {len(df_processed)}")

    return df_processed
