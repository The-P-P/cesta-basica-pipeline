# ANEXO B — Metodologia oficial da Cesta Básica (DIEESE) e do IPCA (IBGE)

*Material de terceiros — resumo para fins acadêmicos. Consulte sempre as versões atualizadas nos sites oficiais.*

---

## B.1 Pesquisa Nacional da Cesta Básica — DIEESE

### B.1.1 Objetivo

A Pesquisa Nacional da Cesta Básica, conduzida pelo Departamento Intersindical de Estatística e Estudos Socioeconômicos (DIEESE), tem como finalidade acompanhar mensalmente o custo de um conjunto padronizado de alimentos nas capitais brasileiras. O indicador expressa, em reais, quanto uma família tipo precisaria gastar mensalmente para adquirir os itens que compõem a cesta básica naquele município.

### B.1.2 Composição da cesta

A cesta básica do DIEESE é formada por **13 grupos de alimentos**, com quantidades definidas com base em necessidades nutricionais de referência para uma família de **quatro pessoas** (dois adultos e duas crianças), correspondendo a aproximadamente **3.000 kcal por dia por pessoa**. Os grupos incluem, entre outros: cereais e leguminosas; carnes e ovos; leite e derivados; hortaliças; frutas; açúcares e derivados; óleos e gorduras; café, chá e mate; sal e condimentos.

As quantidades e a lista de produtos representativos podem ser ajustadas periodicamente pelo DIEESE para refletir o padrão de consumo da população de baixa renda.

### B.1.3 Coleta de preços

Os preços são levantados em **supermercados, mercearias e feiras livres** de cada capital, em datas padronizadas ao longo do mês. Para cada item, são registrados os preços de produtos representativos da região. O custo mensal da cesta é obtido pela soma do custo de cada grupo:

**Custo da cesta = Σ (quantidade do item × preço unitário)**

### B.1.4 Abrangência e periodicidade

A pesquisa cobre as **27 capitais** dos estados brasileiros. Os resultados são divulgados mensalmente no portal do DIEESE, em formato tabular e histórico acumulado.

### B.1.5 Limitações relevantes para este trabalho

- O indicador mede o **custo nominal** da cesta em cada capital, não um índice de variação percentual (como o IPCA).
- Os valores **não incluem** outros componentes do custo de vida (moradia, transporte, saúde etc.).
- Diferenças metodológicas entre capitais (pontos de venda, sazonalidade local) afetam a comparabilidade direta entre cidades.
- A disponibilidade histórica no portal pode apresentar **lacunas** ou formatos distintos, exigindo tratamento na etapa de extração do pipeline.

**Fonte oficial:** DIEESE. *Pesquisa Nacional da Cesta Básica*. Disponível em: https://www.dieese.org.br/cestaBasica/. Acesso em: ___/___/2026.

---

## B.2 Índice Nacional de Preços ao Consumidor Amplo — IBGE (IPCA)

### B.2.1 Objetivo

O Índice Nacional de Preços ao Consumidor Amplo (IPCA), calculado pelo Instituto Brasileiro de Geografia e Estatística (IBGE), mede a variação dos preços de um conjunto de produtos e serviços consumidos pelas famílias com renda de **1 a 40 salários mínimos** nas áreas urbanas de **11 regiões metropolitanas** e do município de Goiânia. É o índice oficial de inflação utilizado pelo Banco Central na meta de inflação.

### B.2.2 Metodologia geral

O IPCA é um **índice de Laspeyres encadeado**: compara os preços do período atual com os do período base, ponderados pela estrutura de gastos das famílias (Pesquisa de Orçamentos Familiares — POF). A coleta ocorre entre o **primeiro e o último dia útil** de cada mês.

### B.2.3 Estrutura e ponderação

Os itens são organizados em **nove grupos** (alimentação e bebidas; habitação; artigos de residência; vestuário; transportes; saúde e cuidados pessoais; despesas pessoais; educação; comunicação). Cada item possui peso na cesta de consumo das famílias pesquisadas. O grupo **Alimentação e bebidas** é frequentemente utilizado em estudos sobre custo de alimentos, por sua correlação com indicadores como a cesta básica.

### B.2.4 Cálculo

A variação do índice no mês é obtida pela agregação ponderada das variações de preço dos subitens:

**IPCA_mês = Σ (peso_i × variação_preço_i)**

Os índices são encadeados para formar séries históricas de inflação acumulada.

### B.2.5 Relação com este trabalho

No pipeline desenvolvido, referências ao IPCA (especialmente do subgrupo alimentação) foram utilizadas para **calibrar cenários de projeção** e a reconstrução histórica híbrida, uma vez que o DIEESE divulga valores nominais e nem sempre cobre todo o horizonte temporal desejado (2020–2026) de forma uniforme para todas as capitais. O IPCA não substitui os dados do DIEESE na análise principal, mas fundamenta premissas de inflação nos cenários otimista (3%), moderado (4,5%) e conservador (6% a.a.).

**Fonte oficial:** IBGE. *IPCA — Índice Nacional de Preços ao Consumidor Amplo*. Disponível em: https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html. Acesso em: ___/___/2026.

---

## B.3 Documentos complementares (opcional na mídia anexa)

Se a banca solicitar cópia integral das metodologias, baixe e anexe em PDF:

| Documento | Onde obter |
|-----------|------------|
| Nota metodológica da Cesta Básica | https://www.dieese.org.br/analisecestabasica/notaMetodologica.html |
| Metodologia do IPCA (IBGE) | Portal do IPCA → aba "Metodologia" no site do IBGE |
