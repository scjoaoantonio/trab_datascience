# ---------------------------------------------------
# 📦 Importações de Bibliotecas e Módulos do Projeto
# ---------------------------------------------------
import streamlit as st
import pandas as pd
from api.blueskyApi import search_posts, cleanText  # Funções da API personalizada para busca e limpeza de texto
from utils.graph_utils import distribution_values, analyze_correlation, generate_wordcloud  # Utilitários de visualização
from utils.mining import analyzeSentiment, topicModeling  # Funções de mineração de texto

# ---------------------------------------------------
# 🔝 Função Auxiliar: Tokens com Maior Engajamento
# ---------------------------------------------------
def get_top_tokens(df):
    token_engagement = {}
    for _, row in df.iterrows():
        for token in row['tokens']:
            if token not in token_engagement:
                token_engagement[token] = 0
            token_engagement[token] += row['total']  # Soma o engajamento total por token

    # Retorna os 10 tokens mais engajados como DataFrame
    return pd.DataFrame(
        list(token_engagement.items()), 
        columns=['Token', 'Engajamento']
    ).sort_values(by='Engajamento', ascending=False).head(10)

# ---------------------------------------------------
# 🔍 Função para Buscar e Processar Posts de um Tema
# ---------------------------------------------------
def buscar_e_processar_posts(tema, limit, language_code):
    all_posts = []
    
    result = search_posts(tema, limit)
    if result:
        posts = result.get('posts', [])
        
        for post in posts:
            # Coleta de métricas de engajamento
            replyCount = post.get('replyCount', 0)
            repostCount = post.get('repostCount', 0)
            likeCount = post.get('likeCount', 0)
            quoteCount = post.get('quoteCount', 0)
            total = replyCount + repostCount + likeCount + quoteCount

            # Coleta de metadados e texto
            record = post.get('record', {})
            text = record.get('text', '')
            author = post.get('author', {})
            timestamp = post.get('indexedAt', '')

            # Limpeza e tokenização do texto
            tokens = cleanText(text, language_code)
            clean_text = ' '.join(tokens)

            post_data = {
                'texto_original': text,
                'texto_limpo': clean_text,
                'tokens': tokens,
                'comentarios': replyCount,
                'likes': likeCount,
                'compartilhamentos': repostCount,
                'repostagens': quoteCount,
                'total': total,
                'data_hora': timestamp,
                'author_handle': author.get('handle', ''),
                'author_displayName': author.get('displayName', '')
            }
            all_posts.append(post_data)
    
    return pd.DataFrame(all_posts)

# ---------------------------------------------------
# 📊 Página de Análise por Tema (Interface Streamlit)
# ---------------------------------------------------
def topicPage():
    st.title("Analisar Posts Sobre um Tema")

    # 🌐 Escolha do idioma (para limpeza de texto)
    language = st.radio("Escolha o idioma:", ('Português', 'Inglês'), key="topic_lang")
    language_code = 'portuguese' if language == 'Português' else 'english'

    # 🎯 Entrada de tema e número de posts
    tema = st.text_input("Digite o tema para buscar os posts:", "Cruzeiro")
    limit = st.number_input("Número máximo de posts:", min_value=1, value=15, step=5)

    # ▶️ Botão de execução da análise
    if st.button("Analisar Tema"):
        if tema:
            st.write("Coletando dados...")
            df = buscar_e_processar_posts(tema, limit, language_code)

            if not df.empty:
                st.write(f"Total de posts coletados: {len(df)}")

                # 💾 Botão para baixar os dados como CSV
                csv = df.to_csv(index=False)
                st.download_button(label="Baixar CSV", data=csv, file_name="dados_tema.csv", mime="text/csv")

                # ☁️ WordCloud
                st.write("### WordCloud das Palavras Mais Frequentes")
                generate_wordcloud(df['tokens'])

                # 🕒 Evolução temporal do engajamento
                st.write("### Evolução Temporal de Engajamento")
                df['data_hora'] = pd.to_datetime(df['data_hora'])  # Conversão para datetime
                temporal_data = df.groupby(df['data_hora'].dt.date)['total'].sum()
                st.line_chart(temporal_data)

                # 📊 Distribuição dos valores (likes, comentários etc.)
                st.write("### Distribuição dos Valores")
                distribution_values(df)

                # 🔥 Análise de correlação entre as métricas
                st.write("### Correlação Entre as Métricas")
                analyze_correlation(df[['comentarios', 'likes', 'compartilhamentos', 'repostagens', 'total']])

                # 🔝 Tokens com maior engajamento
                st.write("### Tokens com Mais Engajamento")
                top_tokens = get_top_tokens(df)
                st.dataframe(top_tokens)

                # 💬 Análise de sentimentos (negativo, neutro, positivo)
                st.write("### Análise de Sentimentos")
                df_sentimento = analyzeSentiment(df)
                st.bar_chart(df_sentimento[['neg', 'neu', 'pos']].mean())

                # 🧠 Modelagem de Tópicos com LDA
                st.write("### Modelagem de Tópicos")
                topics = topicModeling(df, num_topics=3, passes=10)
                for topic in topics:
                    st.write(f"Tópico {topic[0]+1}: {topic[1]}")

            else:
                st.error("Nenhum post encontrado para este tema.")
        else:
            st.error("Por favor, insira um tema para busca.")
