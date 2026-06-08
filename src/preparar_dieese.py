"""
Converte exportação DIEESE (.xls) para o formato do pipeline.

Uso:
    python preparar_dieese.py "caminho/para/exporta.xls"

Saída:
    data/raw/dieese_cesta_basica.csv
"""

import re
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
SAIDA_PADRAO = BASE_DIR / "data" / "raw" / "dieese_cesta_basica.csv"

# Capitais do pipeline (Macaé do DIEESE é excluída — não é capital estadual)
CAPITAIS_VALIDAS = {
    "brasilia": "Brasília",
    "campo grande": "Campo Grande",
    "cuiaba": "Cuiabá",
    "goiania": "Goiânia",
    "belo horizonte": "Belo Horizonte",
    "rio de janeiro": "Rio de Janeiro",
    "sao paulo": "São Paulo",
    "vitoria": "Vitória",
    "curitiba": "Curitiba",
    "florianopolis": "Florianópolis",
    "porto alegre": "Porto Alegre",
    "belem": "Belém",
    "boa vista": "Boa Vista",
    "macapa": "Macapá",
    "manaus": "Manaus",
    "palmas": "Palmas",
    "porto velho": "Porto Velho",
    "rio branco": "Rio Branco",
    "aracaju": "Aracaju",
    "fortaleza": "Fortaleza",
    "joao pessoa": "João Pessoa",
    "maceio": "Maceió",
    "natal": "Natal",
    "recife": "Recife",
    "salvador": "Salvador",
    "sao luis": "São Luís",
    "teresina": "Teresina",
}


def _normalizar_texto(texto: str) -> str:
    """Remove acentos e padroniza para comparação."""
    import unicodedata

    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower().strip()


def _mapear_capital(nome_coluna: str) -> str | None:
    """Mapeia nome da coluna DIEESE para nome padrão do pipeline."""
    chave = _normalizar_texto(nome_coluna)
    return CAPITAIS_VALIDAS.get(chave)


def _parsear_data(valor: str) -> pd.Timestamp | None:
    """Converte 'MM-AAAA' em datetime (primeiro dia do mês)."""
    if not isinstance(valor, str):
        return None
    match = re.match(r"^(\d{2})-(\d{4})$", valor.strip())
    if not match:
        return None
    mes, ano = int(match.group(1)), int(match.group(2))
    return pd.Timestamp(year=ano, month=mes, day=1)


def converter_dieese(caminho_entrada: str | Path, caminho_saida: Path = SAIDA_PADRAO) -> pd.DataFrame:
    """
    Lê XLS exportado do DIEESE (formato largo) e gera CSV longo.
    Colunas de saída: data, capital, custo
    """
    caminho_entrada = Path(caminho_entrada)
    if not caminho_entrada.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_entrada}")

    df_largo = pd.read_excel(caminho_entrada, sheet_name=0, header=1)

    col_data = df_largo.columns[0]
    registros = []

    for _, linha in df_largo.iterrows():
        data = _parsear_data(linha[col_data])
        if data is None:
            continue

        for coluna in df_largo.columns[1:]:
            capital = _mapear_capital(coluna)
            if capital is None:
                continue

            valor = linha[coluna]
            if pd.isna(valor):
                continue

            registros.append({
                "data": data,
                "capital": capital,
                "custo": round(float(valor), 2),
            })

    df = pd.DataFrame(registros)
    if df.empty:
        raise ValueError("Nenhum dado válido encontrado no arquivo DIEESE.")

    df = df.sort_values(["capital", "data"]).reset_index(drop=True)

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho_saida, index=False, encoding="utf-8-sig")

    return df


def exibir_resumo(df: pd.DataFrame) -> None:
    """Imprime resumo da conversão."""
    print(f"\nRegistros convertidos: {len(df)}")
    print(f"Capitais: {df['capital'].nunique()}")
    print(f"Período: {df['data'].min().strftime('%m/%Y')} a {df['data'].max().strftime('%m/%Y')}")

    cobertura = df.groupby("capital").agg(
        registros=("custo", "count"),
        inicio=("data", "min"),
        fim=("data", "max"),
    )
    incompletas = cobertura[cobertura["registros"] < 60]
    if not incompletas.empty:
        print("\nCapitais com histórico curto neste arquivo:")
        for capital, row in incompletas.iterrows():
            print(
                f"  - {capital}: {row['registros']} meses "
                f"({row['inicio'].strftime('%m/%Y')} a {row['fim'].strftime('%m/%Y')})"
            )
        print("\nDica: no site do DIEESE, exporte um período maior para essas capitais.")


if __name__ == "__main__":
    entrada = sys.argv[1] if len(sys.argv) > 1 else BASE_DIR / "data" / "raw" / "exporta.xls"
    df_convertido = converter_dieese(entrada)
    exibir_resumo(df_convertido)
    print(f"\nCSV salvo em: {SAIDA_PADRAO}")
