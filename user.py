import streamlit as st
import pandas as pd
from blueskyApi import collectPosts
from graph_utils import distribution_values, analyze_correlation, generate_wordcloud
from mining import analyzeSentiment, topicModeling
from arima_model import train_arima

def get_top_tokens(df):
    token_engagement = {}
    for _, row in df.iterrows():
        for token in row['tokens']:
            if token not in token_engagement:
                token_engagement[token] = 0
            token_engagement[token] += row['total']
    return pd.DataFrame(list(token_engagement.items()), columns=['Token', 'Engajamento']).sort_values(by='Engajamento', ascending=False).head(10)

def identify_patterns(top_posts):
    st.write("### Identificação de Padrões nos Posts de Maior Engajamento")
    
    # Analisando palavras mais frequentes
    st.write("#### Palavras Mais Frequentes")
    generate_wordcloud(top_posts['tokens'])
    
    # Analisando sentimentos
    st.write("#### Análise de Sentimentos")
    sentiment_data = analyzeSentiment(top_posts)
    st.dataframe(sentiment_data[['texto_original', 'neg', 'neu', 'pos', 'compound']])
    
    # Analisando modelagem de tópicos
    st.write("#### Modelagem de Tópicos")
    topics = topicModeling(top_posts, num_topics=3, passes=5)
    for topic in topics:
        st.write(f"Tópico {topic[0]}: {topic[1]}")
    
    # Analisando horário de postagem
    st.write("#### Horário de Postagem")
    top_posts['data_hora'] = pd.to_datetime(top_posts['data_hora'])
    post_hours = top_posts['data_hora'].dt.hour.value_counts().sort_index()
    st.line_chart(post_hours)

def usersPage():
    st.title("Analisar Posts de um Usuário")

    actor = st.text_input("Digite o @ do usuário:", value="cruzeiro.com.br", key="actor_input")
    limit = st.number_input("Quantidade de posts por iteração:", min_value=1, max_value=100, value=10, key="limit_input")
    iterations = st.number_input("Número de iterações:", min_value=1, max_value=100, value=3, key="iterations_input")
    forecast_days = st.radio("Quantidade de dias para previsão de engajamento:", (3,7,30), key="days_radio")
    
    language = st.radio("Escolha o idioma:", ('Português', 'Inglês'), key="language_radio")
    language_code = 'portuguese' if language == 'Português' else 'english'
    
    if st.button("Analisar", key="analyze_button"):
        if actor:
            st.write("Coletando dados...")
            posts = collectPosts(actor, limit, iterations, language_code)

            if posts:
                st.write(f"Total de posts coletados: {len(posts)}")
                df = pd.DataFrame(posts)
                
                st.write("### Baixar Dados como CSV")
                csv = df.to_csv(index=False)
                st.download_button(label="Baixar CSV", data=csv, file_name="dados_posts.csv", mime="text/csv")
                
                st.write("### WordCloud das Palavras Mais Frequentes")
                generate_wordcloud(df['tokens'])
                
                st.write("### Evolução Temporal de Engajamento")
                df['data_hora'] = pd.to_datetime(df['data_hora'])
                temporal_data = df.groupby(df['data_hora'].dt.date)['total'].sum()
                st.line_chart(temporal_data)
                
                st.write("### Previsão de Engajamento para os Próximos Dias")
                train_arima(df, forecast_days)
                
                st.write("### Distribuição dos Valores")
                distribution_values(df)
                
                st.write("### Correlação Entre os Atributos")
                analyze_correlation(df)
                
                st.write("### Tokens com Mais Engajamento")
                top_tokens = get_top_tokens(df)
                st.dataframe(top_tokens)
                
                st.write("### Posts com Mais Engajamento")
                top_posts = df.sort_values(by='total', ascending=False).head(5)
                
                for _, row in top_posts.iterrows():
                    st.write(f"**{row['author_displayName']}** (@{row['author_handle']}) - **Engajamento:** {row['total']}")
                    st.write(f"**Texto Original:** {row['texto_original']}")
                    
                    embed = row.get("record", {}).get("embed", {}) if isinstance(row.get("record"), dict) else {}
                    if embed.get("$type") == "app.bsky.embed.images#view":
                        for image in embed.get("images", []):
                            image_url = image.get("fullsize", "")
                            if image_url:
                                st.image(image_url, caption="Imagem do Post", use_column_width=True)
                
                identify_patterns(top_posts)
            else:
                st.error("Nenhum dado encontrado para o usuário informado.")
        else:
            st.error("Por favor, insira o @ do usuário.")
