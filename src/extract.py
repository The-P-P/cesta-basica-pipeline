"""
Módulo de extração de dados da cesta básica.
ÚNICO arquivo a modificar para alternar entre dados simulados e reais.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Seed fixo para reprodutibilidade
np.random.seed(42)

# Valores de referência: março/2026 por capital (base DIEESE)
CAPITAIS_REFERENCIA = [
    {"capital": "São Paulo", "estado": "SP", "custo_mar2026": 883.94, "regiao": "Sudeste"},
    {"capital": "Rio de Janeiro", "estado": "RJ", "custo_mar2026": 870.12, "regiao": "Sudeste"},
    {"capital": "Porto Alegre", "estado": "RS", "custo_mar2026": 865.30, "regiao": "Sul"},
    {"capital": "Florianópolis", "estado": "SC", "custo_mar2026": 858.00, "regiao": "Sul"},
    {"capital": "Curitiba", "estado": "PR", "custo_mar2026": 845.00, "regiao": "Sul"},
    {"capital": "Brasília", "estado": "DF", "custo_mar2026": 840.00, "regiao": "Centro-Oeste"},
    {"capital": "Manaus", "estado": "AM", "custo_mar2026": 820.00, "regiao": "Norte"},
    {"capital": "Belém", "estado": "PA", "custo_mar2026": 810.00, "regiao": "Norte"},
    {"capital": "Campo Grande", "estado": "MS", "custo_mar2026": 800.00, "regiao": "Centro-Oeste"},
    {"capital": "Goiânia", "estado": "GO", "custo_mar2026": 795.00, "regiao": "Centro-Oeste"},
    {"capital": "Belo Horizonte", "estado": "MG", "custo_mar2026": 790.00, "regiao": "Sudeste"},
    {"capital": "Vitória", "estado": "ES", "custo_mar2026": 785.00, "regiao": "Sudeste"},
    {"capital": "Cuiabá", "estado": "MT", "custo_mar2026": 782.00, "regiao": "Centro-Oeste"},
    {"capital": "Porto Velho", "estado": "RO", "custo_mar2026": 778.00, "regiao": "Norte"},
    {"capital": "Rio Branco", "estado": "AC", "custo_mar2026": 775.00, "regiao": "Norte"},
    {"capital": "Palmas", "estado": "TO", "custo_mar2026": 772.00, "regiao": "Norte"},
    {"capital": "Macapá", "estado": "AP", "custo_mar2026": 770.00, "regiao": "Norte"},
    {"capital": "Boa Vista", "estado": "RR", "custo_mar2026": 768.00, "regiao": "Norte"},
    {"capital": "Natal", "estado": "RN", "custo_mar2026": 765.00, "regiao": "Nordeste"},
    {"capital": "João Pessoa", "estado": "PB", "custo_mar2026": 762.00, "regiao": "Nordeste"},
    {"capital": "Maceió", "estado": "AL", "custo_mar2026": 758.00, "regiao": "Nordeste"},
    {"capital": "Recife", "estado": "PE", "custo_mar2026": 755.00, "regiao": "Nordeste"},
    {"capital": "Fortaleza", "estado": "CE", "custo_mar2026": 750.00, "regiao": "Nordeste"},
    {"capital": "Teresina", "estado": "PI", "custo_mar2026": 745.00, "regiao": "Nordeste"},
    {"capital": "Aracaju", "estado": "SE", "custo_mar2026": 742.00, "regiao": "Nordeste"},
    {"capital": "Salvador", "estado": "BA", "custo_mar2026": 780.55, "regiao": "Nordeste"},
    {"capital": "São Luís", "estado": "MA", "custo_mar2026": 738.00, "regiao": "Nordeste"},
]

# Deflação acumulada jan/2020 em relação a mar/2026 (~26% IPCA alimentação)
FATOR_DEFLACAO_2020 = 0.74
# Crescimento médio anual base
CRESCIMENTO_ANUAL_BASE = 0.055
# Ruído gaussiano
RUIDO_STD = 8.0


def _mapa_capitais() -> dict:
    """Retorna mapa de metadados por capital."""
    return {c["capital"]: {"estado": c["estado"], "regiao": c["regiao"]} for c in CAPITAIS_REFERENCIA}


def _gerar_serie_capital(
    capital: str,
    custo_mar2026: float,
    datas: pd.DatetimeIndex,
    crescimento_anual: float,
) -> np.ndarray:
    """Gera série mensal de custos para uma capital."""
    n_meses = len(datas)
    # Índice temporal: 0 = jan/2020, último = mar/2026
    meses_desde_inicio = np.arange(n_meses)

    # Valor alvo em jan/2020 (deflação de ~26% sobre mar/2026)
    if capital == "São Luís":
        custo_jan2020 = 490.0
    else:
        custo_jan2020 = custo_mar2026 * FATOR_DEFLACAO_2020

    # Ruído reduzido no primeiro mês para ancorar jan/2020
    ruido_inicial = np.random.normal(0, 2, 1)[0] if capital == "São Luís" else 0

    # Tendência: crescimento mensal composto
    taxa_mensal = (1 + crescimento_anual) ** (1 / 12) - 1
    tendencia = custo_jan2020 * (1 + taxa_mensal) ** meses_desde_inicio

    # Sazonalidade: pico jan-fev (+2%), vale abr-mai (-1.5%)
    sazonalidade = np.ones(n_meses)
    for i, data in enumerate(datas):
        mes = data.month
        if mes in (1, 2):
            sazonalidade[i] = 1.02
        elif mes in (4, 5):
            sazonalidade[i] = 0.985

    # Choque COVID: +8% entre ago/2020 e dez/2020
    choque_covid = np.ones(n_meses)
    for i, data in enumerate(datas):
        if data.year == 2020 and data.month >= 8:
            choque_covid[i] = 1.08

    # Ruído gaussiano
    ruido = np.random.normal(0, RUIDO_STD, n_meses)
    if capital == "São Luís":
        ruido[0] = ruido_inicial

    custos = tendencia * sazonalidade * choque_covid + ruido

    # Ancorar São Luís em ~R$ 490 em jan/2020
    if capital == "São Luís":
        custos[0] = 490.0 + ruido_inicial

    # Ajuste fino para aproximar o valor de mar/2026
    idx_mar2026 = np.where((datas.year == 2026) & (datas.month == 3))[0]
    if len(idx_mar2026) > 0:
        fator_ajuste = custo_mar2026 / custos[idx_mar2026[0]]
        # Aplica ajuste gradualmente nos últimos 12 meses
        for j in range(max(0, idx_mar2026[0] - 11), idx_mar2026[0] + 1):
            peso = (j - max(0, idx_mar2026[0] - 11)) / 11
            custos[j] = custos[j] * (1 + peso * (fator_ajuste - 1))

    return np.maximum(custos, 100.0)  # custo mínimo plausível


def get_data_simulado() -> pd.DataFrame:
    """
    Retorna dados simulados realistas da cesta básica (2020-2026).
    Baseado em valores históricos reais do DIEESE.
    ATIVO POR PADRÃO.
    """
    datas = pd.date_range(start="2020-01-01", end="2026-03-01", freq="MS")
    registros = []

    for info in CAPITAIS_REFERENCIA:
        # Variação ±1% no crescimento anual por capital
        variacao = np.random.uniform(-0.01, 0.01)
        crescimento = CRESCIMENTO_ANUAL_BASE + variacao

        custos = _gerar_serie_capital(
            capital=info["capital"],
            custo_mar2026=info["custo_mar2026"],
            datas=datas,
            crescimento_anual=crescimento,
        )

        for i, data in enumerate(datas):
            registros.append({
                "data": data,
                "capital": info["capital"],
                "estado": info["estado"],
                "regiao": info["regiao"],
                "custo": round(custos[i], 2),
                "fonte_dado": "simulado",
            })

    df = pd.DataFrame(registros)
    df["data"] = pd.to_datetime(df["data"])
    return df.sort_values(["capital", "data"]).reset_index(drop=True)


def get_data_real(caminho_csv: str = None) -> pd.DataFrame:
    """
    PARA USAR DADOS REAIS: descomente a chamada desta função em load_data().
    Baixe o CSV em: https://www.dieese.org.br...
    Formato esperado: colunas [data, capital, custo]
    """
    if caminho_csv is None:
        caminho_csv = Path(__file__).resolve().parent.parent / "data" / "raw" / "dieese_cesta_basica.csv"
    caminho = Path(caminho_csv)
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho_csv}. "
            "Baixe os dados em https://www.dieese.org.br/cestaBasica/index.html"
        )

    df = pd.read_csv(caminho, parse_dates=["data"])
    def _normalizar_custo(valor):
        texto = str(valor).strip()
        if "," in texto:
            # Formato brasileiro: 1.234,56 -> 1234.56
            texto = texto.replace(".", "").replace(",", ".")
        return texto

    df["custo"] = df["custo"].map(_normalizar_custo)
    df["custo"] = pd.to_numeric(df["custo"], errors="coerce")
    df = df.dropna(subset=["data", "capital", "custo"]).copy()

    # Mapeamento de capitais para estado e região
    mapa = _mapa_capitais()
    df["estado"] = df["capital"].map(lambda x: mapa.get(x, {}).get("estado", ""))
    df["regiao"] = df["capital"].map(lambda x: mapa.get(x, {}).get("regiao", ""))
    df["fonte_dado"] = "real_dieese"

    colunas = ["data", "capital", "estado", "regiao", "custo", "fonte_dado"]
    df = df[colunas].copy()
    df["data"] = pd.to_datetime(df["data"])
    df["custo"] = pd.to_numeric(df["custo"], errors="coerce")
    df = df.dropna(subset=["data", "capital", "custo"])
    return df.sort_values(["capital", "data"]).reset_index(drop=True)


def _reconstruir_historico_calibrado(df_real_capital: pd.DataFrame, capital: str) -> pd.DataFrame:
    """
    Reconstrói histórico de 2020 até mês anterior ao primeiro dado real.
    Série sintética é calibrada para encaixar suavemente no primeiro valor real.
    """
    primeira_data_real = df_real_capital["data"].min()
    if pd.isna(primeira_data_real):
        return pd.DataFrame(columns=df_real_capital.columns)

    inicio = pd.Timestamp("2020-01-01")
    fim = primeira_data_real - pd.offsets.MonthBegin(1)
    if fim < inicio:
        return pd.DataFrame(columns=df_real_capital.columns)

    datas_hist = pd.date_range(inicio, fim, freq="MS")
    valor_ancora = float(df_real_capital.loc[df_real_capital["data"] == primeira_data_real, "custo"].iloc[0])
    meses_ate_ancora = max(1, len(datas_hist))

    # Backcasting com inflação média anual e variação por capital
    variacao = np.random.uniform(-0.01, 0.01)
    crescimento_anual = CRESCIMENTO_ANUAL_BASE + variacao
    taxa_mensal = (1 + crescimento_anual) ** (1 / 12) - 1

    # Gera tendência para trás a partir da âncora real
    tendencia = np.array([
        valor_ancora / ((1 + taxa_mensal) ** (meses_ate_ancora - i))
        for i in range(meses_ate_ancora)
    ])

    # Sazonalidade leve
    fator_sazonal = np.ones(len(datas_hist))
    for i, data in enumerate(datas_hist):
        if data.month in (1, 2):
            fator_sazonal[i] = 1.02
        elif data.month in (4, 5):
            fator_sazonal[i] = 0.985

    # Choque COVID no fim de 2020
    choque = np.ones(len(datas_hist))
    for i, data in enumerate(datas_hist):
        if data.year == 2020 and data.month >= 8:
            choque[i] = 1.08

    ruido = np.random.normal(0, 5.0, len(datas_hist))
    custos = np.maximum(tendencia * fator_sazonal * choque + ruido, 100.0)

    # Ajuste de São Luís para partir próximo de 490 em jan/2020
    if capital == "São Luís" and len(custos) > 0:
        custos[0] = 490.0 + np.random.normal(0, 2)

    meta = _mapa_capitais()[capital]
    return pd.DataFrame({
        "data": datas_hist,
        "capital": capital,
        "estado": meta["estado"],
        "regiao": meta["regiao"],
        "custo": np.round(custos, 2),
        "fonte_dado": "simulado_calibrado",
    })


def get_data_hibrido(caminho_csv: str = None) -> pd.DataFrame:
    """
    Combina dados reais disponíveis com reconstrução histórica calibrada.
    - Reais: período disponível no arquivo DIEESE
    - Reconstruído: jan/2020 até mês anterior ao primeiro dado real por capital
    """
    df_real = get_data_real(caminho_csv=caminho_csv)
    if df_real.empty:
        raise ValueError("Dados reais vazios para composição híbrida.")

    registros = []
    for capital in sorted(df_real["capital"].unique()):
        df_cap = df_real[df_real["capital"] == capital].sort_values("data").reset_index(drop=True)
        df_hist = _reconstruir_historico_calibrado(df_cap, capital=capital)
        combinado = pd.concat([df_hist, df_cap], ignore_index=True)
        combinado = combinado.sort_values("data").drop_duplicates(subset=["data"], keep="last")
        registros.append(combinado)

    df_hibrido = pd.concat(registros, ignore_index=True)
    df_hibrido["data"] = pd.to_datetime(df_hibrido["data"])
    df_hibrido["custo"] = pd.to_numeric(df_hibrido["custo"], errors="coerce")
    df_hibrido = df_hibrido.dropna(subset=["data", "capital", "custo"]).copy()
    return df_hibrido.sort_values(["capital", "data"]).reset_index(drop=True)


def load_data() -> pd.DataFrame:
    """Ponto de entrada único. Troque aqui para alternar entre simulado, real e híbrido."""
    return get_data_hibrido()
    # return get_data_simulado()
    # return get_data_real()
