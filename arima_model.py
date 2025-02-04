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

import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import numpy as np

# Carregar os dados
def load_data():
    df = pd.read_csv("data.csv")  # Substituir pelo dataset correto
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    df['dia_da_semana'] = df['data_hora'].dt.dayofweek
    df['hora'] = df['data_hora'].dt.hour
    return df

def train_arima(df, forecast_days=7):
    df = df.set_index('data_hora').resample('D').sum()
    df = df[['total']]
    
    model = ARIMA(df['total'], order=(5,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=forecast_days)
    
    plt.figure(figsize=(10,5))
    plt.plot(df.index, df['total'], label="Dados Reais")
    plt.plot(pd.date_range(df.index[-1], periods=forecast_days+1, freq='D')[1:], forecast, label="Previsão", linestyle='dashed')
    plt.xlabel("Data")
    plt.ylabel("Engajamento")
    plt.title("Previsão de Engajamento com ARIMA")
    plt.legend()
    st.pyplot(plt)
    return forecast

def train_random_forest(df):
    X = df[['char_count', 'hora_postagem', 'dia_postagem']]
    y = df['total']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    st.write(f"Erro médio absoluto do modelo: {mae:.2f}")
    return model

def heatmap_engajamento(df):
    heatmap_data = df.pivot_table(values='total', index='hora', columns='dia_da_semana', aggfunc=np.mean)
    plt.figure(figsize=(10,6))
    sns.heatmap(heatmap_data, cmap='coolwarm', annot=True, fmt='.0f')
    plt.xlabel("Dia da Semana (0=Segunda, 6=Domingo)")
    plt.ylabel("Hora do Dia")
    plt.title("Engajamento Médio por Hora e Dia da Semana")
    st.pyplot(plt)

def predict_engagement(model, caracteres, hora, dia_da_semana):
    input_data = np.array([[caracteres, hora, dia_da_semana]])
    pred = model.predict(input_data)
    return pred[0]