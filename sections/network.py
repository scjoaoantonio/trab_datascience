import blueskyApi
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import networkx as nx

# Baixar stopwords
nltk.download('stopwords')
nltk.download('punkt')

# Função para limpar texto
def cleanText(text, language):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    
    tokens = word_tokenize(text, language=language)
    
    # Definir as stop words com base no idioma
    if language == 'portuguese':
        stop_words = set(stopwords.words('portuguese'))
    else:  # Assume que o idioma é inglês
        stop_words = set(stopwords.words('english'))

    tokens_sem_stopwords = [word for word in tokens if word not in stop_words]
    return tokens_sem_stopwords

# Função para coletar posts
def collectPosts(actor, limit, iterations, language):
    all_posts = []
    cursor = None

    for i in range(iterations):
        st.write(f"Coletando lote {i + 1} de posts...")
        result = blueskyApi.getUserFeedPlus(actor, limit=limit, cursor=cursor)
        if not result:
            break

        posts = result.get('feed', [])
        cursor = result.get('cursor', None)

        for post in posts:
            replyCount = post.get('post', {}).get('replyCount', 0)
            repostCount = post.get('post', {}).get('repostCount', 0)
            likeCount = post.get('post', {}).get('likeCount', 0)
            quoteCount = post.get('post', {}).get('quoteCount', 0)
            timestamp = post.get('post', {}).get('indexedAt')
            total = replyCount + repostCount + likeCount + quoteCount

            record = post.get('post', {}).get('record', {})
            text = record.get('text')
            author = post.get('post', {}).get('author', {})
            embed = record.get('embed', {}).get('images', [])

            image_ref = embed[0].get('image', {}).get('ref', {}).get('$link') if embed else None

            if text:
                # Armazena o texto original
                original_text = text

                # Limpa o texto usando a função cleanText
                tokens = cleanText(text, language)
                clean = ' '.join(tokens)

                postData = {
                    'texto_original': original_text,  # Armazena o texto original
                    'texto_limpo': clean,  # Armazena o texto limpo
                    'tokens': tokens,
                    'comentarios': replyCount,
                    'likes': likeCount,
                    'compartilhamentos': repostCount,
                    'repostagens': quoteCount,
                    'total': total,
                    'data_hora': timestamp,
                    'author_handle': author.get('handle', ''),
                    'author_displayName': author.get('displayName', ''),
                    'image_ref': image_ref
                }
                all_posts.append(postData)

        if not cursor:
            st.write("Fim dos dados disponíveis.")
            break

    st.write(f"Total de posts coletados: {len(all_posts)}")
    return all_posts

# Função para visualizar a distribuição dos valores
def distribution_values(df):
    numeric_columns = ['comentarios', 'likes', 'compartilhamentos', 'repostagens']
    sns.set(style="whitegrid")

    for column in numeric_columns:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.histplot(df[column], bins=20, kde=True, ax=ax)
        ax.set_title(f'Histograma de {column}')
        ax.set_xlabel(column)
        ax.set_ylabel('Frequência')
        st.pyplot(fig)

# Função para analisar a correlação
def analyze_correlation(df):
    numeric_columns = ['comentarios', 'likes', 'compartilhamentos', 'repostagens', 'total']
    matriz_correlacao = df[numeric_columns].corr()

    st.write("Matriz de Correlação:")
    st.dataframe(matriz_correlacao)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(matriz_correlacao, annot=True, fmt=".2f", cmap='coolwarm', cbar=True, square=True,
                linewidths=0.5, linecolor='black', ax=ax)
    ax.set_title('Mapa de Calor da Correlação Entre Atributos')
    st.pyplot(fig)

# Função para gerar WordCloud
def generate_wordcloud(tokens_list):
    all_tokens = ' '.join([' '.join(tokens) for tokens in tokens_list])
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(all_tokens)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title("WordCloud das Palavras Mais Frequentes", fontsize=16)
    st.pyplot(fig)

# Função para remover duplicados
def remove_repetidos(vetor):
    return list(set(vetor))

# Função para coletar seguidores e seguidos
def coletar_seguidores_e_seguidos(autores):
    seguidores_por_autor = {}
    seguidos_por_autor = {}

    for autor in autores:
        seguidores_por_autor[autor] = blueskyApi.getUserFollowers(autor, 100)  # Directly assign the list of handles
        seguidos_por_autor[autor] = blueskyApi.getUserFollows(autor, 100)  # Directly assign the list of handles

    return seguidores_por_autor, seguidos_por_autor


