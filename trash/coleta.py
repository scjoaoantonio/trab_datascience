import pandas as pd
import requests

def getUserFeed(actor, limit, cursor=None):
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

def collectPosts(actor, limit, iterations):
    all_posts = []
    cursor = None  # Inicializa o cursor como None

    for i in range(iterations):
        print(f"Coletando lote {i + 1} de posts...")
        result = getUserFeed(actor, limit=limit, cursor=cursor)
        posts = result.get('feed')
        cursor = result.get('cursor')  # Atualiza o cursor para a próxima iteração

        if posts:
            for post in posts:
                replyCount = post.get('post', {}).get('replyCount', 0)
                repostCount = post.get('post', {}).get('repostCount', 0)
                likeCount = post.get('post', {}).get('likeCount', 0)
                quoteCount = post.get('post', {}).get('quoteCount', 0)
                timestamp = post.get('post', {}).get('indexedAt')
                total = replyCount + repostCount + likeCount + quoteCount

                record = post.get('post', {}).get('record', {})
                text = record.get('text')
                if text:
                    tokens = cleanText(text)
                    clean = ' '.join(tokens)

                    postData = {
                        'texto_limpo': clean,
                        'tokens': tokens,
                        'comentarios': replyCount,
                        'likes': likeCount,
                        'compartilhamentos': repostCount,
                        'repostagens': quoteCount,
                        'total': total,
                        'data_hora': timestamp
                    }
                    all_posts.append(postData)
        else:
            print("Nenhum post encontrado ou limite da API atingido.")
            break

        if not cursor:  # Encerra o loop se não houver mais cursor
            print("Fim dos dados disponíveis.")
            break

    print(f"Total de posts coletados: {len(all_posts)}")
    return all_posts

def SaveCSV(postsData, fileName):
    df = pd.DataFrame(postsData)
    if not df.empty:
        df.to_csv(fileName, index=False, encoding='utf-8-sig')
        print(f"Dataset salvo com sucesso no arquivo '{fileName}'.")
    else:
        print("Nenhum dado disponível para salvar no CSV.")

if __name__ == "__main__":
    actor = "cruzeiro.com.br"
    limit = 100  # Número de posts por lote
    iterations = 100  # Número de lotes a serem coletados

    # Coletar os dados dos posts
    dados_posts = collectPosts(actor, limit, iterations)
    nome_arquivo = f"{actor}.csv"
    df = pd.DataFrame(dados_posts)

    if dados_posts:
        # Salvar os dados em um arquivo CSV
        SaveCSV(dados_posts, nome_arquivo)

    else:
        print("Nenhum dado foi coletado para salvar.")
        # Exibir informações sobre os dados coletados
        print(f"Coleta finalizada. Total de posts coletados: {len(dados_posts)}")
  