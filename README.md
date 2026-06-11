# Pipeline de Análise e Projeção de Preços da Cesta Básica

**TCC — Engenharia de Software**  
*Desenvolvimento de Pipeline para Análise e Projeção de Preços da Cesta Básica no Brasil (2020–2030) Utilizando Séries Temporais*

Pipeline modular e reprodutível para análise exploratória, modelagem preditiva (SARIMA e Prophet) e projeção de cenários do custo da cesta básica nas **27 capitais brasileiras**, com agregação e destaque para a **média nacional**.

---

## Instalação

```bash
# Clone ou acesse o diretório do projeto
cd cesta-basica-pipeline

# Crie um ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

---

## Como Executar

```bash
# Abrir o notebook principal
jupyter notebook notebooks/analise_completa.ipynb

# Abrir o dashboard interativo (Nível 1)
streamlit run dashboard/app.py
# Windows: .\run_dashboard.ps1
```

Execute todas as células do notebook. Os gráficos serão salvos automaticamente em `outputs/graficos/` e as métricas/projeções em `outputs/`.

### Execução via linha de comando (opcional)

```bash
cd src
python -c "from load import executar_pipeline; from eda import executar_eda; from model import executar_modelagem; df = executar_pipeline(); executar_eda(df); executar_modelagem(df)"
```

---

## Como Usar Dados Reais

> **Esta é a principal vantagem da arquitetura do pipeline:** apenas um arquivo precisa ser alterado.

### Passo a passo

1. **Baixe os dados do DIEESE** em [dieese.org.br/cestaBasica](https://www.dieese.org.br/cestaBasica/index.html)
2. **Salve o CSV** em `data/raw/dieese_cesta_basica.csv`
3. **Formato esperado** do CSV:

   | data       | capital    | custo   |
   |------------|------------|---------|
   | 2020-01-01 | Aracaju    | 368.69  |
   | 2020-01-01 | São Paulo  | 654.12  |
   | ...        | ...        | ...     |

4. **Edite `src/extract.py`** — na função `load_data()`, troque:

   ```python
   def load_data() -> pd.DataFrame:
       # return get_data_simulado()
       return get_data_real()  # <- descomente esta linha
   ```

5. **Execute o notebook** normalmente. Todo o pipeline usará os dados reais.

---

## Estrutura de Pastas

```
cesta-basica-pipeline/
├── data/
│   ├── raw/                  # Dados brutos (CSV simulado ou DIEESE)
│   └── processed/            # Dados transformados (CSV + SQLite)
├── src/
│   ├── extract.py            # ⭐ ÚNICO arquivo para trocar dados
│   ├── transform.py          # Limpeza, features e outliers
│   ├── load.py               # Persistência SQLite + CSV
│   ├── eda.py                # Gráficos exploratórios
│   └── model.py              # SARIMA, Prophet e projeções
├── notebooks/
│   └── analise_completa.ipynb
├── dashboard/
│   └── app.py                  # Dashboard Streamlit (deploy + QR code)
├── outputs/
│   ├── graficos/             # PNGs para slides (150 dpi)
│   ├── metricas_modelos.csv
│   └── projecoes_2026_2030.csv
├── requirements.txt
└── README.md
```

---

## Gráficos Gerados

Ao executar o pipeline completo, os seguintes arquivos são criados em `outputs/graficos/`:

| Arquivo | Descrição |
|---------|-----------|
| `01_evolucao_historica_nacional.png` | Evolução 2020–2026 com destaque na média nacional e São Paulo |
| `02_heatmap_capitais.png` | Heatmap custo médio por capital e ano |
| `03_decomposicao_media_nacional.png` | Decomposição temporal da média nacional (tendência, sazonalidade, resíduo) |
| `04_boxplot_regional.png` | Distribuição de preços por região |
| `05_ranking_capitais_marco2026.png` | Ranking horizontal — março/2026 |
| `projecao_media_nacional_2020_2030.png` | **Gráfico principal** — projeções da média nacional em 3 cenários |
| `projecoes_2026_2030.csv` | Projeções das **27 capitais** + média nacional (3 cenários) |

### Exemplo — Gráfico Principal

O gráfico de projeção da média nacional mostra:
- Linha histórica sólida (2020–mar/2026)
- Três cenários pontilhados até dez/2030 (Otimista 3%, Moderado 4,5%, Conservador 6%)
- Faixa sombreada de incerteza
- Anotações dos valores finais

---

## Modelos Utilizados

### SARIMA
- Busca automática de parâmetros `(p,d,q)(P,D,Q,12)` via critério AIC
- Treino: jan/2020 – dez/2024 | Teste: jan/2025 – mar/2026

### Prophet (Facebook)
- Sazonalidade anual e mensal
- Feriados brasileiros incluídos
- Mesmo período de treino/teste

### Cenários de Projeção (abr/2026 – dez/2030)

| Cenário | Inflação Anual (alimentos) |
|---------|---------------------------|
| Otimista | 3,0% |
| Moderado | 4,5% |
| Conservador | 6,0% |

---

## Paleta de Cores

| Elemento | Cor | Hex |
|----------|-----|-----|
| Média Nacional | Azul | `#2980b9` |
| São Paulo | Vermelho | `#c0392b` |
| Destaque / primária | Verde escuro | `#1a5c38` |
| Cenário Otimista | Verde | `#27ae60` |
| Cenário Moderado | Laranja | `#e67e22` |
| Cenário Conservador | Vermelho | `#c0392b` |

---

## Tecnologias

- **Python 3.11+**
- pandas, numpy, matplotlib, seaborn
- statsmodels (SARIMA)
- Prophet (Facebook)
- scikit-learn (métricas)
- SQLite (persistência)

---

## Licença

Projeto acadêmico — TCC Engenharia de Software.