# Função para construir a rede
def construir_rede(seguidores_por_autor, seguidos_por_autor):
    G = nx.DiGraph()

    for autor, seguidores in seguidores_por_autor.items():
        for seguidor in seguidores:
            G.add_edge(seguidor, autor)

    for autor, seguidos in seguidos_por_autor.items():
        for seguido in seguidos:
            G.add_edge(autor, seguido)

    return G

# Função para analisar a rede
def analisar_rede(G):
    # Centralidade de grau
    degree_centrality = nx.degree_centrality(G)

    # Detecção de comunidades
    communities = nx.algorithms.community.greedy_modularity_communities(G)

    return degree_centrality, communities

# Função para visualizar a rede
def visualizar_rede(G, degree_centrality, communities):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))

    # Desenhar os nós com cores baseadas nas comunidades
    for i, community in enumerate(communities):
        nx.draw_networkx_nodes(G, pos, nodelist=community, node_color=[i] * len(community), cmap=plt.cm.tab20, node_size=100)

    # Desenhar as arestas
    nx.draw_networkx_edges(G, pos, alpha=0.5)

    # Desenhar os rótulos dos nós
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.title("Rede de Seguidores")
    st.pyplot(plt)

def networkPage():
    # Interface do Streamlit
    st.title("Análise de Rede de Seguidores")
    st.markdown("""
    Esta aplicação coleta seguidores de perfis, constrói uma rede de relacionamentos e analisa centralidade e comunidades.
    """)

    # Inputs do usuário
    temas = st.text_input("Digite os temas separados por vírgula (ex: Cruzeiro, Gabigol):")
    temas = [tema.strip() for tema in temas.split(",")] if temas else ["Cruzeiro", "Gabigol"]
    limit = st.number_input("Número máximo de posts para buscar por tema:", min_value=1, value=5)

    if st.button("Analisar Rede"):
        st.write("Coletando dados...")

        textos_gerais = []
        autores_gerais = []

        for tema in temas:
            result = blueskyApi.search_posts(tema, limit)
            if result:
                st.write(f"Posts encontrados para o tema '{tema}':")
                textos = []
                usuarios = []

                for post in result.get("posts", []):
                    record = post.get("record")
                    author = post.get("author")

                    if record and author:  # Verifica se ambos os dados estão presentes
                        textos.append(record.get("text"))
                        usuarios.append(author.get("handle"))

                textos_gerais.extend(textos)
                autores_gerais.extend(usuarios)

        # Coletar informações de seguidores e seguidos
        st.write("Coletando seguidores e seguidos...")
        seguidores_por_autor, seguidos_por_autor = coletar_seguidores_e_seguidos(set(autores_gerais))

        # Construir a rede
        st.write("Construindo a rede...")
        G = construir_rede(seguidores_por_autor, seguidos_por_autor)

        # Analisar a rede
        st.write("Analisando a rede...")
        degree_centrality, communities = analisar_rede(G)

        # Visualizar a rede
        st.write("Visualizando a rede...")
        visualizar_rede(G, degree_centrality, communities)

        # Exibir métricas de centralidade
        st.subheader("Centralidade de Grau")
        st.write(pd.DataFrame.from_dict(degree_centrality, orient="index", columns=["Centralidade"]).sort_values(by="Centralidade", ascending=False))

        # Exibir comunidades
        st.subheader("Comunidades Detectadas")
        for i, community in enumerate(communities):
            st.write(f"Comunidade {i + 1}: {list(community)}")

        # Exportar os dados para arquivos CSV
        st.write("Exportando dados...")
        df_posts = pd.DataFrame({"Texto": textos_gerais, "Usuario": autores_gerais})
        df_posts.to_csv("posts.csv", index=False)

        data_seguidores = {"Usuario": [], "Seguidores": [], "Seguidos": []}
        for autor in seguidores_por_autor:
            data_seguidores["Usuario"].append(autor)
            data_seguidores["Seguidores"].append(", ".join(seguidores_por_autor[autor]))
            data_seguidores["Seguidos"].append(", ".join(seguidos_por_autor[autor]))

        df_relacoes = pd.DataFrame(data_seguidores)
        df_relacoes.to_csv("relacoes_seguidores.csv", index=False)

        st.success("Análise concluída!")
        st.markdown("""
        - **Posts** salvos em `posts.csv`
        - **Relações de seguidores/seguidos** salvas em `relacoes_seguidores.csv`
        """)