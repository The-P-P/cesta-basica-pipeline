"""
Módulo de modelagem preditiva: SARIMA, Prophet e projeções de cenários.
"""

import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX

from transform import calcular_media_nacional, obter_serie_agregada

warnings.filterwarnings("ignore")

plt.style.use("seaborn-v0_8-whitegrid")

# Paleta e configuração
COR_SAO_LUIS = "#1a5c38"
COR_HISTORICO = "#1a3a5c"
COR_OTIMISTA = "#27ae60"
COR_MODERADO = "#e67e22"
COR_CONSERVADOR = "#c0392b"
FONTE_DADOS = "Fonte: Dados simulados baseados em DIEESE"

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs" / "graficos"
METRICAS_PATH = BASE_DIR / "outputs" / "metricas_modelos.csv"
PROJECOES_PATH = BASE_DIR / "outputs" / "projecoes_2026_2030.csv"
DPI = 150

# Períodos de treino e teste
DATA_TREINO_FIM = "2024-12-01"
DATA_TESTE_INICIO = "2025-01-01"
DATA_HISTORICO_FIM = "2026-03-01"
DATA_PROJECAO_INICIO = "2026-04-01"
DATA_PROJECAO_FIM = "2030-12-01"

# Cenários de inflação anual para alimentos
CENARIOS = {
    "Otimista": 0.03,
    "Moderado": 0.045,
    "Conservador": 0.06,
}


def _calcular_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calcula MAPE evitando divisão por zero."""
    mask = y_true != 0
    if not mask.any():
        return np.nan
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def _calcular_metricas(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calcula MAE, RMSE e MAPE."""
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "MAPE": _calcular_mape(y_true, y_pred),
    }


def _preparar_serie(serie_df: pd.DataFrame) -> pd.Series:
    """Converte DataFrame em série temporal indexada por data."""
    return serie_df.set_index("data")["custo"].sort_index().asfreq("MS")


def _previsao_sarima_valida(serie: pd.Series, pred: np.ndarray) -> bool:
    """Verifica se previsões SARIMA estão em faixa plausível."""
    if pred is None or len(pred) == 0:
        return False
    pred = np.asarray(pred, dtype=float)
    if not np.all(np.isfinite(pred)):
        return False
    lim_inf = serie.min() * 0.5
    lim_sup = serie.max() * 1.5
    return bool(np.all((pred >= lim_inf) & (pred <= lim_sup)))


def _buscar_melhor_sarima(serie: pd.Series, passos_validacao: int = 15) -> Tuple[SARIMAX, Tuple]:
    """
    Busca automática de parâmetros SARIMA via grid search com critério AIC.
    Rejeita modelos com previsões instáveis (explosivas).
    """
    melhor_aic = np.inf
    melhor_modelo = None
    melhor_ordem = None

    # Grid reduzido para performance
    p_values = range(0, 3)
    d_values = [0, 1]
    q_values = range(0, 3)
    P_values = range(0, 2)
    D_values = [0, 1]
    Q_values = range(0, 2)

    for p in p_values:
        for d in d_values:
            for q in q_values:
                for P in P_values:
                    for D in D_values:
                        for Q in Q_values:
                            try:
                                modelo = SARIMAX(
                                    serie,
                                    order=(p, d, q),
                                    seasonal_order=(P, D, Q, 12),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False,
                                )
                                resultado = modelo.fit(disp=False, maxiter=150)
                                pred_teste = resultado.forecast(steps=passos_validacao)
                                if not _previsao_sarima_valida(serie, pred_teste.values):
                                    continue
                                if resultado.aic < melhor_aic:
                                    melhor_aic = resultado.aic
                                    melhor_modelo = resultado
                                    melhor_ordem = (p, d, q, P, D, Q)
                            except Exception:
                                continue

    if melhor_modelo is None:
        # Fallback estável para séries suaves (ex.: média nacional)
        modelo = SARIMAX(serie, order=(1, 1, 1), seasonal_order=(1, 0, 1, 12))
        melhor_modelo = modelo.fit(disp=False)
        melhor_ordem = (1, 1, 1, 1, 0, 1)

    print(f"  SARIMA{best_ordem_display(melhor_ordem)} — AIC: {melhor_modelo.aic:.2f}")
    return melhor_modelo, melhor_ordem


