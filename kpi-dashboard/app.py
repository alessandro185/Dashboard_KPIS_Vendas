"""
app.py
-------
Dashboard de KPIs de Vendas.

Para rodar:
    streamlit run app.py
"""

import time

import pandas as pd
import plotly.express as px
import streamlit as st

from data_cleaning import limpar_dados
from data_source import SalesAPIError, fetch_sales_data

st.set_page_config(page_title="Dashboard de KPIs - Vendas", layout="wide", page_icon="📊")

# ---------------------------------------------------------------------------
# Cache: evita bater na API/banco a cada interação do usuário (filtro, etc).
# Só busca dados novos de fato a cada `ttl` segundos.
# ---------------------------------------------------------------------------
@st.cache_data(ttl=30, show_spinner="Buscando dados de vendas...")
def carregar_dados(n: int, simular_falha: bool) -> pd.DataFrame:
    return fetch_sales_data(n=n, simular_duplicados=True, simular_falha=simular_falha)


# ---------------------------------------------------------------------------
# Sidebar - configurações
# ---------------------------------------------------------------------------
st.sidebar.title("⚙️ Configurações")
qtd_registros = st.sidebar.slider("Qtd. de vendas simuladas", 50, 1000, 300, step=50)
auto_refresh = st.sidebar.checkbox("🔄 Atualizar automaticamente", value=False)
intervalo = st.sidebar.slider("Intervalo de atualização (segundos)", 5, 60, 10, disabled=not auto_refresh)
simular_falha = st.sidebar.checkbox(
    "⚠️ Simular falha de API (teste)",
    value=False,
    help="Ativa ~15% de chance da 'API' falhar, para testar o tratamento de erro.",
)

if st.sidebar.button("🔁 Atualizar agora"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(
    "Hoje os dados são simulados em `data_source.py`. "
    "Troque a função `fetch_sales_data()` pela chamada à sua API real "
    "de vendas quando estiver pronta."
)

# ---------------------------------------------------------------------------
# 1. Busca dos dados (API) - com tratamento de erro
# ---------------------------------------------------------------------------
try:
    df_bruto = carregar_dados(qtd_registros, simular_falha)
except SalesAPIError as e:
    st.error(f"🚫 Não foi possível carregar os dados de vendas.\n\n**Detalhe:** {e}")
    st.info("Tentando novamente em alguns segundos, ou clique em '🔁 Atualizar agora' na barra lateral.")
    st.stop()
except Exception as e:
    st.error(f"🚫 Erro inesperado ao carregar os dados: {e}")
    st.stop()

# ---------------------------------------------------------------------------
# 2. Limpeza dos dados
# ---------------------------------------------------------------------------
resultado = limpar_dados(df_bruto)
df = resultado["df"]
relatorio = resultado["relatorio"]

if df.empty:
    st.warning("Nenhum dado disponível após a limpeza.")
    st.stop()

# ---------------------------------------------------------------------------
# 3. Filtros (sidebar)
# ---------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros")

produtos_opts = sorted(df["produto"].unique())
canais_opts = sorted(df["canal"].unique())
regioes_opts = sorted(df["regiao"].unique())

f_produtos = st.sidebar.multiselect("Produto", produtos_opts, default=produtos_opts)
f_canais = st.sidebar.multiselect("Canal", canais_opts, default=canais_opts)
f_regioes = st.sidebar.multiselect("Região", regioes_opts, default=regioes_opts)

data_min = df["data_venda"].min().date()
data_max = df["data_venda"].max().date()
f_periodo = st.sidebar.date_input(
    "Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max,
)

df_filtrado = df[
    df["produto"].isin(f_produtos)
    & df["canal"].isin(f_canais)
    & df["regiao"].isin(f_regioes)
]

if isinstance(f_periodo, tuple) and len(f_periodo) == 2:
    inicio, fim = f_periodo
    df_filtrado = df_filtrado[
        (df_filtrado["data_venda"].dt.date >= inicio) & (df_filtrado["data_venda"].dt.date <= fim)
    ]

df = df_filtrado

# ---------------------------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------------------------
st.title("📊 Dashboard de KPIs - Vendas")
st.caption(f"Última atualização: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}")

with st.expander("🧹 Relatório de limpeza de dados"):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros recebidos", relatorio["total_inicial"])
    c2.metric("Duplicados (exatos)", relatorio["duplicados_exatos_removidos"])
    c3.metric("Duplicados (por ID)", relatorio["duplicados_por_id_removidos"])
    c4.metric("Registros válidos", relatorio["total_final"])

if df.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

# ---------------------------------------------------------------------------
# 4. KPIs principais
# ---------------------------------------------------------------------------
faturamento_total = df["valor_total"].sum()
ticket_medio = df["valor_total"].mean()
qtd_vendas = len(df)
qtd_itens = df["quantidade"].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}")
k2.metric("🧾 Vendas", f"{qtd_vendas}")
k3.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.2f}")
k4.metric("📦 Itens Vendidos", f"{int(qtd_itens)}")

st.markdown("---")

# ---------------------------------------------------------------------------
# 5. Gráficos
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    vendas_produto = (
        df.groupby("produto")["valor_total"].sum().sort_values(ascending=False).reset_index()
    )
    fig1 = px.bar(
        vendas_produto,
        x="produto",
        y="valor_total",
        title="Faturamento por Produto",
        labels={"valor_total": "Faturamento (R$)", "produto": "Produto"},
        color="produto",
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    vendas_canal = df.groupby("canal")["valor_total"].sum().reset_index()
    fig2 = px.pie(
        vendas_canal,
        names="canal",
        values="valor_total",
        title="Distribuição por Canal de Venda",
        hole=0.4,
    )
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    vendas_regiao = df.groupby("regiao")["valor_total"].sum().sort_values(ascending=False).reset_index()
    fig3 = px.bar(
        vendas_regiao,
        x="regiao",
        y="valor_total",
        title="Faturamento por Região",
        labels={"valor_total": "Faturamento (R$)", "regiao": "Região"},
        color="regiao",
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    df_tempo = df.copy()
    df_tempo["hora"] = df_tempo["data_venda"].dt.floor("h")
    vendas_tempo = df_tempo.groupby("hora")["valor_total"].sum().reset_index()
    fig4 = px.line(
        vendas_tempo,
        x="hora",
        y="valor_total",
        title="Faturamento ao Longo do Tempo",
        labels={"valor_total": "Faturamento (R$)", "hora": "Hora"},
        markers=True,
    )
    st.plotly_chart(fig4, use_container_width=True)

# ---------------------------------------------------------------------------
# 6. Tabela detalhada
# ---------------------------------------------------------------------------
with st.expander("📋 Ver dados detalhados"):
    st.dataframe(df.sort_values("data_venda", ascending=False), use_container_width=True)

# ---------------------------------------------------------------------------
# 7. Auto-refresh (simula tempo real)
# ---------------------------------------------------------------------------
if auto_refresh:
    time.sleep(intervalo)
    st.cache_data.clear()
    st.rerun()
