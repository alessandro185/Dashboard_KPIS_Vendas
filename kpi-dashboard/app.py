"""
app.py
------
Dashboard de KPIs de Vendas.

Para rodar:
    streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from data_cleaning import limpar_dados
from data_source import SalesAPIError, fetch_sales_data

st.set_page_config(page_title="Dashboard de KPIs - Vendas", layout="wide", page_icon="📊")


# ---------------------------------------------------------------------------
# Cache: evita bater na API a cada interação (filtro, etc).
# Só busca dados novos de fato a cada `ttl` segundos.
# ---------------------------------------------------------------------------
@st.cache_data(ttl=30, show_spinner="Buscando dados de vendas...")
def carregar_dados(n: int, simular_falha: bool, seed: int | None) -> pd.DataFrame:
    return fetch_sales_data(n=n, simular_duplicados=True, simular_falha=simular_falha, seed=seed)


# ---------------------------------------------------------------------------
# Sidebar - configurações
# ---------------------------------------------------------------------------
st.sidebar.title("⚙️ Configurações")
qtd_registros = st.sidebar.slider("Qtd. de vendas simuladas", 50, 1000, 300, step=50)
usar_seed = st.sidebar.checkbox(
    "🎲 Dados reproduzíveis (seed fixa)",
    value=False,
    help="Gera sempre o mesmo conjunto simulado. Útil para testar.",
)
auto_refresh = st.sidebar.checkbox("🔄 Atualizar automaticamente", value=False)
intervalo = st.sidebar.slider(
    "Intervalo de atualização (segundos)", 5, 60, 10, disabled=not auto_refresh
)
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
    "Os dados são simulados em `data_source.py`. "
    "Troque `fetch_sales_data()` pela chamada à sua API real quando estiver pronta."
)
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros")


def _multiselect(rotulo: str, chave: str, opcoes: list[str]) -> list[str]:
    """Multiselect que preserva a seleção do usuário entre atualizações."""
    atual = st.session_state.get(chave)
    if atual is None:
        st.session_state[chave] = list(opcoes)
    else:
        st.session_state[chave] = [o for o in atual if o in opcoes]
    return st.sidebar.multiselect(rotulo, opcoes, key=chave)


# ---------------------------------------------------------------------------
# Corpo do dashboard. É um fragment: com auto-refresh ligado, só esta parte
# é reexecutada a cada `intervalo` segundos, sem bloquear a interface.
# ---------------------------------------------------------------------------
@st.fragment(run_every=intervalo if auto_refresh else None)
def dashboard() -> None:
    # 1. Busca (com tratamento de erro)
    try:
        df_bruto = carregar_dados(qtd_registros, simular_falha, 42 if usar_seed else None)
    except SalesAPIError as e:
        st.error(f"🚫 Não foi possível carregar os dados de vendas.\n\n**Detalhe:** {e}")
        st.info("Tente novamente em alguns segundos ou clique em '🔁 Atualizar agora'.")
        return
    except Exception as e:
        st.error(f"🚫 Erro inesperado ao carregar os dados: {e}")
        return

    # 2. Limpeza
    resultado = limpar_dados(df_bruto)
    df = resultado["df"]
    relatorio = resultado["relatorio"]

    if df.empty:
        st.warning("Nenhum dado disponível após a limpeza.")
        return

    # 3. Filtros
    f_produtos = _multiselect("Produto", "f_produtos", sorted(df["produto"].unique()))
    f_canais = _multiselect("Canal", "f_canais", sorted(df["canal"].unique()))
    f_regioes = _multiselect("Região", "f_regioes", sorted(df["regiao"].unique()))

    data_min = df["data_venda"].min().date()
    data_max = df["data_venda"].max().date()
    periodo = st.session_state.get("f_periodo")
    if not (isinstance(periodo, tuple) and len(periodo) == 2):
        periodo = (data_min, data_max)
    # mantém o período escolhido dentro dos limites dos dados atuais
    st.session_state["f_periodo"] = (max(periodo[0], data_min), min(periodo[1], data_max))
    f_periodo = st.sidebar.date_input(
        "Período", key="f_periodo", min_value=data_min, max_value=data_max
    )

    df = df[
        df["produto"].isin(f_produtos)
        & df["canal"].isin(f_canais)
        & df["regiao"].isin(f_regioes)
    ]
    if isinstance(f_periodo, tuple) and len(f_periodo) == 2:
        inicio, fim = f_periodo
        df = df[(df["data_venda"].dt.date >= inicio) & (df["data_venda"].dt.date <= fim)]

    # Cabeçalho
    st.title("📊 Dashboard de KPIs - Vendas")
    st.caption(f"Última atualização: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}")

    with st.expander("🧹 Relatório de limpeza de dados"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Registros recebidos", relatorio["total_inicial"])
        c2.metric("Duplicados (exatos)", relatorio["duplicados_exatos_removidos"])
        c3.metric("Duplicados (por ID)", relatorio["duplicados_por_id_removidos"])
        c4, c5, c6 = st.columns(3)
        c4.metric("Incompletos", relatorio["linhas_incompletas_removidas"])
        c5.metric("Valores inválidos", relatorio["valores_invalidos_removidos"])
        c6.metric("Registros válidos", relatorio["total_final"])

    if df.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        return

    # 4. KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Faturamento Total", f"R$ {df['valor_total'].sum():,.2f}")
    k2.metric("🧾 Vendas", f"{len(df)}")
    k3.metric("🎯 Ticket Médio", f"R$ {df['valor_total'].mean():,.2f}")
    k4.metric("📦 Itens Vendidos", f"{int(df['quantidade'].sum())}")

    st.markdown("---")

    # 5. Gráficos
    col1, col2 = st.columns(2)
    with col1:
        por_produto = (
            df.groupby("produto")["valor_total"].sum().sort_values(ascending=False).reset_index()
        )
        fig = px.bar(
            por_produto, x="produto", y="valor_total", color="produto",
            title="Faturamento por Produto",
            labels={"valor_total": "Faturamento (R$)", "produto": "Produto"},
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        por_canal = df.groupby("canal")["valor_total"].sum().reset_index()
        fig = px.pie(
            por_canal, names="canal", values="valor_total", hole=0.4,
            title="Distribuição por Canal de Venda",
        )
        st.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        por_regiao = (
            df.groupby("regiao")["valor_total"].sum().sort_values(ascending=False).reset_index()
        )
        fig = px.bar(
            por_regiao, x="regiao", y="valor_total", color="regiao",
            title="Faturamento por Região",
            labels={"valor_total": "Faturamento (R$)", "regiao": "Região"},
        )
        st.plotly_chart(fig, width="stretch")

    with col4:
        por_hora = (
            df.assign(hora=df["data_venda"].dt.floor("h"))
            .groupby("hora")["valor_total"].sum().reset_index()
        )
        fig = px.line(
            por_hora, x="hora", y="valor_total", markers=True,
            title="Faturamento ao Longo do Tempo",
            labels={"valor_total": "Faturamento (R$)", "hora": "Hora"},
        )
        st.plotly_chart(fig, width="stretch")

    # 6. Tabela detalhada
    with st.expander("📋 Ver dados detalhados"):
        st.dataframe(df.sort_values("data_venda", ascending=False), width="stretch")


dashboard()