def best_ordem_display(ordem) -> str:
    """Formata ordem SARIMA para exibição."""
    p, d, q, P, D, Q = ordem
    return f"({p},{d},{q})({P},{D},{Q},12)"


def treinar_sarima(
    serie: pd.Series,
    data_treino_fim: str = DATA_TREINO_FIM,
) -> Tuple[object, pd.Series, pd.Series]:
    """
    Treina SARIMA e retorna modelo, série de treino e série de teste.
    """
    treino = serie[serie.index <= data_treino_fim]
    teste = serie[serie.index > data_treino_fim]

    modelo, _ = _buscar_melhor_sarima(treino)
    return modelo, treino, teste


def prever_sarima(modelo, n_periodos: int) -> pd.Series:
    """Gera previsões com modelo SARIMA treinado."""
    forecast = modelo.forecast(steps=n_periodos)
    return forecast


def treinar_prophet(
    serie: pd.Series,
    data_treino_fim: str = DATA_TREINO_FIM,
) -> Tuple[Prophet, pd.DataFrame, pd.DataFrame]:
    """
    Treina Prophet com sazonalidade anual/mensal e feriados brasileiros.
    """
    df_prophet = pd.DataFrame({
        "ds": serie.index,
        "y": serie.values,
    })

    treino = df_prophet[df_prophet["ds"] <= data_treino_fim]
    teste = df_prophet[df_prophet["ds"] > data_treino_fim]

    modelo = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
    )
    # Sazonalidade mensal customizada
    modelo.add_seasonality(name="monthly", period=30.5, fourier_order=5)

    # Feriados brasileiros (2019-2031 para cobrir projeções)
    feriados = pd.DataFrame({
        "holiday": "feriado_br",
        "ds": pd.to_datetime([
            f"{ano}-{mes:02d}-{dia:02d}"
            for ano in range(2019, 2032)
            for mes, dia in [
                (1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (12, 25),
                (2, 17), (2, 18), (3, 29), (4, 18), (6, 19), (8, 15),
            ]
        ]),
        "lower_window": 0,
        "upper_window": 0,
    })
    modelo.holidays = feriados

    modelo.fit(treino)
    return modelo, treino, teste


def prever_prophet(
    modelo: Prophet,
    datas: pd.DatetimeIndex,
) -> pd.DataFrame:
    """Gera previsões Prophet para datas especificadas."""
    future = pd.DataFrame({"ds": datas})
    return modelo.predict(future)


def avaliar_modelos(
    df: pd.DataFrame,
    series_alvo: List[str] = None,
) -> pd.DataFrame:
    """
    Avalia SARIMA e Prophet para séries alvo (São Luís e Média Nacional).
    Retorna DataFrame com métricas.
    """
    if series_alvo is None:
        series_alvo = ["São Luís", "Média Nacional"]

    resultados = []

    for nome in series_alvo:
        print(f"\nAvaliando modelos para: {nome}")
        capital = None if nome == "Média Nacional" else nome
        serie_df = obter_serie_agregada(df, capital=capital)
        serie = _preparar_serie(serie_df)

        # --- SARIMA ---
        modelo_sarima, treino, teste = treinar_sarima(serie)
        if len(teste) > 0:
            pred_sarima = modelo_sarima.forecast(steps=len(teste))
            metricas_sarima = _calcular_metricas(teste.values, pred_sarima.values)
            for metrica, valor in metricas_sarima.items():
                resultados.append({
                    "serie": nome,
                    "modelo": "SARIMA",
                    "metrica": metrica,
                    "valor": round(valor, 4),
                })

        # --- Prophet ---
        modelo_prophet, treino_p, teste_p = treinar_prophet(serie)
        if len(teste_p) > 0:
            future_teste = modelo_prophet.make_future_dataframe(periods=len(teste_p), freq="MS")
            pred_prophet = modelo_prophet.predict(future_teste)
            pred_teste = pred_prophet.tail(len(teste_p))["yhat"].values
            metricas_prophet = _calcular_metricas(teste_p["y"].values, pred_teste)
            for metrica, valor in metricas_prophet.items():
                resultados.append({
                    "serie": nome,
                    "modelo": "Prophet",
                    "metrica": metrica,
                    "valor": round(valor, 4),
                })

    df_metricas = pd.DataFrame(resultados)
    METRICAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_metricas.to_csv(METRICAS_PATH, index=False, encoding="utf-8-sig")
    print(f"\nMétricas salvas em: {METRICAS_PATH}")

    # Imprimir métricas
    print("\n" + "=" * 60)
    print("MÉTRICAS DE AVALIAÇÃO")
    print("=" * 60)
    for _, row in df_metricas.iterrows():
        print(f"  {row['serie']} | {row['modelo']} | {row['metrica']}: {row['valor']:.4f}")

    return df_metricas


def gerar_projecoes_cenarios(
    df: pd.DataFrame,
    capital: str = "São Luís",
) -> Tuple[pd.DataFrame, Prophet, pd.Series]:
    """
    Gera projeções em 3 cenários (abr/2026 a dez/2030) usando Prophet como base.
    """
    serie_df = obter_serie_agregada(df, capital=None if capital == "Média Nacional" else capital)
    serie = _preparar_serie(serie_df)

    # Treinar Prophet com todos os dados históricos
    df_prophet = pd.DataFrame({"ds": serie.index, "y": serie.values})
    modelo = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
    )
    modelo.add_seasonality(name="monthly", period=30.5, fourier_order=5)
    modelo.fit(df_prophet)

    # Datas de projeção
    datas_projecao = pd.date_range(start=DATA_PROJECAO_INICIO, end=DATA_PROJECAO_FIM, freq="MS")
    pred_base = prever_prophet(modelo, datas_projecao)

    # Valor base em mar/2026 (último histórico)
    valor_base = float(serie.iloc[-1])

    # Sazonalidade histórica por mês (padrão observado na série)
    serie_df_idx = serie_df.copy()
    serie_df_idx["mes"] = serie_df_idx["data"].dt.month
    sazonal_mensal = serie_df_idx.groupby("mes")["custo"].mean()
    sazonal_mensal = sazonal_mensal / sazonal_mensal.mean()

    # Tendência suavizada do Prophet (evita oscilações em horizontes longos)
    trend_prophet = pred_base["trend"].values
    inflacao_moderada = CENARIOS["Moderado"]
    registros = []
    projecoes_cenarios = {}

    for nome_cenario, inflacao_anual in CENARIOS.items():
        valores = []

        for i, data in enumerate(datas_projecao):
            meses = i + 1

            # Projeção base: tendência do Prophet ancorada no último valor histórico
            trend_i = valor_base * (trend_prophet[i] / trend_prophet[0])

            # Multiplicador de cenário sobre projeção moderada (regra do TCC)
            fator_cenario = (1 + inflacao_anual) ** (meses / 12)
            fator_moderado = (1 + inflacao_moderada) ** (meses / 12)
            valor_ajustado = trend_i * (fator_cenario / fator_moderado)

            # Sazonalidade mensal histórica (amplitude limitada)
            fator_sazonal = float(sazonal_mensal.get(data.month, 1.0))
            fator_sazonal = np.clip(fator_sazonal, 0.97, 1.03)
            valor_final = valor_ajustado * fator_sazonal
            valores.append(valor_final)

            registros.append({
                "data": data,
                "capital": capital,
                "cenario": nome_cenario,
                "custo_projetado": round(valor_final, 2),
                "modelo": "Prophet",
            })

        projecoes_cenarios[nome_cenario] = pd.Series(valores, index=datas_projecao)

    df_projecoes = pd.DataFrame(registros)
    return df_projecoes, modelo, serie


