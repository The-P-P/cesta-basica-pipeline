,# Guia — Apêndices e Anexos do TCC

Use este guia para montar a parte final do trabalho (após as referências bibliográficas).
Conforme a ABNT NBR 14724, **apêndices** são material **produzido pelo autor**; **anexos** são material **de terceiros**.

Repositório do projeto: **https://github.com/The-P-P/cesta-basica-pipeline**

---

## Ordem sugerida no documento

```
REFERÊNCIAS
APÊNDICE A — Código-fonte do Pipeline ETL
APÊNDICE B — Notebook de Análise Exploratória e Modelagem Preditiva
ANEXO A — Tabela de preços da Pesquisa Nacional da Cesta Básica (DIEESE)
ANEXO B — Metodologia oficial da Cesta Básica (DIEESE) e do IPCA (IBGE)
```

---

## Texto introdutório (cole antes dos apêndices/anexos)

> Os apêndices e anexos que seguem complementam o desenvolvimento apresentado nos capítulos anteriores. Os **Apêndices A e B** reúnem, respectivamente, o código-fonte do pipeline ETL desenvolvido para este trabalho e os trechos do notebook de análise exploratória e modelagem preditiva. Os **Anexos A e B** apresentam a base de dados primária obtida junto ao DIEESE e um resumo da metodologia oficial de cálculo da cesta básica e do IPCA, fontes utilizadas como referência metodológica do estudo. O código completo, dados processados e artefatos de saída encontram-se no repositório público indicado nas referências.

---

# APÊNDICE A — Código-fonte do Pipeline ETL

## Texto para o corpo do TCC (1 parágrafo)

> O Apêndice A apresenta o código-fonte do pipeline ETL desenvolvido em Python para extração, transformação e carga dos dados da Pesquisa Nacional da Cesta Básica. A arquitetura modular separa responsabilidades em quatro módulos: `extract.py` (extração e composição híbrida de dados reais do DIEESE com reconstrução histórica calibrada), `transform.py` (limpeza, engenharia de features e detecção de outliers com Pandas), `load.py` (persistência em CSV e SQLite) e `preparar_dieese.py` (pré-processamento do arquivo bruto do DIEESE). O ponto de entrada único é a função `load_data()` em `extract.py`, que permite alternar entre dados simulados, reais ou híbridos sem alterar os demais módulos. O código integral está disponível em: https://github.com/The-P-P/cesta-basica-pipeline (pasta `src/`).

## O que incluir no PDF

| Prioridade | Conteúdo | Arquivo no projeto |
|------------|----------|-------------------|
| Obrigatório | Função `load_data()` e fluxo ETL | `src/extract.py` (final), `src/load.py` |
| Obrigatório | Pipeline de transformação | `src/transform.py` |
| Recomendado | Persistência SQLite/CSV | `src/load.py` |
| Opcional (resumir) | Geração simulada/calibrada | `src/extract.py` (início) |
| Referência apenas | Código completo | Link GitHub |

**Dica:** No Word, use fonte monoespaçada (Consolas 9 pt), numeração de linhas opcional. Se o código for longo, inclua apenas os trechos do arquivo `docs/tcc/apendice-a-trechos.py` e cite o repositório para o restante.

## Figura sugerida (no capítulo de implementação, não no apêndice)

Diagrama do fluxo ETL:

```
DIEESE (CSV) → extract.py → transform.py → load.py → SQLite + CSV
                              ↓
                         eda.py / model.py
```

---

# APÊNDICE B — Notebook de Análise / EDA e Modelagem

## Texto para o corpo do TCC

> O Apêndice B documenta a análise exploratória de dados (EDA) e a modelagem preditiva conduzidas no notebook `analise_completa.ipynb`. O fluxo compreende: (i) execução do pipeline ETL; (ii) geração de gráficos exploratórios (evolução histórica, heatmap por capital, decomposição sazonal, boxplot regional e ranking); (iii) validação de modelos SARIMA e Prophet com divisão treino/teste (jan/2020–dez/2024 para treino; jan/2025–mar/2026 para teste); e (iv) projeções de cenários até dez/2030. As métricas de erro (MAE, RMSE e MAPE) e os gráficos de projeção constam neste apêndice. O notebook completo está em: https://github.com/The-P-P/cesta-basica-pipeline/blob/master/notebooks/analise_completa.ipynb

## Trechos do notebook a incluir (se não couber tudo)

1. Célula de importação e configuração
2. Célula `executar_pipeline()` com shape dos dados
3. Chamada `executar_eda(df)`
4. Chamada `executar_modelagem(df)` com saída das métricas
5. Tabela de métricas (copiar de `outputs/metricas_modelos.csv`)

