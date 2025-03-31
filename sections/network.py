# ---------------------------------------------------
# 📦 Importações de Bibliotecas Necessárias
# ---------------------------------------------------
import api.blueskyApi as blueskyApi  # Módulo personalizado para chamadas à API do Bluesky
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

# ---------------------------------------------------
# ⬇️ Download dos Recursos do NLTK
# ---------------------------------------------------
nltk.download('stopwords')
nltk.download('punkt')

# ---------------------------------------------------
# 🧹 Função para Limpeza e Tokenização de Texto
# ---------------------------------------------------
def cleanText(text, language):
    text = text.lower()  # Converte tudo para minúsculas
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r'[^\w\s]', '', text)  # Remove pontuação
    text = re.sub(r'\d+', '', text)  # Remove números
    
    tokens = word_tokenize(text, language=language)  # Tokeniza o texto com base no idioma
    
    stop_words = set(stopwords.words(language if language == 'portuguese' else 'english'))  # Define as stopwords
    tokens_sem_stopwords = [word for word in tokens if word not in stop_words]  # Remove stopwords
    return tokens_sem_stopwords

# ---------------------------------------------------
# 📥 Coleta de Posts via API do Bluesky
# ---------------------------------------------------
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
            # Coleta estatísticas de engajamento
            replyCount = post.get('post', {}).get('replyCount', 0)
            repostCount = post.get('post', {}).get('repostCount', 0)
            likeCount = post.get('post', {}).get('likeCount', 0)
            quoteCount = post.get('post', {}).get('quoteCount', 0)
            timestamp = post.get('post', {}).get('indexedAt')
            total = replyCount + repostCount + likeCount + quoteCount

            # Extrai texto e metadados
            record = post.get('post', {}).get('record', {})
            text = record.get('text')
            author = post.get('post', {}).get('author', {})
            embed = record.get('embed', {}).get('images', [])
            image_ref = embed[0].get('image', {}).get('ref', {}).get('$link') if embed else None

            if text:
                original_text = text
                tokens = cleanText(text, language)
                clean = ' '.join(tokens)

                postData = {
                    'texto_original': original_text,
                    'texto_limpo': clean,
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

# ---------------------------------------------------
# 📊 Visualização de Distribuições
# ---------------------------------------------------
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

# ---------------------------------------------------
# 🔥 Análise de Correlação entre Métricas
# ---------------------------------------------------
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

# ---------------------------------------------------
# ☁️ Geração de WordCloud
# ---------------------------------------------------
def generate_wordcloud(tokens_list):
    all_tokens = ' '.join([' '.join(tokens) for tokens in tokens_list])
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(all_tokens)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title("WordCloud das Palavras Mais Frequentes", fontsize=16)
    st.pyplot(fig)

# ---------------------------------------------------
# 🔁 Função para Remover Duplicados
# ---------------------------------------------------
def remove_repetidos(vetor):
    return list(set(vetor))

# ---------------------------------------------------
# 📡 Coleta de Seguidores e Seguidos de Autores
# ---------------------------------------------------
def coletar_seguidores_e_seguidos(autores):
    seguidores_por_autor = {}
    seguidos_por_autor = {}

    for autor in autores:
        seguidores_por_autor[autor] = blueskyApi.getUserFollowers(autor, 100)
        seguidos_por_autor[autor] = blueskyApi.getUserFollows(autor, 100)

    return seguidores_por_autor, seguidos_por_autor

# ---------------------------------------------------
# 🌐 Construção do Grafo de Rede
# ---------------------------------------------------
def construir_rede(seguidores_por_autor, seguidos_por_autor):
    G = nx.DiGraph()  # Grafo direcionado

    for autor, seguidores in seguidores_por_autor.items():
        for seguidor in seguidores:
            G.add_edge(seguidor, autor)

    for autor, seguidos in seguidos_por_autor.items():
        for seguido in seguidos:
            G.add_edge(autor, seguido)

    return G

# ---------------------------------------------------
# 🧠 Análise da Rede: Centralidade e Comunidades
# ---------------------------------------------------
def analisar_rede(G):
    degree_centrality = nx.degree_centrality(G)
    communities = nx.algorithms.community.greedy_modularity_communities(G)
    return degree_centrality, communities

# ---------------------------------------------------
# 🧩 Visualização da Rede com NetworkX e Streamlit
# ---------------------------------------------------
def visualizar_rede(G, degree_centrality, communities):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))

    for i, community in enumerate(communities):
        nx.draw_networkx_nodes(G, pos, nodelist=community, node_color=[i] * len(community),
                               cmap=plt.cm.tab20, node_size=100)

    nx.draw_networkx_edges(G, pos, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.title("Rede de Seguidores")
    st.pyplot(plt)

# ---------------------------------------------------
# 🧭 Página Principal: Interface Streamlit para Análise de Rede
# ---------------------------------------------------
def networkPage():
    st.title("Análise de Rede de Seguidores")
    st.markdown("""
    Esta aplicação coleta seguidores de perfis, constrói uma rede de relacionamentos e analisa centralidade e comunidades.
    """)

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

                    if record and author:
                        textos.append(record.get("text"))
                        usuarios.append(author.get("handle"))

                textos_gerais.extend(textos)
                autores_gerais.extend(usuarios)

        st.write("Coletando seguidores e seguidos...")
        seguidores_por_autor, seguidos_por_autor = coletar_seguidores_e_seguidos(set(autores_gerais))

        st.write("Construindo a rede...")
        G = construir_rede(seguidores_por_autor, seguidos_por_autor)

        st.write("Analisando a rede...")
        degree_centrality, communities = analisar_rede(G)

        st.write("Visualizando a rede...")
        visualizar_rede(G, degree_centrality, communities)

        st.subheader("Centralidade de Grau")
        st.write(pd.DataFrame.from_dict(degree_centrality, orient="index", columns=["Centralidade"]).sort_values(by="Centralidade", ascending=False))

        st.subheader("Comunidades Detectadas")
        for i, community in enumerate(communities):
            st.write(f"Comunidade {i + 1}: {list(community)}")

        # Salvar os dados em arquivos CSV
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
