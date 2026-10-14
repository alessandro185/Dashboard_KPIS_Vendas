import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kpi-dashboard"))

from data_cleaning import limpar_dados  # noqa: E402
from data_source import fetch_sales_data  # noqa: E402


def _base():
    return pd.DataFrame(
        {
            "id_venda": [1, 2, 3],
            "produto": ["A", "B", "C"],
            "canal": ["Site"] * 3,
            "regiao": ["Sul"] * 3,
            "quantidade": [1, 2, 3],
            "valor_unitario": [10.0, 20.0, 30.0],
            "data_venda": pd.to_datetime(["2026-01-01 10:00"] * 3),
        }
    )


def test_remove_duplicados_exatos():
    df = pd.concat([_base(), _base().iloc[[0]]], ignore_index=True)
    r = limpar_dados(df)
    assert r["relatorio"]["duplicados_exatos_removidos"] == 1
    assert len(r["df"]) == 3


def test_remove_duplicados_por_id():
    reenvio = _base().iloc[[0]].copy()
    reenvio["data_venda"] = reenvio["data_venda"] + pd.Timedelta(seconds=30)
    r = limpar_dados(pd.concat([_base(), reenvio], ignore_index=True))
    assert r["relatorio"]["duplicados_por_id_removidos"] == 1
    assert len(r["df"]) == 3


def test_remove_incompletos_e_invalidos():
    df = _base()
    df.loc[0, "produto"] = None
    df.loc[1, "quantidade"] = 0
    r = limpar_dados(df)
    assert r["relatorio"]["linhas_incompletas_removidas"] == 1
    assert r["relatorio"]["valores_invalidos_removidos"] == 1
    assert len(r["df"]) == 1


def test_valor_total():
    r = limpar_dados(_base())
    assert list(r["df"]["valor_total"]) == [10.0, 40.0, 90.0]


def test_mock_gera_ambos_tipos_de_duplicata_e_limpa_tudo():
    bruto = fetch_sales_data(n=300, seed=42)
    r = limpar_dados(bruto)
    rel = r["relatorio"]
    assert rel["duplicados_exatos_removidos"] > 0
    assert rel["duplicados_por_id_removidos"] > 0
    assert len(r["df"]) == 300
