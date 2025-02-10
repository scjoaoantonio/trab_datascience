import requests
import pandas as pd
import streamlit as st
import spacy

# Carregar modelo para português e inglês
nlp_pt = spacy.load("pt_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")

def cleanText(text, language):
    # Escolher o modelo correto
    nlp = nlp_pt if language == "portuguese" else nlp_en
    
    # Processar o texto
    doc = nlp(text.lower())
    
    # Remover stopwords e pontuação
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return tokens


# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords

# # nltk.download('punkt')
# nltk.download('stopwords')
# nltk.data.path.append("./nltk_data")

# def cleanText(text, language):
#     text = text.lower()
#     text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
#     text = re.sub(r'[^\w\s]', '', text)
#     text = re.sub(r'\d+', '', text)
    
#     tokens = word_tokenize(text, language=language)
    
#     # Definir as stop words com base no idioma
#     if language == 'portuguese':
#         stop_words = set(stopwords.words('portuguese'))
#     else:  # Assume que o idioma é inglês
#         stop_words = set(stopwords.words('english'))

#     tokens_sem_stopwords = [word for word in tokens if word not in stop_words]
#     return tokens_sem_stopwords

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

def collectPosts(actor, limit, iterations,language):
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
            image_ref = True if image_ref else False

            if text:
                # Armazena o texto original
                original_text = text

                # Limpa o texto usando a função cleanText
                tokens = cleanText(text,language)
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
            print("Fim dos dados disponíveis.")
            break

    print(f"Total de posts coletados: {len(all_posts)}")
    return all_posts

# Streamlit: Exibir o texto original e o texto limpo
if st.button("Analisar"):
    actor = st.text_input("Digite o handle do ator:")
    limit = st.number_input("Limite de posts:", min_value=1, value=10)
    iterations = st.number_input("Número de iterações:", min_value=1, value=5)

    if actor:
        st.write("Coletando dados...")
        posts = collectPosts(actor, limit, iterations)

        if posts:
            st.write(f"Total de posts coletados: {len(posts)}")

            # Criar DataFrame
            df = pd.DataFrame(posts)

            # Posts com mais engajamento
            st.write("### Posts com Mais Engajamento")
            top_posts = df.sort_values(by='total', ascending=False).head(5)

            for _, row in top_posts.iterrows():
                st.write(f"**Usuário:** {row['author_handle']} - **Nome:** {row['author_displayName']}")

                # Exibir o texto original e o texto limpo
                st.write(f"**Texto Original:** {row['texto_original']}")
                st.write(f"**Texto Limpo:** {row['texto_limpo']}")

                # Verificar se há imagens associadas ao post
                image_ref = row['image_ref']
                if image_ref:
                    st.image(image_ref, caption="Imagem do Post", use_column_width=True)

                st.write(f"**Engajamento Total:** {row['total']}\n---")

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
  