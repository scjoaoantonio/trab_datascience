# ---------------------------------------------------
# 📦 Importações de Bibliotecas Necessárias
# ---------------------------------------------------
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from nltk.sentiment import SentimentIntensityAnalyzer  # Analisador de sentimentos VADER (NLTK)
from gensim import corpora                            # Para criação de dicionário textual
from gensim.models import LdaModel                    # Modelo de tópicos LDA
from gensim.models.coherencemodel import CoherenceModel  # Avaliação de coerência dos tópicos
import nltk
from wordcloud import WordCloud
from collections import defaultdict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ---------------------------------------------------
# ⬇️ Download de Recursos do NLTK
# ---------------------------------------------------
nltk.download('vader_lexicon')  # Lexicon de sentimentos para o VADER

# ---------------------------------------------------
# 🚀 Configuração da Página Streamlit
# ---------------------------------------------------
st.title("Análise de Sentimentos e Modelagem de Tópicos")

# ---------------------------------------------------
# 💬 Função: Análise de Sentimentos com VADER
# ---------------------------------------------------
def analyzeSentiment(df):
    sia = SentimentIntensityAnalyzer()
    df['texto_limpo'] = df['texto_limpo'].fillna('')

    # Aplica o analisador VADER a cada linha do DataFrame
    sentiments = df['texto_limpo'].apply(
        lambda text: sia.polarity_scores(text) if isinstance(text, str)
        else {"neg": 0, "neu": 0, "pos": 0, "compound": 0}
    )

    # Combina os scores ao DataFrame original
    sentiment_df = pd.DataFrame(sentiments.tolist())
    df = pd.concat([df.reset_index(drop=True), sentiment_df.reset_index(drop=True)], axis=1)
    df = df.dropna(subset=['texto_limpo'])

    # 📊 Visualização da distribuição dos sentimentos
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df['compound'], bins=20, kde=True, color='blue', ax=ax)
    ax.set_title("Distribuição dos Sentimentos (VADER)", fontsize=14)
    ax.set_xlabel("Score de Sentimento (Compound)")
    ax.set_ylabel("Frequência")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    # 📈 Exibe os 3 posts mais positivos e negativos
    top_positive = df.nlargest(3, 'compound')
    top_negative = df.nsmallest(3, 'compound')

    st.write("### Posts mais positivos")
    for _, row in top_positive.iterrows():
        st.write(f"- {row['texto_limpo']} (Score: {row['compound']})")

    st.write("### Posts mais negativos")
    for _, row in top_negative.iterrows():
        st.write(f"- {row['texto_limpo']} (Score: {row['compound']})")

    return df

# ---------------------------------------------------
# 🧠 Função: Modelagem de Tópicos com LDA (Gensim)
# ---------------------------------------------------
def topicModeling(df, num_topics=5, passes=10):
    """
    Aplica LDA para modelar os tópicos principais nos textos.
    """
    # 🧹 Garante que os tokens estejam em formato de lista
    if isinstance(df['tokens'].iloc[0], str):
        df['tokens'] = df['tokens'].apply(eval)

    # Prepara textos, dicionário e corpus
    texts = df['tokens'].tolist()
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    # ⚙️ Treina o modelo LDA
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=passes, random_state=42)

    # 📋 Exibe os tópicos gerados
    topics = lda_model.print_topics(num_words=10)
    for topic in topics:
        st.write(f"**Tópico {topic[0]}:** {topic[1]}")

    # 📐 Avalia a coerência dos tópicos
    coherence_model = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence='c_v')
    coherence_score = coherence_model.get_coherence()
    st.write(f"**Coerência do modelo:** {coherence_score:.4f}")

    # ☁️ Gera WordCloud para cada tópico
    fig, axes = plt.subplots(1, num_topics, figsize=(20, 5))
    for i, topic in enumerate(topics):
        words = dict(lda_model.show_topic(i, 30))
        wordcloud = WordCloud(width=300, height=300, background_color='white').generate_from_frequencies(words)
        axes[i].imshow(wordcloud, interpolation="bilinear")
        axes[i].axis("off")
        axes[i].set_title(f"Tópico {i}")
    st.pyplot(fig)

    return lda_model

# ---------------------------------------------------
# 🗺️ Função: Análise de Sentimentos por Estado
# ---------------------------------------------------
def analyze_sentiment_by_state(df):
    """
    Analisa sentimentos de textos mencionando estados dos EUA e retorna os extremos (positivo e negativo).
    """
    analyzer = SentimentIntensityAnalyzer()

    # Lista completa de estados dos EUA
    estados_eua = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
        "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
        "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
        "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
        "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
        "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
        "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
    ]

    sentiment_dict = defaultdict(list)
    coluna_texto = "texto_original" if "texto_original" in df.columns else "texto_limpo"

    # 🔁 Percorre os textos e associa sentimentos aos estados mencionados
    for text in df[coluna_texto].dropna():
        states_mentioned = [state for state in estados_eua if state in text]
        if states_mentioned:
            sentiment_score = analyzer.polarity_scores(text)["compound"]
            for state in states_mentioned:
                sentiment_dict[state].append(sentiment_score)

    # 🧮 Calcula a média de sentimento por estado
    state_sentiments = {
        state: sum(scores) / len(scores) if scores else 0
        for state, scores in sentiment_dict.items()
    }

    # 🔍 Identifica os estados com maior e menor sentimento
    if state_sentiments:
        most_positive_state = max(state_sentiments, key=state_sentiments.get)
        most_negative_state = min(state_sentiments, key=state_sentiments.get)

        return {
            "estado_mais_positivo": most_positive_state,
            "sentimento_positivo": state_sentiments[most_positive_state],
            "estado_mais_negativo": most_negative_state,
            "sentimento_negativo": state_sentiments[most_negative_state]
        }
    else:
        return {"mensagem": "Nenhum estado encontrado com sentimentos analisados."}
