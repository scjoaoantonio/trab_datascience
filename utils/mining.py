import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pyLDAvis.gensim_models as gensimvis
from nltk.sentiment import SentimentIntensityAnalyzer
from gensim import corpora
from gensim.models import LdaModel
from gensim.models.coherencemodel import CoherenceModel
import nltk
from wordcloud import WordCloud
from collections import defaultdict
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# Baixar recursos necessários do NLTK
nltk.download('vader_lexicon')

# Configuração do Streamlit
st.title("Análise de Sentimentos e Modelagem de Tópicos")

# Função de análise de sentimentos
def analyzeSentiment(df):
    sia = SentimentIntensityAnalyzer()

    df['texto_limpo'] = df['texto_limpo'].fillna('')

    sentiments = df['texto_limpo'].apply(lambda text: sia.polarity_scores(text) if isinstance(text, str) else {"neg": 0, "neu": 0, "pos": 0, "compound": 0})
    
    sentiment_df = pd.DataFrame(sentiments.tolist())
    df = pd.concat([df.reset_index(drop=True), sentiment_df.reset_index(drop=True)], axis=1)
    df = df.dropna(subset=['texto_limpo'])

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df['compound'], bins=20, kde=True, color='blue', ax=ax)
    ax.set_title("Distribuição dos Sentimentos (VADER)", fontsize=14)
    ax.set_xlabel("Score de Sentimento (Compound)")
    ax.set_ylabel("Frequência")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    top_positive = df.nlargest(3, 'compound')
    top_negative = df.nsmallest(3, 'compound')

    st.write("### Posts mais positivos")
    for _, row in top_positive.iterrows():
        st.write(f"- {row['texto_limpo']} (Score: {row['compound']})")

    st.write("### Posts mais negativos")
    for _, row in top_negative.iterrows():
        st.write(f"- {row['texto_limpo']} (Score: {row['compound']})")

    return df

# Função para modelagem de tópicos
def topicModeling(df, num_topics=5, passes=10):
    if isinstance(df['tokens'].iloc[0], str):
        df['tokens'] = df['tokens'].apply(eval)
    
    texts = df['tokens'].tolist()
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=passes, random_state=42)
    
    topics = lda_model.print_topics(num_words=10)
    for topic in topics:
        st.write(f"**Tópico {topic[0]}:** {topic[1]}")
    
    coherence_model = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence='c_v')
    coherence_score = coherence_model.get_coherence()
    st.write(f"**Coerência do modelo:** {coherence_score:.4f}")
    
    fig, axes = plt.subplots(1, num_topics, figsize=(20, 5))
    for i, topic in enumerate(topics):
        words = dict(lda_model.show_topic(i, 30))
        wordcloud = WordCloud(width=300, height=300, background_color='white').generate_from_frequencies(words)
        axes[i].imshow(wordcloud, interpolation="bilinear")
        axes[i].axis("off")
        axes[i].set_title(f"Tópico {i}")
    
    st.pyplot(fig)
    
    return lda_model

# Função de análise de sentimento por estado
def analyze_engagement_and_sentiment(df):
    from nltk.sentiment import SentimentIntensityAnalyzer
    from collections import defaultdict

    estados_eua = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
    # paises_mundo = ["United States", "Canada", "Mexico", "Brazil", "United Kingdom", "France", "Germany", "Italy", "Spain", "Russia", "China", "Japan", "India", "Australia", "South Africa", "Argentina", "Chile", "Colombia", "Peru", "Venezuela", "Saudi Arabia", "South Korea", "Turkey", "Egypt", "Nigeria", "Pakistan", "Bangladesh", "Indonesia", "Philippines", "Vietnam"]

    analyzer = SentimentIntensityAnalyzer()
    
    def sentiment_by_region(df, region_list):
        sentiment_dict = defaultdict(list)
        coluna_texto = "texto_original" if "texto_original" in df.columns else "texto_limpo"
        
        for text in df[coluna_texto].dropna():
            regions_mentioned = [region for region in region_list if region.lower() in text.lower()]
            if regions_mentioned:
                sentiment_score = analyzer.polarity_scores(text)["compound"]
                for region in regions_mentioned:
                    sentiment_dict[region].append(sentiment_score)

        return {region: sum(scores) / len(scores) for region, scores in sentiment_dict.items() if scores}
    # country_sentiments = sentiment_by_region(df, paises_mundo)
    state_sentiments = sentiment_by_region(df, estados_eua)

    return state_sentiments

# Função para exibir o mapa
def display_sentiment_map(state_sentiments):
    # Cria um mapa centrado nos EUA
    map_center = [37.0902, -95.7129]  # Latitude e longitude dos EUA
    sentiment_map = folium.Map(location=map_center, zoom_start=4)
    
    # Adiciona os sentimentos de cada estado ao mapa
    for state, sentiment in state_sentiments.items():
        # Aqui, você pode personalizar a cor com base no sentimento
        color = 'green' if sentiment > 0 else 'red' if sentiment < 0 else 'gray'
        folium.CircleMarker(location=[20, -100],  # Coordenadas aproximadas; substitua com coordenadas reais
                            radius=10,
                            color=color,
                            fill=True,
                            fill_opacity=0.6,
                            popup=f"{state}: {sentiment:.2f}").add_to(sentiment_map)

    st.write("### Mapa Interativo de Sentimentos por Estado")
    folium_static(sentiment_map)

# Exemplo de carregamento do arquivo CSV
# df_file = st.file_uploader("Carregue um arquivo CSV contendo os posts", type=["csv"])

# if df_file:
#     df = pd.read_csv(df_file)
    
#     if 'texto_limpo' not in df.columns or 'tokens' not in df.columns:
#         st.error("O arquivo CSV deve conter as colunas 'texto_limpo' e 'tokens'.")
#     else:
#         st.subheader("Análise de Sentimentos")
#         df = analyzeSentiment(df)
        
#         st.subheader("Modelagem de Tópicos com LDA")
#         num_topics = st.slider("Número de Tópicos", 2, 10, 5)
#         passes = st.slider("Número de Passes", 5, 50, 10)
#         topicModeling(df, num_topics, passes)
