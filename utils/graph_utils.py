# ---------------------------------------------------
# 📦 Importações de Bibliotecas
# ---------------------------------------------------
import seaborn as sns                  # Visualizações estatísticas
import matplotlib.pyplot as plt        # Geração de gráficos
from wordcloud import WordCloud        # Criação de nuvem de palavras
import streamlit as st                 # Interface web interativa

# ---------------------------------------------------
# ☁️ Geração de WordCloud a partir de tokens
# ---------------------------------------------------
def generate_wordcloud(tokens_list):
    """
    Gera e exibe uma WordCloud com base em uma lista de listas de tokens.
    """
    # 🔤 Junta todos os tokens em uma única string
    all_tokens = ' '.join([' '.join(tokens) for tokens in tokens_list])

    # ☁️ Cria a WordCloud com estilo personalizado
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='viridis'
    ).generate(all_tokens)

    # 🎨 Exibe a imagem no Streamlit
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title("WordCloud das Palavras Mais Frequentes", fontsize=16)
    st.pyplot(fig)

# ---------------------------------------------------
# 📊 Distribuição das Métricas de Engajamento
# ---------------------------------------------------
def distribution_values(df):
    """
    Exibe histogramas das colunas numéricas relacionadas ao engajamento.
    """
    # 📈 Colunas numéricas para plotar
    numeric_columns = ['comentarios', 'likes', 'compartilhamentos', 'repostagens']
    sns.set(style="whitegrid")  # Estilo visual dos gráficos

    # 🔁 Para cada coluna, gera um histograma com linha de densidade (KDE)
    for column in numeric_columns:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.histplot(df[column], bins=20, kde=True, ax=ax)
        ax.set_title(f'Histograma de {column}')
        ax.set_xlabel(column)
        ax.set_ylabel('Frequência')
        st.pyplot(fig)

# ---------------------------------------------------
# 🔥 Análise de Correlação entre Métricas
# ---------------------------------------------------
def analyze_correlation(df):
    """
    Calcula e exibe a matriz de correlação entre as métricas de engajamento.
    """
    # 🔢 Seleção das colunas numéricas relevantes
    numeric_columns = ['comentarios', 'likes', 'compartilhamentos', 'repostagens', 'total']

    # 🧮 Cálculo da matriz de correlação
    matriz_correlacao = df[numeric_columns].corr()

    # 📌 Exibição do mapa de calor no Streamlit
    st.write("### Matriz de Correlação")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        matriz_correlacao,
        annot=True,
        fmt=".2f",
        cmap='coolwarm',
        cbar=True,
        square=True,
        linewidths=0.5,
        linecolor='black',
        ax=ax
    )
    ax.set_title('Mapa de Calor da Correlação Entre Atributos')
    st.pyplot(fig)
