"""
data_cleaning.py
----------------
Funções de limpeza e padronização dos dados de vendas vindos da API.
"""

import pandas as pd


def limpar_dados(df: pd.DataFrame) -> dict:
    """
    Limpa o DataFrame de vendas e retorna o df limpo + um relatório
    do que foi feito (útil para mostrar no dashboard).

    Etapas:
      1. Converte tipos (datas e números).
      2. Remove duplicados exatos.
      3. Remove duplicados por id_venda (mesma venda reenviada pela API).
      4. Remove linhas com campos essenciais nulos ou inválidos.
      5. Remove valores inválidos (quantidade ou valor <= 0).
      6. Cria a coluna 'valor_total' (quantidade x valor_unitario).
    """
    total_inicial = len(df)
    relatorio = {
        "duplicados_exatos_removidos": 0,
        "duplicados_por_id_removidos": 0,
        "linhas_incompletas_removidas": 0,
        "valores_invalidos_removidos": 0,
    }

    df = df.copy()

    # 1. Tipos corretos (antes de comparar duplicados e nulos)
    if "data_venda" in df.columns:
        df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
    for col in ("quantidade", "valor_unitario"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 2. Duplicados exatos
    antes = len(df)
    df = df.drop_duplicates()
    relatorio["duplicados_exatos_removidos"] = antes - len(df)

    # 3. Duplicados por id_venda (mantém a primeira ocorrência)
    if "id_venda" in df.columns:
        antes = len(df)
        df = df.drop_duplicates(subset="id_venda", keep="first")
        relatorio["duplicados_por_id_removidos"] = antes - len(df)

    # 4. Campos essenciais ausentes (inclui valores que não puderam ser convertidos)
    essenciais = [
        c for c in ["produto", "valor_unitario", "quantidade", "data_venda"] if c in df.columns
    ]
    antes = len(df)
    df = df.dropna(subset=essenciais)
    relatorio["linhas_incompletas_removidas"] = antes - len(df)

    # 5. Valores inválidos
    antes = len(df)
    if "quantidade" in df.columns:
        df = df[df["quantidade"] > 0]
    if "valor_unitario" in df.columns:
        df = df[df["valor_unitario"] > 0]
    relatorio["valores_invalidos_removidos"] = antes - len(df)

    # 6. Coluna derivada
    if {"quantidade", "valor_unitario"}.issubset(df.columns):
        df["valor_total"] = df["quantidade"] * df["valor_unitario"]

    relatorio["total_inicial"] = total_inicial
    relatorio["total_final"] = len(df)
    relatorio["total_removido"] = total_inicial - len(df)

    return {"df": df.reset_index(drop=True), "relatorio": relatorio}
