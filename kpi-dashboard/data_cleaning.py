"""
data_cleaning.py
-----------------
Funções de limpeza e padronização dos dados de vendas vindos da API.
"""

import pandas as pd


def limpar_dados(df: pd.DataFrame) -> dict:
    """
    Limpa o DataFrame de vendas e retorna o df limpo + um relatório
    do que foi feito (útil para mostrar no dashboard).

    Etapas:
      1. Remove duplicados exatos (mesma linha repetida).
      2. Remove duplicados por id_venda (mesma venda reenviada pela API).
      3. Remove linhas com campos essenciais nulos.
      4. Garante tipos corretos (datas, números).
      5. Cria coluna 'valor_total' (quantidade x valor_unitario).
    """
    relatorio = {}
    total_inicial = len(df)

    df = df.copy()

    # 1. Duplicados exatos
    antes = len(df)
    df = df.drop_duplicates()
    relatorio["duplicados_exatos_removidos"] = antes - len(df)

    # 2. Duplicados por id_venda (mantém a primeira ocorrência)
    if "id_venda" in df.columns:
        antes = len(df)
        df = df.drop_duplicates(subset="id_venda", keep="first")
        relatorio["duplicados_por_id_removidos"] = antes - len(df)

    # 3. Remove linhas com campos essenciais ausentes
    campos_essenciais = [c for c in ["produto", "valor_unitario", "quantidade", "data_venda"] if c in df.columns]
    antes = len(df)
    df = df.dropna(subset=campos_essenciais)
    relatorio["linhas_incompletas_removidas"] = antes - len(df)

    # 4. Tipos corretos
    if "data_venda" in df.columns:
        df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
    if "quantidade" in df.columns:
        df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
    if "valor_unitario" in df.columns:
        df["valor_unitario"] = pd.to_numeric(df["valor_unitario"], errors="coerce")

    df = df.dropna(subset=campos_essenciais)

    # 5. Coluna derivada
    if {"quantidade", "valor_unitario"}.issubset(df.columns):
        df["valor_total"] = df["quantidade"] * df["valor_unitario"]

    relatorio["total_inicial"] = total_inicial
    relatorio["total_final"] = len(df)
    relatorio["total_removido"] = total_inicial - len(df)

    return {"df": df.reset_index(drop=True), "relatorio": relatorio}
