import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from collections import defaultdict
from nltk.sentiment import SentimentIntensityAnalyzer
from streamlit_folium import folium_static

# Definindo as coordenadas dos estados dos EUA
STATE_COORDINATES = {
    "Alabama": [32.806671, -86.791130], "Alaska": [61.370716, -152.404419], "Arizona": [33.729759, -111.431221],
    "Arkansas": [34.746481, -92.289595], "California": [36.778259, -119.417931], "Colorado": [39.550051, -105.782067],
    "Connecticut": [41.603221, -73.087749], "Delaware": [38.910832, -75.527670], "Florida": [27.994402, -81.760254],
    "Georgia": [32.165622, -82.900075], "Hawaii": [19.741755, -155.844437], "Idaho": [44.068202, -114.742041],
    "Illinois": [40.633125, -89.398528], "Indiana": [40.267194, -86.134902], "Iowa": [41.878003, -93.097702],
    "Kansas": [39.011902, -98.484246], "Kentucky": [37.839333, -84.270018], "Louisiana": [30.984298, -91.962333],
    "Maine": [45.253783, -69.445469], "Maryland": [39.045755, -76.641271], "Massachusetts": [42.407211, -71.382437],
    "Michigan": [44.314844, -85.602364], "Minnesota": [46.729553, -94.685900], "Mississippi": [32.354668, -89.398528],
    "Missouri": [37.964253, -91.831833], "Montana": [46.879682, -110.362566], "Nebraska": [41.492537, -99.901813],
    "Nevada": [38.802610, -116.419389], "New Hampshire": [43.193852, -71.572395], "New Jersey": [40.058324, -74.405661],
    "New Mexico": [34.972730, -105.032363], "New York": [43.299428, -74.217933], "North Carolina": [35.759573, -79.019300],
    "North Dakota": [47.551493, -101.002012], "Ohio": [40.417287, -82.907123], "Oklahoma": [35.467560, -97.516428],
    "Oregon": [43.804133, -120.554201], "Pennsylvania": [41.203322, -77.194525], "Rhode Island": [41.580095, -71.477429],
    "South Carolina": [33.836081, -81.163725], "South Dakota": [43.969515, -99.901813], "Tennessee": [35.517491, -86.580447],
    "Texas": [31.968599, -99.901810], "Utah": [39.320980, -111.093731], "Vermont": [44.558803, -72.577841],
    "Virginia": [37.431573, -78.656894], "Washington": [47.751074, -120.740139], "West Virginia": [38.597626, -80.454903],
    "Wisconsin": [43.784440, -88.787868], "Wyoming": [43.075968, -107.290283]
}

# Função de análise de sentimento por estado
def analyze_sentiment_by_state(df):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = defaultdict(list)

    # Verifica o sentimento em textos e associa aos estados
    for _, row in df.iterrows():
        text = row.get('texto_limpo', '')
        if pd.notna(text):
            sentiment = analyzer.polarity_scores(text)['compound']
            for state in STATE_COORDINATES.keys():
                if state.lower() in text.lower():
                    sentiment_scores[state].append(sentiment)

    # Calcula os sentimentos médios por estado
    avg_sentiments = {state: sum(scores) / len(scores) for state, scores in sentiment_scores.items() if scores}
    
    return avg_sentiments

# Função para exibir o mapa com os sentimentos
def create_sentiment_map(df):
    st.title("Mapa de Sentimentos por Estado dos EUA")
    
    # Analisando os sentimentos
    state_sentiments = analyze_sentiment_by_state(df)
    
    # Criando o mapa
    map_center = [37.0902, -95.7129]  # Latitude e longitude dos EUA
    sentiment_map = folium.Map(location=map_center, zoom_start=4)
    
    # Adiciona marcadores de acordo com o sentimento por estado
    for state, sentiment in state_sentiments.items():
        lat, lon = STATE_COORDINATES.get(state, [0, 0])
        
        # Define a cor do marcador com base no sentimento
        color = 'green' if sentiment > 0 else 'red' if sentiment < 0 else 'gray'
        
        # Cria o marcador
        folium.CircleMarker(
            location=[lat, lon],
            radius=10,
            color=color,
            fill=True,
            fill_opacity=0.6,
            popup=f"{state}: {sentiment:.2f}",
        ).add_to(sentiment_map)
    
    # Exibe o mapa no Streamlit
    folium_static(sentiment_map)