def grafico_projecao(
    serie_historica: pd.Series,
    projecoes: Dict[str, pd.Series],
    capital: str,
    nome_arquivo: str,
) -> Path:
    """
    Gráfico principal de projeção histórica + 3 cenários até 2030.
    """
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Histórico
    ax.plot(
        serie_historica.index,
        serie_historica.values,
        color=COR_HISTORICO,
        linewidth=2.5,
        label="Histórico",
        zorder=5,
    )

    # Cenários
    cores_cenarios = {
        "Otimista": COR_OTIMISTA,
        "Moderado": COR_MODERADO,
        "Conservador": COR_CONSERVADOR,
    }
    estilos = {
        "Otimista": (COR_OTIMISTA, "--"),
        "Moderado": (COR_MODERADO, "--"),
        "Conservador": (COR_CONSERVADOR, "--"),
    }

    for nome, serie_proj in projecoes.items():
        cor, estilo = estilos[nome]
        ax.plot(
            serie_proj.index,
            serie_proj.values,
            color=cor,
            linestyle=estilo,
            linewidth=2,
            label=f"Cenário {nome}",
        )

    # Área sombreada entre otimista e conservador
    if "Otimista" in projecoes and "Conservador" in projecoes:
        ax.fill_between(
            projecoes["Otimista"].index,
            projecoes["Otimista"].values,
            projecoes["Conservador"].values,
            alpha=0.15,
            color="gray",
            label="Faixa de incerteza",
        )

    # Linha vertical em mar/2026
    data_corte = pd.Timestamp("2026-03-01")
    ax.axvline(x=data_corte, color="gray", linestyle=":", linewidth=1.5, alpha=0.8)
    ax.text(
        data_corte,
        ax.get_ylim()[1] * 0.95,
        " Início das Projeções",
        fontsize=10,
        color="gray",
        va="top",
    )

    # Anotações dos valores finais em dez/2030
    for nome, serie_proj in projecoes.items():
        valor_final = serie_proj.iloc[-1]
        data_final = serie_proj.index[-1]
        cor, _ = estilos[nome]
        ax.annotate(
            f"R$ {valor_final:,.0f}".replace(",", "."),
            xy=(data_final, valor_final),
            xytext=(10, 0),
            textcoords="offset points",
            fontsize=9,
            color=cor,
            fontweight="bold",
        )

    titulo = f"Projeção do Custo da Cesta Básica — {capital} (2020–2030)"
    ax.set_title(titulo, fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Data", fontsize=12)
    ax.set_ylabel("Custo (R$)", fontsize=12)
    ax.legend(loc="upper left", fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator())

    fig.text(
        0.12, 0.02,
        "Modelos ARIMA/SARIMA e Prophet | " + FONTE_DADOS,
        fontsize=9,
        color="gray",
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    caminho = OUTPUT_DIR / nome_arquivo
    fig.savefig(caminho, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Gráfico salvo: {caminho}")
    return caminho


def executar_modelagem(df: pd.DataFrame) -> Dict:
    """
    Pipeline completo de modelagem: avaliação, projeções e gráficos.
    """
    # Avaliar modelos
    df_metricas = avaliar_modelos(df)

    # Projeções e gráficos
    todas_projecoes = []

    for capital in ["São Luís", "Média Nacional"]:
        print(f"\nGerando projeções para: {capital}")
        df_proj, _, serie = gerar_projecoes_cenarios(df, capital=capital)
        todas_projecoes.append(df_proj)

        # Montar dicionário de cenários para gráfico
        projecoes_dict = {}
        for cenario in CENARIOS:
            projecoes_dict[cenario] = pd.Series(
                df_proj[df_proj["cenario"] == cenario]["custo_projetado"].values,
                index=pd.to_datetime(df_proj[df_proj["cenario"] == cenario]["data"]),
            )

        nome_arquivo = (
            "projecao_sao_luis_2020_2030.png"
            if capital == "São Luís"
            else "projecao_media_nacional_2020_2030.png"
        )
        grafico_projecao(serie, projecoes_dict, capital, nome_arquivo)

    # Salvar todas as projeções
    df_todas = pd.concat(todas_projecoes, ignore_index=True)
    PROJECOES_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_todas.to_csv(PROJECOES_PATH, index=False, encoding="utf-8-sig")
    print(f"\nProjeções salvas em: {PROJECOES_PATH}")

    return {
        "metricas": df_metricas,
        "projecoes": df_todas,
    }
