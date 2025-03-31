# ---------------------------------------------------
# 📦 Importações de Bibliotecas
# ---------------------------------------------------
import pandas as pd
import streamlit as st
from statsmodels.tsa.arima.model import ARIMA  # Modelo ARIMA para séries temporais
import numpy as np
import wordcloud as WordCloud
import matplotlib as plt      

# ---------------------------------------------------
# 📈 Previsão com ARIMA: Engajamento Futuro
# ---------------------------------------------------
def train_arima(df, forecast_days):
    """
    Realiza a previsão do engajamento dos posts para os próximos dias utilizando ARIMA.
    """

    # 🕒 Converte a coluna 'data_hora' para datetime e ordena os dados por data
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    df = df.sort_values('data_hora')

    # 📊 Agrega os dados de engajamento por dia
    df_daily = df.set_index('data_hora').resample('D')['total'].sum().fillna(0)

    # Visualiza a série temporal agregada
    st.write("### Série Temporal Diária de Engajamento")
    st.line_chart(df_daily)

    # ⚙️ Define e treina o modelo ARIMA (padrão: (5,1,0))
    try:
        model = ARIMA(df_daily, order=(5, 1, 0))
        model_fit = model.fit()
    except Exception as e:
        st.error(f"Erro ao ajustar o modelo ARIMA: {e}")
        return

    # 🔮 Realiza a previsão para os próximos N dias
    forecast = model_fit.forecast(steps=forecast_days)

    # Exibe a previsão
    st.write("### Previsão para os Próximos Dias - ARIMA")
    st.line_chart(forecast)

    # (Opcional) Exibe os valores previstos em formato de tabela
    # st.dataframe(forecast.reset_index().rename(columns={'index': 'Data', 0: 'Engajamento Previsto'}))


# ---------------------------------------------------
# 🤖 Previsão de Engajamento com Características de Post
# ---------------------------------------------------
def predict_engagement(model, caracteres, hora, dia_da_semana):
    """
    Faz uma previsão de engajamento com base em variáveis manuais: caracteres, hora e dia da semana.
    """
    input_data = np.array([[caracteres, hora, dia_da_semana]], dtype=np.float32)
    pred = model.predict(input_data)

    # Mostra a previsão em texto e gráfico
    st.write(f"Previsão de engajamento: {pred[0]}")

    if isinstance(pred, (list, np.ndarray)):
        st.line_chart(pred)
    else:
        st.line_chart([pred])


# ---------------------------------------------------
# 🧠 Análise do Melhor Post: Hora, Dia e Tamanho
# ---------------------------------------------------
def analyze_best_post(df):
    """
    Analisa e sugere o melhor tipo de post com base em características como:
    - horário de postagem
    - dia da semana
    - número de caracteres
    """

    # 🔍 Extração de variáveis úteis para análise
    df['num_caracteres'] = df['texto_original'].apply(len)
    df['hora'] = pd.to_datetime(df['data_hora']).dt.hour
    df['dia_semana'] = pd.to_datetime(df['data_hora']).dt.dayofweek

    # 🕒 Melhor hora com base na média de engajamento
    eng_por_hora = df.groupby('hora')['total'].mean().reset_index()
    melhor_hora = eng_por_hora.loc[eng_por_hora['total'].idxmax(), 'hora']

    # 📅 Melhor dia da semana
    eng_por_dia = df.groupby('dia_semana')['total'].mean().reset_index()
    melhor_dia_index = eng_por_dia.loc[eng_por_dia['total'].idxmax(), 'dia_semana']
    dias_da_semana = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
    melhor_dia = dias_da_semana[melhor_dia_index]

    # ✍️ Melhor comprimento de texto (em caracteres)
    melhor_tamanho = df.groupby('num_caracteres')['total'].mean().idxmax()

    # 💡 Sugestão de combinação ideal
    st.write("### Postagem Ideal Sugerida")
    st.write(f"Poste no dia {melhor_dia} às {melhor_hora}h com aproximadamente {melhor_tamanho} caracteres para obter maior engajamento.")

    # 🔁 Resumo textual
    st.write(f"Melhor horário para postar: {melhor_hora}h")
    st.write(f"Melhor dia da semana: {melhor_dia}")
    st.write(f"Número ideal de caracteres: {melhor_tamanho}")

    return melhor_hora, melhor_dia, melhor_tamanho
