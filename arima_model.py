import pandas as pd
import streamlit as st
from statsmodels.tsa.arima.model import ARIMA
import numpy as np

# ----------------------------
# Previsão com ARIMA
# ----------------------------

def train_arima(df, forecast_days):
    
    """
    Realiza a previsão do engajamento dos posts para os próximos dias utilizando ARIMA.
    """

    # Converte a coluna 'data_hora' para datetime e ordena os dados
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    df = df.sort_values('data_hora')
    
    # Agrega o engajamento diário (pode ser ajustado para outra granularidade)
    df_daily = df.set_index('data_hora').resample('D')['total'].sum().fillna(0)
    
    st.write("### Série Temporal Diária de Engajamento")
    st.line_chart(df_daily)
    
    # Define e treina o modelo ARIMA (a ordem pode ser ajustada conforme os dados)
    try:
        model = ARIMA(df_daily, order=(5, 1, 0))
        model_fit = model.fit()
    except Exception as e:
        st.error(f"Erro ao ajustar o modelo ARIMA: {e}")
        return
    
    # Realiza a previsão para os próximos 'forecast_days' dias
    forecast = model_fit.forecast(steps=forecast_days)
    st.write("### Previsão para os Próximos Dias - ARIMA")
    st.line_chart(forecast)
    # st.dataframe(forecast.reset_index().rename(columns={'index': 'Data', 0: 'Engajamento Previsto'}))


def predict_engagement(model, caracteres, hora, dia_da_semana):
    input_data = np.array([[caracteres, hora, dia_da_semana]], dtype=np.float32)
    pred = model.predict(input_data)
    st.write(f"Previsão de engajamento: {pred[0]}")

    # Verifica se a previsão é um array e exibe corretamente no gráfico
    if isinstance(pred, (list, np.ndarray)):
        st.line_chart(pred)
    else:
        st.line_chart([pred])  # Converte para lista caso seja um único valor
