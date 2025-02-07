import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Imports de funções customizadas
import mining as mining
import graph_utils as graph


# ----------------------------
# Funções de Pré-processamento e Visualização
# ----------------------------

def get_top_tokens(df, top_n=10):

    """
    Retorna um DataFrame com os tokens que acumularam maior engajamento.
    """
    token_engagement = {}
    for _, row in df.iterrows():
        for token in row['tokens']:
            token_engagement[token] = token_engagement.get(token, 0) + row['total']
    return pd.DataFrame(list(token_engagement.items()), columns=['Token', 'Engajamento']) \
             .sort_values(by='Engajamento', ascending=False).head(top_n)


# ----------------------------
# Análise de Características dos Posts
# ----------------------------

def analyze_post_features(df):

    """
    Analisa características dos posts que possam estar associadas a engajamento alto ou baixo.
    """
    
    st.write("## Análise de Características dos Posts Relacionadas ao Engajamento")
    
    # 1. Quantidade de caracteres
    df['num_caracteres'] = df['texto_original'].apply(len)
    st.write("### Relação entre Quantidade de Caracteres e Engajamento")
    fig, ax = plt.subplots()
    sns.scatterplot(x='num_caracteres', y='total', data=df, ax=ax)
    ax.set_title("Engajamento vs. Número de Caracteres")
    st.pyplot(fig)
    
    # Exibe correlação entre número de caracteres e engajamento
    corr_chars = df[['num_caracteres', 'total']].corr().iloc[0, 1]
    # st.write(f"Correlação entre número de caracteres e engajamento: {corr_chars:.2f}")
    
    # 2. Horário de Postagem
    df['hora'] = pd.to_datetime(df['data_hora']).dt.hour
    st.write("### Engajamento Médio por Hora de Postagem")
    eng_por_hora = df.groupby('hora')['total'].mean().reset_index()
    fig2, ax2 = plt.subplots()
    sns.lineplot(x='hora', y='total', data=eng_por_hora, marker='o', ax=ax2)
    ax2.set_title("Engajamento Médio por Hora")
    ax2.set_xlabel("Hora do Dia")
    ax2.set_ylabel("Engajamento Médio")
    st.pyplot(fig2)
    
    # 3. Tokens com Maior Engajamento
    st.write("### Tokens com Maior Acúmulo de Engajamento")
    top_tokens = get_top_tokens(df)
    st.dataframe(top_tokens)

# ----------------------------
# Identificação de Padrões nos Posts de Maior Engajamento
# ----------------------------

def identify_patterns(top_posts):
    """
    Realiza análise de padrões dos posts de maior engajamento:
      - Geração de wordcloud com os tokens mais frequentes.
      - Análise de sentimentos.
      - Modelagem de tópicos.
      - Visualização do horário de postagem.
    """
    st.write("### Identificação de Padrões nos Posts de Maior Engajamento")
    
    # Palavras mais frequentes
    st.write("#### Palavras Mais Frequentes")
    graph.generate_wordcloud(top_posts['tokens'])
    
    # Análise de Sentimentos
    st.write("#### Análise de Sentimentos")
    sentiment_data = mining.analyzeSentiment(top_posts)
    st.dataframe(sentiment_data[['texto_original', 'neg', 'neu', 'pos', 'compound']])
    
    # # Modelagem de Tópicos
    # st.write("#### Modelagem de Tópicos")
    # topics = topicModeling(top_posts, num_topics=3, passes=5)
    # for topic in topics:
    #     st.write(f"Tópico {topic[0]}: {topic[1]}")
    
    # Horário de Postagem
    st.write("#### Horário de Postagem")
    top_posts['data_hora'] = pd.to_datetime(top_posts['data_hora'])
    post_hours = top_posts['data_hora'].dt.hour.value_counts().sort_index()
    st.line_chart(post_hours)