"""
data_source.py
----------------
Responsável por buscar os dados de vendas.

Hoje gera dados simulados (mock) para você testar o dashboard sem
depender de uma API real. Quando você tiver a API de vendas de verdade,
troque o corpo da função `fetch_sales_data()` pela chamada com `requests`
(exemplo comentado abaixo).
"""

import random
from datetime import datetime, timedelta

import pandas as pd
import requests


class SalesAPIError(Exception):
    """Erro ao buscar dados da API de vendas (timeout, indisponibilidade, etc)."""


# ---------------------------------------------------------------------------
# MOCK: gera vendas falsas para simular uma API em tempo real
# ---------------------------------------------------------------------------
PRODUTOS = ["Camiseta", "Tênis", "Boné", "Mochila", "Jaqueta", "Meia"]
CANAIS = ["Site", "App", "Loja Física", "Marketplace"]
REGIOES = ["Nordeste", "Sudeste", "Sul", "Centro-Oeste", "Norte"]


def _gerar_venda_falsa(id_base: int) -> dict:
    agora = datetime.now() - timedelta(minutes=random.randint(0, 600))
    return {
        "id_venda": id_base,
        "produto": random.choice(PRODUTOS),
        "canal": random.choice(CANAIS),
        "regiao": random.choice(REGIOES),
        "quantidade": random.randint(1, 5),
        "valor_unitario": round(random.uniform(20, 350), 2),
        "data_venda": agora,
    }


def fetch_sales_data(n: int = 300, simular_duplicados: bool = True, simular_falha: bool = False) -> pd.DataFrame:
    """
    Busca os dados de vendas.

    MODO ATUAL: gera dados simulados em memória.

    MODO REAL (exemplo): troque o corpo da função por algo assim,
    com tratamento de erro e timeout:

        try:
            resp = requests.get(
                "https://sua-api.com/vendas",
                headers={"Authorization": f"Bearer {os.environ['SALES_API_TOKEN']}"},
                timeout=10,
            )
            resp.raise_for_status()
        except requests.exceptions.Timeout:
            raise SalesAPIError("A API de vendas demorou demais para responder.")
        except requests.exceptions.ConnectionError:
            raise SalesAPIError("Não foi possível conectar à API de vendas.")
        except requests.exceptions.HTTPError as e:
            raise SalesAPIError(f"API de vendas retornou erro: {e}")

        dados = resp.json()
        return pd.DataFrame(dados)

    Args:
        n: quantidade de registros simulados a gerar.
        simular_duplicados: se True, injeta registros duplicados de propósito,
            para você ver a etapa de limpeza funcionando.
        simular_falha: se True, tem ~15% de chance de simular uma falha de API
            (útil para testar o tratamento de erro no dashboard).

    Raises:
        SalesAPIError: quando a "API" (simulada ou real) falha.
    """
    if simular_falha and random.random() < 0.15:
        raise SalesAPIError("Falha simulada: a API de vendas não respondeu a tempo.")

    registros = [_gerar_venda_falsa(i) for i in range(1, n + 1)]

    if simular_duplicados:
        # duplica ~8% dos registros para simular o problema real
        duplicados = random.sample(registros, k=max(1, n // 12))
        registros.extend(duplicados)

    df = pd.DataFrame(registros)
    return df
