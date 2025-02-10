import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import streamlit as st

"""
Gera e exibe uma wordcloud com base em uma lista de tokens.
"""
def generate_wordcloud(tokens_list):
    # Junta todos os tokens em uma única string
    all_tokens = ' '.join([' '.join(tokens) for tokens in tokens_list])
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(all_tokens)
    
    # Exibe a wordcloud
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title("WordCloud das Palavras Mais Frequentes", fontsize=16)
    st.pyplot(fig)

def distribution_values(df):
    """
    Exibe histogramas para as colunas numéricas de interesse.
    """
    numeric_columns = ['comentarios', 'likes', 'compartilhamentos', 'repostagens']
    sns.set(style="whitegrid")

    for column in numeric_columns:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.histplot(df[column], bins=20, kde=True, ax=ax)
        ax.set_title(f'Histograma de {column}')
        ax.set_xlabel(column)
        ax.set_ylabel('Frequência')
        st.pyplot(fig)

def analyze_correlation(df):
    """
    Calcula e exibe a matriz de correlação e seu respectivo mapa de calor.
    """
    numeric_columns = ['comentarios', 'likes', 'compartilhamentos', 'repostagens', 'total']
    matriz_correlacao = df[numeric_columns].corr()

    st.write("### Matriz de Correlação")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(matriz_correlacao, annot=True, fmt=".2f", cmap='coolwarm', cbar=True, square=True,
                linewidths=0.5, linecolor='black', ax=ax)
    ax.set_title('Mapa de Calor da Correlação Entre Atributos')
    st.pyplot(fig)


