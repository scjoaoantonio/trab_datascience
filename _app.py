import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Estilizando com CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
    }
    .stMarkdown h1 {
        color: white;
    }
    .css-1d391kg {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
def mainPage():
    st.title("Snowflake Healthcare App")

    # Gerando dados aleatórios para os gráficos
    np.random.seed(42)
    x = np.arange(20)
    y1 = np.random.randn(20)
    y2 = np.random.randn(20)
    y3 = np.random.randn(20)

    # Criando gráficos com Plotly
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=x, y=y1, fill='tozeroy', mode='lines', name='a'))
    fig1.add_trace(go.Scatter(x=x, y=y2, fill='tozeroy', mode='lines', name='b'))
    fig1.add_trace(go.Scatter(x=x, y=y3, fill='tozeroy', mode='lines', name='c'))

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=x, y=y1, name='a'))
    fig2.add_trace(go.Bar(x=x, y=y2, name='b'))
    fig2.add_trace(go.Bar(x=x, y=y3, name='c'))

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=x, y=y1, mode='lines', name='a'))
    fig3.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='b'))
    fig3.add_trace(go.Scatter(x=x, y=y3, mode='lines', name='c'))

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=x, y=y1, mode='lines', name='a'))
    fig4.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='b'))
    fig4.add_trace(go.Scatter(x=x, y=y3, mode='lines', name='c'))

    # Exibindo os gráficos lado a lado
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1, use_container_width=True)
    col2.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    col3.plotly_chart(fig3, use_container_width=True)
    col4.plotly_chart(fig4, use_container_width=True)
