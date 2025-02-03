import pandas as pd
import streamlit as st
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

def train_arima(df, forecast_days=7):
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    df = df.set_index('data_hora')
    
    # Seleciona apenas a coluna de engajamento total para a previsão
    df = df.resample('D').sum()  # Agrupa por dia e soma os valores
    df = df[['total']]

    # Treina o modelo ARIMA
    model = ARIMA(df['total'], order=(5,1,0))  # Parâmetros podem ser ajustados
    model_fit = model.fit()

    # Faz previsão para os próximos dias
    forecast = model_fit.forecast(steps=forecast_days)

    # Plotando a previsão
    plt.figure(figsize=(10,5))
    plt.plot(df.index, df['total'], label="Dados Reais")
    plt.plot(pd.date_range(df.index[-1], periods=forecast_days+1, freq='D')[1:], forecast, label="Previsão", linestyle='dashed')
    plt.xlabel("Data")
    plt.ylabel("Engajamento")
    plt.title("Previsão de Engajamento com ARIMA")
    plt.legend()
    st.pyplot(plt)

    return forecast
