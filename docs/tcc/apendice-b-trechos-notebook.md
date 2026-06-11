# APÊNDICE B — Trechos do notebook `analise_completa.ipynb`

*Cole no TCC com formatação monoespaçada. Notebook completo: `notebooks/analise_completa.ipynb`*

---

## B.1 Configuração e importação dos módulos

```python
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from extract import load_data
from transform import transformar, calcular_media_nacional, obter_serie_agregada
from load import executar_pipeline
from eda import executar_eda
from model import executar_modelagem

OUTPUT_GRAFICOS = PROJECT_ROOT / "outputs" / "graficos"
OUTPUT_GRAFICOS.mkdir(parents=True, exist_ok=True)
```

---

## B.2 Execução do pipeline ETL

```python
df = executar_pipeline()
print(f"Shape dos dados: {df.shape}")
print(f"Período: {df['data'].min().strftime('%b/%Y')} a {df['data'].max().strftime('%b/%Y')}")
print(f"Capitais: {df['capital'].nunique()}")
df.head()
```

**Saída típica:** 1.970 registros × 13 colunas; 27 capitais; jan/2020 a mar/2026.

---

## B.3 Análise exploratória (EDA)

```python
executar_eda(df)
```

Gera automaticamente em `outputs/graficos/`:

- `01_evolucao_historica_nacional.png`
- `02_heatmap_capitais.png`
- `03_decomposicao_media_nacional.png`
- `04_boxplot_regional.png`
- `05_ranking_capitais_marco2026.png`

---

## B.4 Modelagem preditiva e validação

```python
resultados = executar_modelagem(df)
```

### Divisão treino/teste (definida em `src/model.py`)

| Conjunto | Período |
|----------|---------|
| Treino | jan/2020 – dez/2024 |
| Teste | jan/2025 – mar/2026 |

### Modelos avaliados

- **SARIMA:** busca automática de ordem `(p,d,q)(P,D,Q,12)` por critério AIC
- **Prophet:** sazonalidade anual e mensal; feriados brasileiros

### Métricas de validação

| Série | Modelo | MAE (R$) | RMSE (R$) | MAPE (%) |
|-------|--------|----------|-----------|----------|
| Média Nacional | SARIMA | 15,52 | 19,74 | 2,22 |
| Média Nacional | Prophet | 15,78 | 21,10 | 2,26 |

### Cenários de projeção (abr/2026 – dez/2030)

| Cenário | Inflação anual (alimentos) |
|---------|----------------------------|
| Otimista | 3,0% |
| Moderado | 4,5% |
| Conservador | 6,0% |

---

## B.5 Gráficos de projeção (inserir como figuras no apêndice)

- `projecao_media_nacional_2020_2030.png` — figura principal do trabalho (agregado nacional)

Arquivos de dados gerados:

- `outputs/metricas_modelos.csv`
- `outputs/projecoes_2026_2030.csv`
