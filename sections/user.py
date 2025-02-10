import streamlit as st
import pandas as pd

# Imports de funções customizadas
import blueskyApi as bsky
import mining as mining
import utils.arima_model as arima
import utils.graph_utils as graph
import utils.patterns as patterns
import mining as mining


# ----------------------------
# Função Principal da Página de Usuários
# ----------------------------

def usersPage():
    st.title("Analisar Posts de um Usuário")

    actor = st.text_input("Digite o @ do usuário:", value="cruzeiro.com.br", key="actor_input")
    limit = st.number_input("Quantidade de posts por iteração:", min_value=1, max_value=100, value=10, key="limit_input")
    iterations = st.number_input("Número de iterações:", min_value=1, max_value=100, value=3, key="iterations_input")
    forecast_days = st.radio("Quantidade de dias para previsão de engajamento:", (3, 7, 30), key="days_radio")
    
    language = st.radio("Escolha o idioma:", ('Português', 'Inglês'), key="language_radio")
    language_code = 'portuguese' if language == 'Português' else 'english'
    
    if st.button("Analisar", key="analyze_button"):
        if actor:
            st.write("Coletando dados...")
            # Coleta os posts do usuário (certifique-se de que collectPosts esteja implementada)
            posts = bsky.collectPosts(actor, limit, iterations, language_code)

            if posts:
                st.write(f"Total de posts coletados: {len(posts)}")
                df = pd.DataFrame(posts)
                
                # Permite baixar o CSV dos posts coletados
                st.write("### Baixar Dados como CSV")
                csv = df.to_csv(index=False)
                st.download_button(label="Baixar CSV", data=csv, file_name="dados_posts.csv", mime="text/csv")
                
                # Exibe a WordCloud dos tokens
                st.write("### WordCloud das Palavras Mais Frequentes")
                graph.generate_wordcloud(df['tokens'])
                                
                # Distribuição dos valores (comentários, likes, compartilhamentos, repostagens)
                st.write("### Distribuição dos Valores")
                graph.distribution_values(df)
                
                # Análise de correlação entre os atributos
                st.write("### Correlação Entre os Atributos")
                graph.analyze_correlation(df)
                
                # # Exibe os tokens com maior engajamento
                # st.write("### Tokens com Mais Engajamento")
                # top_tokens = get_top_tokens(df)
                # st.dataframe(top_tokens)
                
                # Exibe os posts com maior engajamento
                st.write("### Posts com Maior Engajamento")
                top_posts = df.sort_values(by='total', ascending=False).head(5)
                for _, row in top_posts.iterrows():
                    st.write(f"**{row['author_displayName']}** (@{row['author_handle']}) - **Engajamento:** {row['total']}")
                    st.write(f"**Texto Original:** {row['texto_original']}")
                    
                    # Exibe imagens caso existam
                    embed = row.get("record", {}).get("embed", {}) if isinstance(row.get("record"), dict) else {}
                    if embed.get("$type") == "app.bsky.embed.images#view":
                        for image in embed.get("images", []):
                            image_url = image.get("fullsize", "")
                            if image_url:
                                st.image(image_url, caption="Imagem do Post", use_column_width=True)
                
                # Análise das características dos posts
                patterns.analyze_post_features(df)
                
                # Identificação de padrões nos posts de maior engajamento
                # patterns.identify_patterns(top_posts)

                # Evolução temporal de engajamento
                # st.write("### Evolução Temporal de Engajamento")
                df['data_hora'] = pd.to_datetime(df['data_hora'])
                temporal_data = df.groupby(df['data_hora'].dt.date)['total'].sum()
                # st.line_chart(temporal_data)     

                # Previsão de engajamento utilizando ARIMA
                st.write("### Previsão de Engajamento para os Próximos Dias")
                arima.train_arima(df, forecast_days)
                # Treinar modelo e sugerir post ideal
                melhor_hora, melhor_dia, melhor_tamanho = arima.analyze_best_post(df)                
                st.write("### Postagem Ideal Sugerida")
                st.write(f"Poste no dia {melhor_dia} às {melhor_hora}h com aproximadamente {melhor_tamanho} caracteres para obter maior engajamento.")

                # Análise de sentimentos e modelagem de tópicos
                mining.analyzeSentiment(df)
                mining.topicModeling(df)
                mining.display_sentiment_by_state(df)

            else:
                st.error("Nenhum dado encontrado para o usuário informado.")
        else:
            st.error("Por favor, insira o @ do usuário.")