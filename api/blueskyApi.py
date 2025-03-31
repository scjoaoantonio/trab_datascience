# ---------------------------------------------------
# 📦 Importações de bibliotecas necessárias
# ---------------------------------------------------
import os
import re
import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import streamlit as st

# ---------------------------------------------------
# 🧠 Função para configurar o caminho local do NLTK
# ---------------------------------------------------
def nltkDownload():
    # Define o caminho local para salvar os dados do NLTK no diretório do script
    nltk_data_path = os.path.join(os.path.dirname(__file__), 'nltk_data')
    nltk.data.path.append(nltk_data_path)

# ---------------------------------------------------
# 🧹 Função para limpeza e tokenização de texto
# ---------------------------------------------------
def cleanText(text, language):
    # Converte o texto para minúsculas
    text = text.lower()

    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # Remove pontuação e números
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)

    # Mapeia siglas de idioma para formatos reconhecidos pelo NLTK
    language_map = {"pt": "portuguese", "en": "english"}
    language = language_map.get(language, language)

    # Tenta tokenizar o texto com o idioma especificado
    try:
        tokens = nltk.word_tokenize(text, language=language)
    except LookupError:
        print(f"Erro: Não foi possível encontrar os recursos de tokenização para '{language}'.")
        tokens = text.split()  # Fallback: separação simples por espaço

    # Remove stopwords (palavras comuns irrelevantes)
    stop_words = set(nltk.corpus.stopwords.words(language if language in nltk.corpus.stopwords.fileids() else 'english'))
    tokens_sem_stopwords = [word for word in tokens if word not in stop_words]
    return tokens_sem_stopwords

# ---------------------------------------------------
# 🌐 Coleta os posts de um usuário específico do Bluesky
# ---------------------------------------------------
def getUserFeedPlus(actor, limit, cursor=None):
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
    params = {"actor": actor, "limit": limit}
    if cursor:
        params["cursor"] = cursor

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None

# ---------------------------------------------------
# 🔍 Busca por posts com base em um termo de consulta
# ---------------------------------------------------
def search_posts(query, limit):
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    params = {"q": query, "limit": limit}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None

# ---------------------------------------------------
# 📥 Função principal para coletar, limpar e organizar posts
# ---------------------------------------------------
def collectPosts(actor, limit, iterations, language):
    all_posts = []
    cursor = None

    for i in range(iterations):
        print(f"Coletando lote {i + 1} de posts...")
        result = getUserFeedPlus(actor, limit=limit, cursor=cursor)
        if not result:
            break

        posts = result.get('feed', [])
        cursor = result.get('cursor', None)

        for post in posts:
            # Coleta dados de engajamento
            replyCount = post.get('post', {}).get('replyCount', 0)
            repostCount = post.get('post', {}).get('repostCount', 0)
            likeCount = post.get('post', {}).get('likeCount', 0)
            quoteCount = post.get('post', {}).get('quoteCount', 0)
            timestamp = post.get('post', {}).get('indexedAt')
            total = replyCount + repostCount + likeCount + quoteCount

            # Coleta texto e metadados
            record = post.get('post', {}).get('record', {})
            text = record.get('text')
            author = post.get('post', {}).get('author', {})
            embed = record.get('embed', {}).get('images', [])

            # Verifica se o post tem imagem
            image_ref = embed[0].get('image', {}).get('ref', {}).get('$link') if embed else None
            image_ref = True if image_ref else False

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
            print("Fim dos dados disponíveis.")
            break

    print(f"Total de posts coletados: {len(all_posts)}")
    return all_posts

# ---------------------------------------------------
# 🖥️ Interface interativa com Streamlit
# ---------------------------------------------------
if st.button("Analisar"):
    actor = st.text_input("Digite o handle do ator:")
    limit = st.number_input("Limite de posts:", min_value=1, value=10)
    iterations = st.number_input("Número de iterações:", min_value=1, value=5)

    if actor:
        st.write("Coletando dados...")
        posts = collectPosts(actor, limit, iterations)

        if posts:
            st.write(f"Total de posts coletados: {len(posts)}")

            # Exibe os posts com maior engajamento
            st.write("### Posts com Mais Engajamento")
            df = pd.DataFrame(posts)
            top_posts = df.sort_values(by='total', ascending=False).head(5)

            for _, row in top_posts.iterrows():
                st.write(f"**Usuário:** {row['author_handle']} - **Nome:** {row['author_displayName']}")
                st.write(f"**Texto Original:** {row['texto_original']}")
                st.write(f"**Texto Limpo:** {row['texto_limpo']}")

                if row['image_ref']:
                    st.image(row['image_ref'], caption="Imagem do Post", use_column_width=True)

                st.write(f"**Engajamento Total:** {row['total']}\n---")

# ---------------------------------------------------
# 👥 Funções para obter seguidores e seguidos de um usuário
# ---------------------------------------------------
def getUserFollows(actor, limit):
    url = "https://public.api.bsky.app/xrpc/app.bsky.graph.getFollows"
    params = {"actor": actor, "limit": limit}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None

def getUserFollowers(actor, limit):
    url = "https://public.api.bsky.app/xrpc/app.bsky.graph.getFollowers"
    params = {"actor": actor, "limit": limit}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None