## Gráficos para o Apêndice B (inserir como figuras)

| Figura | Arquivo |
|--------|---------|
| Evolução histórica nacional | `outputs/graficos/01_evolucao_historica_nacional.png` |
| Heatmap capitais | `outputs/graficos/02_heatmap_capitais.png` |
| Decomposição média nacional | `outputs/graficos/03_decomposicao_media_nacional.png` |
| Boxplot regional | `outputs/graficos/04_boxplot_regional.png` |
| Ranking mar/2026 | `outputs/graficos/05_ranking_capitais_marco2026.png` |
| Projeção média nacional (principal) | `outputs/graficos/projecao_media_nacional_2020_2030.png` |

## Tabela de métricas (cole no Apêndice B)

| Série | Modelo | MAE (R$) | RMSE (R$) | MAPE (%) |
|-------|--------|----------|-----------|----------|
| Média Nacional | SARIMA | 15,52 | 19,74 | 2,22 |
| Média Nacional | Prophet | 15,78 | 21,10 | 2,26 |

*Fonte: elaboração própria a partir de `outputs/metricas_modelos.csv`.*

## Legenda de figura (modelo ABNT)

> Figura X – Projeção do custo médio da cesta básica no Brasil (2020–2030) em três cenários de inflação alimentar (otimista 3%, moderado 4,5% e conservador 6% a.a.), com período histórico e faixa de incerteza. Fonte: DIEESE; elaboração própria.

---

# ANEXO A — Tabela de preços do DIEESE

## Texto para o corpo do TCC

> O Anexo A reproduz a base de dados extraída da Pesquisa Nacional da Cesta Básica, divulgada pelo Departamento Intersindical de Estatística e Estudos Socioeconômicos (DIEESE). O arquivo contém o custo mensal da cesta básica para as 27 capitais brasileiras, no formato `data`, `capital` e `custo` (em reais), totalizando 1.394 registros no período disponibilizado pela fonte. Os dados foram obtidos em [data de acesso] no endereço https://www.dieese.org.br/cestaBasica/

## Como anexar

**Opção 1 (recomendada para TCC digital):** Anexe o arquivo `data/raw/dieese_cesta_basica.csv` ao PDF final ou à mídia entregue à banca (pendrive/CD), e no documento escreva:

> O arquivo completo encontra-se em mídia anexa (`dieese_cesta_basica.csv`).

**Opção 2 (se a instituição exige tudo no PDF):** Inclua as primeiras e últimas 20 linhas como amostra e indique o repositório ou mídia para o arquivo integral.

**Opção 3 (tabela no Word):** Importe o CSV no Excel → formate como tabela → cole no Anexo A (pode gerar documento muito longo; use só se a norma da faculdade exigir).

## Amostra (primeiras linhas — já no projeto)

```
data,capital,custo
2020-01-01,Aracaju,368.69
2020-02-01,Aracaju,371.22
...
```

---

# ANEXO B — Metodologia oficial (DIEESE e IBGE)

## Texto para o corpo do TCC

> O Anexo B apresenta um resumo da metodologia oficial de cálculo da cesta básica pelo DIEESE e do Índice Nacional de Preços ao Consumidor Amplo (IPCA) pelo IBGE, fontes primárias que fundamentam a interpretação dos dados utilizados neste trabalho. O conteúdo integral das metodologias é de autoria dos respectivos órgãos e está disponível nos endereços oficiais citados abaixo.

## Conteúdo

Use o arquivo `anexo-b-metodologia-oficial.md` desta pasta: copie o texto para o Anexo B do Word ou converta para PDF.

**Referências oficiais para a lista bibliográfica:**

- DIEESE. *Pesquisa Nacional da Cesta Básica*. Disponível em: https://www.dieese.org.br/cestaBasica/. Acesso em: dd mmm. aaaa.
- IBGE. *IPCA — Índice Nacional de Preços ao Consumidor Amplo*. Disponível em: https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html. Acesso em: dd mmm. aaaa.

---

## Checklist final

- [ ] Apêndice A com trechos de código + link GitHub
- [ ] Apêndice B com gráficos principais + tabela de métricas
- [ ] Anexo A com CSV (mídia ou amostra + referência)
- [ ] Anexo B com resumo metodológico DIEESE/IBGE
- [ ] Cada apêndice/anexo referenciado no texto (ex.: "conforme Apêndice A")
- [ ] Lista de figuras e tabelas atualizada
- [ ] Data de acesso nas URLs do DIEESE e IBGE
