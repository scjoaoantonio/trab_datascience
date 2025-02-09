import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
from nltk.sentiment import SentimentIntensityAnalyzer
from gensim import corpora
from gensim.models import LdaModel
from gensim.models.coherencemodel import CoherenceModel
import nltk
from wordcloud import WordCloud

# Baixar recursos necessários do NLTK
nltk.download('vader_lexicon')

# Configuração do Streamlit
st.title("Análise de Sentimentos e Modelagem de Tópicos")

def analyzeSentiment(df):
    sia = SentimentIntensityAnalyzer()
    sentiments = df['texto_limpo'].apply(lambda text: sia.polarity_scores(text) if isinstance(text, str) else {"neg": 0, "neu": 0, "pos": 0, "compound": 0})
    sentiment_df = pd.DataFrame(list(sentiments))
    df = pd.concat([df, sentiment_df], axis=1)
    
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
