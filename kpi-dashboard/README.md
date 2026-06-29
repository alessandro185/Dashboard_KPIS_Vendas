# Dashboard de KPIs - Vendas

Dashboard em tempo (quase) real para acompanhar métricas de vendas, com:

- Conexão com API de vendas (hoje simulada em `data_source.py`, pronta para trocar por uma API real)
- Limpeza automática de dados duplicados (`data_cleaning.py`)
- KPIs: faturamento total, ticket médio, quantidade de vendas e itens
- Gráficos interativos com Plotly: por produto, canal, região e linha do tempo
- Auto-refresh configurável para simular tempo real

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

Acesse em `http://localhost:8501`.

## Estrutura

```
kpi-dashboard/
├── app.py              # Dashboard (UI + KPIs + gráficos)
├── data_source.py       # Busca de dados (mock hoje, API real depois)
├── data_cleaning.py     # Limpeza de duplicados e tratamento
├── requirements.txt
└── README.md
```

## Conectando sua API de vendas real

Abra `data_source.py` e edite a função `fetch_sales_data()`. Já existe um
exemplo comentado usando `requests.get()`. O importante é que o retorno
seja um `pandas.DataFrame` com (pelo menos) estas colunas:

| coluna          | tipo              |
|------------------|-------------------|
| id_venda         | int/str           |
| produto          | str               |
| canal            | str               |
| regiao           | str               |
| quantidade       | int               |
| valor_unitario   | float             |
| data_venda       | datetime          |

Se sua API tiver nomes de campos diferentes, basta renomear as colunas do
DataFrame antes de retornar (`df.rename(columns={...})`).

## Próximos passos sugeridos

- Trocar o mock pela API real (Sabor Rápido, por exemplo, já tem endpoints
  de pagamento que podem alimentar este dashboard)
- Adicionar autenticação se for expor publicamente
- Persistir histórico em banco (MySQL, já usado nos seus outros projetos)
  para comparar períodos
- Adicionar filtros de data/canal/região na sidebar
