# =============================================================================
# APÊNDICE A — Trechos principais do Pipeline ETL
# Repositório completo: https://github.com/The-P-P/cesta-basica-pipeline
# =============================================================================

# --- extract.py: ponto de entrada dos dados ---
def load_data() -> pd.DataFrame:
    """Ponto de entrada único. Troque aqui para alternar entre simulado, real e híbrido."""
    return get_data_hibrido()
    # return get_data_simulado()
    # return get_data_real()


def get_data_real(caminho_csv: str = None) -> pd.DataFrame:
    """Carrega CSV do DIEESE (data, capital, custo) e enriquece com metadados."""
    # ... leitura de data/raw/dieese_cesta_basica.csv ...
    pass


def get_data_hibrido(caminho_csv: str = None) -> pd.DataFrame:
    """
    Combina dados reais disponíveis com reconstrução histórica calibrada.
    - Reais: período disponível no arquivo DIEESE
    - Reconstruído: jan/2020 até mês anterior ao primeiro dado real por capital
    """
    # ... concatena _reconstruir_historico_calibrado() + get_data_real() ...
    pass


# --- transform.py: limpeza e features ---
def transformar(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline completo de transformação."""
    df = tratar_valores_ausentes(df)      # interpolação linear por capital
    df = calcular_variacoes(df)           # variação mensal e anual (%)
    df = identificar_outliers(df)         # z-score > 3
    df = criar_features_modelagem(df)     # lag_1, lag_12, médias móveis
    return df


# --- load.py: persistência ---
def executar_pipeline() -> pd.DataFrame:
    """Executa ETL completo: extração, transformação e persistência."""
    df_raw = load_data()
    df_raw.to_csv(raw_path, index=False, encoding="utf-8-sig")
    df_processed = transformar(df_raw)
    salvar_csv(df_processed)              # data/processed/cesta_basica_processada.csv
    salvar_sqlite(df_processed)           # data/processed/cesta_basica.db
    return df_processed
