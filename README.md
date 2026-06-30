# Dashboard de KPIs de Vendas

Projeto em Python com Streamlit para acompanhar KPIs de vendas em um dashboard interativo. Os dados atuais sao simulados, mas a estrutura ja esta preparada para conectar uma API real de vendas.

## Funcionalidades

- Indicadores principais: faturamento total, numero de vendas, ticket medio e itens vendidos.
- Graficos interativos com Plotly por produto, canal, regiao e periodo.
- Filtros por produto, canal, regiao e intervalo de datas.
- Atualizacao manual e auto-refresh configuravel.
- Simulacao de falha de API para testar tratamento de erros.
- Limpeza automatica de dados duplicados e incompletos.

## Tecnologias

- Python
- Streamlit
- Pandas
- Plotly
- Requests

## Estrutura do projeto

```text
projetoApis/
+-- kpi-dashboard/
|   +-- app.py              # Interface do dashboard, filtros, KPIs e graficos
|   +-- data_source.py      # Fonte de dados simulada e ponto de conexao com API real
|   +-- data_cleaning.py    # Limpeza, padronizacao e remocao de duplicados
|   +-- requirements.txt    # Dependencias do projeto
|   +-- README.md           # Documentacao interna do dashboard
+-- .gitignore
+-- README.md
```

## Como executar

1. Acesse a pasta do dashboard:

```bash
cd kpi-dashboard
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

3. Instale as dependencias:

```bash
pip install -r requirements.txt
```

4. Execute o dashboard:

```bash
streamlit run app.py
```

Depois, acesse no navegador:

```text
http://localhost:8501
```

## Como funciona

O arquivo `data_source.py` gera vendas simuladas para permitir testar o dashboard sem depender de uma API externa. Esses dados passam por `data_cleaning.py`, que remove duplicidades, trata campos essenciais e cria a coluna `valor_total`.

O arquivo `app.py` monta a interface no Streamlit, exibe os KPIs, aplica filtros e gera os graficos com Plotly.

## Conectando uma API real

Para usar dados reais, edite a funcao `fetch_sales_data()` em `kpi-dashboard/data_source.py`.

A API deve retornar dados que possam ser transformados em um `DataFrame` com colunas equivalentes a:

| Coluna | Descricao |
| --- | --- |
| `id_venda` | Identificador unico da venda |
| `produto` | Nome do produto vendido |
| `canal` | Canal de venda |
| `regiao` | Regiao da venda |
| `quantidade` | Quantidade vendida |
| `valor_unitario` | Valor unitario do produto |
| `data_venda` | Data e hora da venda |

Caso a API use nomes diferentes, basta renomear as colunas antes de retornar o `DataFrame`.

## Possiveis melhorias

- Conectar com uma API real de vendas.
- Adicionar autenticacao para acesso ao dashboard.
- Persistir historico em banco de dados.
- Criar comparativos por periodo.
- Publicar o dashboard em uma plataforma como Streamlit Community Cloud.

## Autor

Projeto desenvolvido por Luis Alessandro.
