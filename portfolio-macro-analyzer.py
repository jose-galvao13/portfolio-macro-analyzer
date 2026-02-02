import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Macro Portfolio Suite", page_icon="📈")

# Adicionar CSS para forçar Dark Mode bonito
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    div[data-testid="stMetric"] { background-color: #262730; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

class MacroTrendExplorer:
    def __init__(self):
        self.tickers = {
            'S&P 500': '^GSPC',         
            'US 10Y Yield': '^TNX', 
            'EUR/USD': 'EURUSD=X',      
            'Gold': 'GC=F',
            'Bitcoin': 'BTC-USD'
        }
        self.data = pd.DataFrame()
        self.metrics = pd.DataFrame()

    def fetch_long_term_data(self):
        # Cache no Streamlit para não sacar dados sempre que clicas num botão
        return self._get_data_internal()

    @st.cache_data(ttl=3600)
    def _get_data_internal(_self):
        # 1. Definir datas dinâmicas
        now = datetime.now()
        
        # Subtrair 730 dias (2 anos) à data de hoje
        start_date = (now - timedelta(days=730)).strftime("%Y-%m-%d")
        
        # Data de hoje formatada
        end_date = now.strftime("%Y-%m-%d")
        
        df_list = []
        for name, ticker in _self.tickers.items():
            try:
                df = yf.download(ticker, start=start_date, end=end_date, interval='1d', progress=False, auto_adjust=True)
                if df.empty: continue
                
                # Tratamento de Colunas
                if isinstance(df.columns, pd.MultiIndex):
                    try:
                        if 'Close' in df.columns.get_level_values(0):
                            df = df.xs('Close', axis=1, level=0, drop_level=True)
                        else: df = df.iloc[:, 0]
                    except: df = df.iloc[:, 0]
                elif 'Close' in df.columns: df = df[['Close']]
                else: df = df.iloc[:, 0]
                
                if df.shape[1] > 1: df = df.iloc[:, 0]
                
                df.columns = [name]
                if df.index.tz is not None: df.index = df.index.tz_localize(None)
                df_list.append(df)
            except Exception: pass

        if df_list:
            data = pd.concat(df_list, axis=1, join='outer')
            data.sort_index(inplace=True)
            data = data.ffill().bfill()
            data.dropna(inplace=True)
            return data
        return pd.DataFrame()

    def calculate_risk_metrics(self, data):
        if data.empty: return pd.DataFrame()

        stats = []
        risk_free_rate = 0.04 

        for col in data.columns:
            prices = data[col]
            total_return = (prices.iloc[-1] / prices.iloc[0]) - 1
            daily_returns = prices.pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(252)
            
            rolling_max = prices.cummax()
            drawdown = (prices - rolling_max) / rolling_max
            max_drawdown = drawdown.min()

            sharpe = (total_return - risk_free_rate) / volatility if volatility != 0 else 0

            stats.append({
                'Asset': col,
                'Total Return': total_return,
                'Volatility': volatility,
                'Max Drawdown': max_drawdown,
                'Sharpe Ratio': sharpe
            })
            
        return pd.DataFrame(stats)

# --- APLICAÇÃO WEB ---

# 1. Título e Cabeçalho
st.title("🏦 Portfolio Analytics Suite")
st.markdown("Real-time market monitoring, risk analysis, and correlations.")

# 2. Inicializar lógica
app = MacroTrendExplorer()
data = app.fetch_long_term_data()

if not data.empty:
    
   # 3. Métricas de Topo (KPIs Rápidos)
    col1, col2, col3, col4 = st.columns(4)
    
    # --- CORREÇÃO DE SEGURANÇA ---
    # Só calcula se a coluna existir. Se o Yahoo falhar, mostra "N/A" em vez de crashar.
    
    # S&P 500
    if 'S&P 500' in data.columns:
        sp500_ret = (data['S&P 500'].iloc[-1] / data['S&P 500'].iloc[0]) - 1
        col1.metric("S&P 500 (YTD)", f"{sp500_ret*100:.2f}%")
    else:
        col1.metric("S&P 500", "N/A", help="Falha no download dos dados")

    # Bitcoin
    if 'Bitcoin' in data.columns:
        btc_ret = (data['Bitcoin'].iloc[-1] / data['Bitcoin'].iloc[0]) - 1
        col2.metric("Bitcoin (YTD)", f"{btc_ret*100:.2f}%")
    else:
        col2.metric("Bitcoin", "N/A")

    col3.metric("Analysed Days", len(data))
    col4.metric("Last Update", data.index[-1].strftime('%Y-%m-%d'))

    # 4. Gráfico Interativo
    st.subheader("Market Performance")
    
    # Normalizar para gráfico
    base_prices = data.iloc[0]
    normalized_data = ((data / base_prices) - 1) * 100
    
    fig = go.Figure()
    colors = {'S&P 500': '#00B5F0', 'US 10Y Yield': '#FF3B30', 
              'EUR/USD': '#34C759', 'Gold': '#FFD60A', 'Bitcoin': '#BD00FF'}

    for col in normalized_data.columns:
        fig.add_trace(go.Scatter(
            x=normalized_data.index, y=normalized_data[col],
            mode='lines', name=col,
            line=dict(color=colors.get(col, 'white'), width=2),
            hovertemplate='%{y:.2f}%'
        ))

    fig.update_layout(
        template="plotly_dark", height=500,
        hovermode="x unified",
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(orientation="h", y=1.1, x=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

    # 5. Tabela Interativa
    st.subheader("Risk & Return Analysis")
    st.markdown("💡 *Click on the headings to sort. Hover your mouse to filter/search.*")
    
    metrics_df = app.calculate_risk_metrics(data)
    
    # CONFIGURAÇÃO DA TABELA INTERATIVA
    st.dataframe(
        metrics_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Asset": "Asset",
            "Total Return": st.column_config.NumberColumn(
                "Total Return",
                format="%.2f%%", # Formata como percentagem automaticamente
            ),
            "Volatility": st.column_config.NumberColumn(
                "Volatility",
                format="%.2f%%",
            ),
            "Max Drawdown": st.column_config.NumberColumn(
                "Max Drawdown",
                format="%.2f%%",
            ),
            "Sharpe Ratio": st.column_config.NumberColumn(
                "Sharpe Ratio",
                format="%.2f",
            ),
        }
    )

else:

    st.error("")




