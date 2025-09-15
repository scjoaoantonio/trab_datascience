# ---------------------------------------------------
# 📦 Importações de Bibliotecas e Módulos do Projeto
# ---------------------------------------------------
import streamlit as st
import pandas as pd

# 🧩 Módulos personalizados para análise de dados
import api as bsky                     # API personalizada para coleta e limpeza de dados do Bluesky
import utils.mining as mining         # Mineração de texto: sentimentos, tópicos, etc.
import utils.arima_model as arima     # Modelagem preditiva com ARIMA
import utils.graph_utils as graph     # Gráficos e visualizações
import utils.patterns as patterns     # Análise de padrões em posts
import utils.map as maps              # Geração de mapas interativos

# ---------------------------------------------------
# 🧑‍💻 Função Principal da Página de Análise por Usuário
# ---------------------------------------------------
def usersPage():
    st.title("Analisar Posts de um Usuário")

    # 🔧 Inputs de configuração da análise
    actor = st.text_input("Digite o @ do usuário:", value="nytimes.com", key="actor_input")
    limit = st.number_input("Quantidade de posts por iteração:", min_value=1, max_value=100, value=100, key="limit_input")
    iterations = st.number_input("Número de iterações:", min_value=1, value=100, key="iterations_input")
    forecast_days = st.radio("Quantidade de dias para previsão de engajamento:", (3, 7, 30), key="days_radio")
    
    language = st.radio("Escolha o idioma:", ('Português', 'Inglês'), key="language_radio")
    language_code = 'portuguese' if language == 'Português' else 'english'

    # ▶️ Botão para iniciar análise
    if st.button("Analisar", key="analyze_button"):
        if actor:
            bsky.nltkDownload()  # Garante que os dados do NLTK estão configurados corretamente
            st.write("Coletando dados...")

            # 📥 Coleta os posts do usuário
            posts = bsky.collectPosts(actor, limit, iterations, language_code)

            if posts:
                st.write(f"Total de posts coletados: {len(posts)}")
                df = pd.DataFrame(posts)

                # 💾 Permite download dos dados coletados
                st.write("### Baixar Dados como CSV")
                csv = df.to_csv(index=False)
                st.download_button(label="Baixar CSV", data=csv, file_name="dados_posts.csv", mime="text/csv")

                # ☁️ Geração de WordCloud
                st.write("### WordCloud das Palavras Mais Frequentes")
                graph.generate_wordcloud(df['tokens'])

                # 📊 Distribuição das métricas de engajamento
                st.write("### Distribuição dos Valores")
                graph.distribution_values(df)

                # 🔥 Análise de correlação entre variáveis
                st.write("### Correlação Entre os Atributos")
                graph.analyze_correlation(df)

                # 🌟 Destaque para os posts com maior engajamento
                st.write("### Posts com Maior Engajamento")
                top_posts = df.sort_values(by='total', ascending=False).head(5)
                for _, row in top_posts.iterrows():
                    st.write(f"**{row['author_displayName']}** (@{row['author_handle']}) - **Engajamento:** {row['total']}")
                    st.write(f"**Texto Original:** {row['texto_original']}")

                    # 🖼️ Exibe imagens dos posts, se houver
                    embed = row.get("record", {}).get("embed", {}) if isinstance(row.get("record"), dict) else {}
                    if embed.get("$type") == "app.bsky.embed.images#view":
                        for image in embed.get("images", []):
                            image_url = image.get("fullsize", "")
                            if image_url:
                                st.image(image_url, caption="Imagem do Post", use_column_width=True)

                # 🔍 Análise de padrões nos posts (ex: tamanho do texto, horários, etc.)
                patterns.analyze_post_features(df)

                # 📈 Pré-processa para análise temporal
                df['data_hora'] = pd.to_datetime(df['data_hora'])
                temporal_data = df.groupby(df['data_hora'].dt.date)['total'].sum()
                # st.line_chart(temporal_data)  # Você pode ativar isso se quiser mostrar a linha do tempo

                # 📉 Previsão de engajamento com ARIMA
                st.write("### Previsão de Engajamento para os Próximos Dias")
                arima.train_arima(df, forecast_days)

                # 🕒 Recomendações com base nos melhores horários e tamanhos de post
                melhor_hora, melhor_dia, melhor_tamanho = arima.analyze_best_post(df)

                # 💬 Análise de sentimentos, modelagem de tópicos e geolocalização
                mining.analyzeSentiment(df)
                mining.topicModeling(df)
                mining.analyze_sentiment_by_state(df)
                maps.create_sentiment_map(df)

            else:
                st.error("Nenhum dado encontrado para o usuário informado.")
        else:
            st.error("Por favor, insira o @ do usuário.")
