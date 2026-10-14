"""
data_source.py
--------------
Responsável por buscar os dados de vendas.

Hoje gera dados simulados (mock) para testar o dashboard sem depender de
uma API real. Para usar uma API de verdade, troque o corpo de
`fetch_sales_data()` (exemplo comentado na função).
"""

import random
from datetime import datetime, timedelta

import pandas as pd


class SalesAPIError(Exception):
    """Erro ao buscar dados da API de vendas (timeout, indisponibilidade, etc)."""


PRODUTOS = ["Camiseta", "Tênis", "Boné", "Mochila", "Jaqueta", "Meia"]
CANAIS = ["Site", "App", "Loja Física", "Marketplace"]
REGIOES = ["Nordeste", "Sudeste", "Sul", "Centro-Oeste", "Norte"]


def _gerar_venda_falsa(id_base: int, rng: random.Random) -> dict:
    momento = datetime.now() - timedelta(minutes=rng.randint(0, 600))
    return {
        "id_venda": id_base,
        "produto": rng.choice(PRODUTOS),
        "canal": rng.choice(CANAIS),
        "regiao": rng.choice(REGIOES),
        "quantidade": rng.randint(1, 5),
        "valor_unitario": round(rng.uniform(20, 350), 2),
        "data_venda": momento,
    }


def fetch_sales_data(
    n: int = 300,
    simular_duplicados: bool = True,
    simular_falha: bool = False,
    seed: int | None = None,
) -> pd.DataFrame:
    """
    Busca os dados de vendas.

    MODO ATUAL: gera dados simulados em memória.

    MODO REAL (exemplo): troque o corpo da função por algo assim:

        import os
        import requests

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

        return pd.DataFrame(resp.json())

    Args:
        n: quantidade de registros simulados a gerar.
        simular_duplicados: injeta dois tipos de duplicata para exercitar a
            limpeza: cópias exatas e reenvios com o mesmo id_venda, mas
            data ligeiramente diferente (como uma API que reenvia o registro).
        simular_falha: ~15% de chance de simular falha de API.
        seed: fixa a aleatoriedade (útil para testes reproduzíveis).

    Raises:
        SalesAPIError: quando a "API" (simulada ou real) falha.
    """
    rng = random.Random(seed)

    if simular_falha and rng.random() < 0.15:
        raise SalesAPIError("Falha simulada: a API de vendas não respondeu a tempo.")

    registros = [_gerar_venda_falsa(i, rng) for i in range(1, n + 1)]

    if simular_duplicados:
        k = max(1, n // 25)
        amostra = rng.sample(registros, k=2 * k)

        # 1) cópias exatas
        registros.extend(dict(r) for r in amostra[:k])

        # 2) reenvios: mesmo id_venda, data_venda ligeiramente diferente
        for r in amostra[k:]:
            reenvio = dict(r)
            reenvio["data_venda"] = r["data_venda"] + timedelta(seconds=rng.randint(1, 90))
            registros.append(reenvio)

    return pd.DataFrame(registros)
