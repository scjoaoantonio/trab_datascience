# Arquivo: graph_utils.py

import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Função para visualizar a distribuição dos valores dos atributos numéricos
def distribution_values(df):
    numeric_columns = ['comentarios', 'likes', 'compartilhamentos', 'repostagens']
    sns.set(style="whitegrid")

    for column in numeric_columns:
        plt.figure(figsize=(12, 5))

        # Histograma
        plt.subplot(1, 2, 1)
        sns.histplot(df[column], bins=20, kde=True)
        plt.title(f'Histograma de {column}')
        plt.xlabel(column)
        plt.ylabel('Frequência')

        # Box-plot
        plt.subplot(1, 2, 2)
        sns.boxplot(x=df[column])
        plt.title(f'Box-plot de {column}')
        plt.xlabel(column)

        plt.tight_layout()
        plt.show()

# Função para analisar a correlação entre atributos numéricos
def analyze_correlation(df):
    numeric_columns = ['comentarios', 'likes', 'compartilhamentos', 'repostagens', 'total']
    correlation_matrix = df[numeric_columns].corr()

    plt.figure(figsize=(10, 8))
    sns.set(style="white")

    # Mapa de calor
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', cbar=True,
                square=True, linewidths=0.5, linecolor='black')    
    plt.title('Mapa de Calor da Correlação Entre Atributos')
    plt.show()

# Função para gerar uma nuvem de palavras a partir de uma lista de tokens
def generate_wordcloud(tokens_list):
    all_tokens = ' '.join([' '.join(tokens) for tokens in tokens_list])
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(all_tokens)

    # Exibir a nuvem de palavras
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title("WordCloud das Palavras Mais Frequentes", fontsize=16)
    plt.show()
