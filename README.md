# Dashboard de KPIs de Vendas

Dashboard interativo em Python + Streamlit para acompanhar KPIs de vendas. Os dados atuais são simulados, mas a estrutura está pronta para conectar uma API real.

<!-- Adicione aqui um screenshot ou GIF: ![Dashboard](docs/screenshot.png) -->
**Demo Online (Vercel):** [https://dashboard-kpis-vendas.vercel.app](https://dashboard-kpis-vendas.vercel.app)

## Funcionalidades

- **KPIs:** faturamento total, número de vendas, ticket médio e itens vendidos.
- **Gráficos interativos (Plotly):** por produto, canal, região e ao longo do tempo.
- **Filtros** por produto, canal, região e intervalo de datas (preservados entre atualizações).
- **Auto-refresh** configurável, sem travar a interface (`st.fragment`).
- **Limpeza automática de dados:** duplicados exatos, reenvios com o mesmo `id_venda`, campos ausentes e valores inválidos, com relatório na tela.
- **Simulação de falha de API** para testar o tratamento de erros.
- **Testes automatizados** (`pytest`) para a limpeza de dados.

## Tecnologias

Python · Streamlit · Pandas · Plotly · Requests · Pytest

## Estrutura

```text
Dashboard_KPIS_Vendas/
├── kpi-dashboard/
│   ├── app.py              # Interface: filtros, KPIs e gráficos
│   ├── data_source.py      # Fonte de dados simulada / ponto de conexão com API real
│   ├── data_cleaning.py    # Limpeza, padronização e remoção de duplicados
│   └── requirements.txt
├── tests/
│   └── test_data_cleaning.py
├── .gitignore
└── README.md
```

## Como executar

```bash
cd kpi-dashboard
python -m venv .venv
# Windows: .venv\Scripts\activate    |    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Acesse `http://localhost:8501`.

### Testes

Na raiz do projeto:

```bash
python -m pytest
```

## Como funciona

1. `data_source.py` gera vendas simuladas (incluindo duplicatas de propósito).
2. `data_cleaning.py` limpa os dados e cria a coluna `valor_total`.
3. `app.py` aplica os filtros, calcula os KPIs e desenha os gráficos.

## Conectando uma API real

Edite `fetch_sales_data()` em `kpi-dashboard/data_source.py` (há um exemplo comentado com `requests`, timeout e tratamento de erros). A API deve retornar dados convertíveis em um `DataFrame` com estas colunas (renomeie com `df.rename(columns={...})` se necessário):

| Coluna | Tipo | Descrição |
| --- | --- | --- |
| `id_venda` | int/str | Identificador único da venda |
| `produto` | str | Produto vendido |
| `canal` | str | Canal de venda |
| `regiao` | str | Região da venda |
| `quantidade` | int | Quantidade vendida |
| `valor_unitario` | float | Valor unitário |
| `data_venda` | datetime | Data e hora da venda |

## Próximos passos

- Conectar a uma API real de vendas.
- Comparativo com o período anterior (deltas nos KPIs).
- Persistir histórico em banco de dados (ex.: MySQL).
- Autenticação, se for exposto publicamente.
- Deploy no Streamlit Community Cloud.

## Autor

Projeto desenvolvido por Luis Alessandro.
