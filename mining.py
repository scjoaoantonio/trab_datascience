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
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import defaultdict

# Baixar recursos necessários do NLTK
nltk.download('vader_lexicon')

# Configuração do Streamlit
st.title("Análise de Sentimentos e Modelagem de Tópicos")

def analyzeSentiment(df):
    sia = SentimentIntensityAnalyzer()

    # Preenchendo valores None para evitar erros na análise
    df['texto_limpo'] = df['texto_limpo'].fillna('')

    # Aplicando a análise de sentimentos
    sentiments = df['texto_limpo'].apply(lambda text: sia.polarity_scores(text) if isinstance(text, str) else {"neg": 0, "neu": 0, "pos": 0, "compound": 0})
    
    # Convertendo a lista de dicionários para DataFrame
    sentiment_df = pd.DataFrame(sentiments.tolist())

    # Resetando o índice antes de concatenar
    df = df.reset_index(drop=True)
    sentiment_df = sentiment_df.reset_index(drop=True)

    # Concatenando os resultados ao DataFrame original
    df = pd.concat([df, sentiment_df], axis=1)

    # Removendo possíveis linhas vazias
    df = df.dropna(subset=['texto_limpo'])

    # Plotando a distribuição dos sentimentos
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df['compound'], bins=20, kde=True, color='blue', ax=ax)
    ax.set_title("Distribuição dos Sentimentos (VADER)", fontsize=14)
    ax.set_xlabel("Score de Sentimento (Compound)")
    ax.set_ylabel("Frequência")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    # Exibindo os posts mais positivos e negativos
    top_positive = df.nlargest(3, 'compound')
    top_negative = df.nsmallest(3, 'compound')

    st.write("### Posts mais positivos")
    for _, row in top_positive.iterrows():
        st.write(f"- {row['texto_limpo']} (Score: {row['compound']})")

    st.write("### Posts mais negativos")
    for _, row in top_negative.iterrows():
        st.write(f"- {row['texto_limpo']} (Score: {row['compound']})")

    return df


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
    
    # lda_vis = gensimvis.prepare(lda_model, corpus, dictionary)
    # html_string = pyLDAvis.prepared_data_to_html(lda_vis)
    # st.components.v1.html(html_string, height=800, scrolling=True)
    
    # Criar WordCloud para cada tópico
    fig, axes = plt.subplots(1, num_topics, figsize=(20, 5))
    for i, topic in enumerate(topics):
        words = dict(lda_model.show_topic(i, 30))
        wordcloud = WordCloud(width=300, height=300, background_color='white').generate_from_frequencies(words)
        axes[i].imshow(wordcloud, interpolation="bilinear")
        axes[i].axis("off")
        axes[i].set_title(f"Tópico {i}")
    
    st.pyplot(fig)
    
    return lda_model

# # Upload do arquivo CSV
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

def analyze_engagement_and_sentiment(df):
    # Listas de estados dos EUA e países do mundo
    estados_eua = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
    paises_mundo = ["United States", "Canada", "Mexico", "Brazil", "United Kingdom", "France", "Germany", "Italy", "Spain", "Russia", "China", "Japan", "India", "Australia", "South Africa", "Argentina", "Chile", "Colombia", "Peru", "Venezuela", "Saudi Arabia", "South Korea", "Turkey", "Egypt", "Nigeria", "Pakistan", "Bangladesh", "Indonesia", "Philippines", "Vietnam"]

    # Instanciando o analisador de sentimentos
    analyzer = SentimentIntensityAnalyzer()

    # Função para analisar sentimentos por país
    def sentiment_by_country(df):
        sentiment_dict = defaultdict(list)
        coluna_texto = "texto_original" if "texto_original" in df.columns else "texto_limpo"
        
        for text in df[coluna_texto].dropna():
            countries_mentioned = [country for country in paises_mundo if country in text]
            if countries_mentioned:
                sentiment_score = analyzer.polarity_scores(text)["compound"]
                for country in countries_mentioned:
                    sentiment_dict[country].append(sentiment_score)

        country_sentiments = {country: sum(sentiments) / len(sentiments) for country, sentiments in sentiment_dict.items()}
        return country_sentiments

    # Função para analisar sentimentos por estado
    def sentiment_by_state(df):
        sentiment_dict = defaultdict(list)
        coluna_texto = "texto_original" if "texto_original" in df.columns else "texto_limpo"
        
        for text in df[coluna_texto].dropna():
            states_mentioned = [state for state in estados_eua if state in text]
            if states_mentioned:
                sentiment_score = analyzer.polarity_scores(text)["compound"]
                for state in states_mentioned:
                    sentiment_dict[state].append(sentiment_score)

        state_sentiments = {state: sum(sentiments) / len(sentiments) for state, sentiments in sentiment_dict.items()}
        return state_sentiments

    # Análise de sentimentos por país
    country_sentiments = sentiment_by_country(df)

    # Identificar países com sentimento mais positivo e negativo
    most_positive_country = max(country_sentiments, key=country_sentiments.get)
    most_negative_country = min(country_sentiments, key=country_sentiments.get)

    # Análise de sentimentos por estado
    state_sentiments = sentiment_by_state(df)

    # Identificar estados com sentimento mais positivo e negativo
    most_positive_state = max(state_sentiments, key=state_sentiments.get)
    most_negative_state = min(state_sentiments, key=state_sentiments.get)

    # Retornar os resultados
    return {
        "País Mais Positivo": (most_positive_country, country_sentiments[most_positive_country]),
        "País Mais Negativo": (most_negative_country, country_sentiments[most_negative_country]),
        "Estado Mais Positivo": (most_positive_state, state_sentiments[most_positive_state]),
        "Estado Mais Negativo": (most_negative_state, state_sentiments[most_negative_state]),
    }

# Função Streamlit para exibir os resultados
def display_sentiment_by_state(df):
    # Obter os resultados da análise
    resultados = analyze_engagement_and_sentiment(df)

    # Exibir os resultados de forma amigável
    st.header("Resultados de Sentimento por País e Estado")

    st.subheader(f"País Mais Positivo: {resultados['País Mais Positivo'][0]} - {resultados['País Mais Positivo'][1]:.2f}")
    st.subheader(f"País Mais Negativo: {resultados['País Mais Negativo'][0]} - {resultados['País Mais Negativo'][1]:.2f}")
    st.subheader(f"Estado Mais Positivo: {resultados['Estado Mais Positivo'][0]} - {resultados['Estado Mais Positivo'][1]:.2f}")
    st.subheader(f"Estado Mais Negativo: {resultados['Estado Mais Negativo'][0]} - {resultados['Estado Mais Negativo'][1]:.2f}")
