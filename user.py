import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from wordcloud import WordCloud

# Imports de funções customizadas (certifique-se de que os módulos existam e estejam implementados)
from blueskyApi import collectPosts
from mining import analyzeSentiment, topicModeling

# ----------------------------
# Funções de Pré-processamento e Visualização
# ----------------------------

def generate_wordcloud(tokens_list):
    """
    Gera e exibe uma wordcloud com base em uma lista de tokens.
    """
    # Junta todos os tokens em uma única string
    all_tokens = ' '.join([' '.join(tokens) for tokens in tokens_list])
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(all_tokens)
    
    # Exibe a wordcloud
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title("WordCloud das Palavras Mais Frequentes", fontsize=16)
    st.pyplot(fig)

def distribution_values(df):
    """
    Exibe histogramas para as colunas numéricas de interesse.
    """
    numeric_columns = ['comentarios', 'likes', 'compartilhamentos', 'repostagens']
    sns.set(style="whitegrid")

    for column in numeric_columns:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.histplot(df[column], bins=20, kde=True, ax=ax)
        ax.set_title(f'Histograma de {column}')
        ax.set_xlabel(column)
        ax.set_ylabel('Frequência')
        st.pyplot(fig)

def analyze_correlation(df):
    """
    Calcula e exibe a matriz de correlação e seu respectivo mapa de calor.
    """
    numeric_columns = ['comentarios', 'likes', 'compartilhamentos', 'repostagens', 'total']
    matriz_correlacao = df[numeric_columns].corr()

    st.write("### Matriz de Correlação")
    st.dataframe(matriz_correlacao)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(matriz_correlacao, annot=True, fmt=".2f", cmap='coolwarm', cbar=True, square=True,
                linewidths=0.5, linecolor='black', ax=ax)
    ax.set_title('Mapa de Calor da Correlação Entre Atributos')
    st.pyplot(fig)

def get_top_tokens(df, top_n=10):
    """
    Retorna um DataFrame com os tokens que acumularam maior engajamento.
    """
    token_engagement = {}
    for _, row in df.iterrows():
        for token in row['tokens']:
            token_engagement[token] = token_engagement.get(token, 0) + row['total']
    return pd.DataFrame(list(token_engagement.items()), columns=['Token', 'Engajamento']) \
             .sort_values(by='Engajamento', ascending=False).head(top_n)

# ----------------------------
# Previsão com ARIMA
# ----------------------------

def train_arima(df, forecast_days):
    """
    Realiza a previsão do engajamento dos posts para os próximos dias utilizando ARIMA.
    """
    st.write("## Previsão de Engajamento com ARIMA")
    # Converte a coluna 'data_hora' para datetime e ordena os dados
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    df = df.sort_values('data_hora')
    
    # Agrega o engajamento diário (pode ser ajustado para outra granularidade)
    df_daily = df.set_index('data_hora').resample('D')['total'].sum().fillna(0)
    
    st.write("### Série Temporal Diária de Engajamento")
    st.line_chart(df_daily)
    
    # Define e treina o modelo ARIMA (a ordem pode ser ajustada conforme os dados)
    try:
        model = ARIMA(df_daily, order=(5, 1, 0))
        model_fit = model.fit()
    except Exception as e:
        st.error(f"Erro ao ajustar o modelo ARIMA: {e}")
        return
    
    # Realiza a previsão para os próximos 'forecast_days' dias
    forecast = model_fit.forecast(steps=forecast_days)
    st.write("### Previsão para os Próximos Dias")
    st.line_chart(forecast)
    st.dataframe(forecast.reset_index().rename(columns={'index': 'Data', 0: 'Engajamento Previsto'}))

# ----------------------------
# Análise de Características dos Posts
# ----------------------------

def analyze_post_features(df):
    """
    Analisa características dos posts que possam estar associadas a engajamento alto ou baixo.
    """
    st.write("## Análise de Características dos Posts Relacionadas ao Engajamento")
    
    # 1. Quantidade de caracteres
    df['num_caracteres'] = df['texto_original'].apply(len)
    st.write("### Relação entre Quantidade de Caracteres e Engajamento")
    fig, ax = plt.subplots()
    sns.scatterplot(x='num_caracteres', y='total', data=df, ax=ax)
    ax.set_title("Engajamento vs. Número de Caracteres")
    st.pyplot(fig)
    
    # Exibe correlação entre número de caracteres e engajamento
    corr_chars = df[['num_caracteres', 'total']].corr().iloc[0, 1]
    st.write(f"Correlação entre número de caracteres e engajamento: {corr_chars:.2f}")
    
    # 2. Horário de Postagem
    df['hora'] = pd.to_datetime(df['data_hora']).dt.hour
    st.write("### Engajamento Médio por Hora de Postagem")
    eng_por_hora = df.groupby('hora')['total'].mean().reset_index()
    fig2, ax2 = plt.subplots()
    sns.lineplot(x='hora', y='total', data=eng_por_hora, marker='o', ax=ax2)
    ax2.set_title("Engajamento Médio por Hora")
    ax2.set_xlabel("Hora do Dia")
    ax2.set_ylabel("Engajamento Médio")
    st.pyplot(fig2)
    
    # 3. Tokens com Maior Engajamento
    st.write("### Tokens com Maior Acúmulo de Engajamento")
    top_tokens = get_top_tokens(df)
    st.dataframe(top_tokens)

# ----------------------------
# Identificação de Padrões nos Posts de Maior Engajamento
# ----------------------------

def identify_patterns(top_posts):
    """
    Realiza análise de padrões dos posts de maior engajamento:
      - Geração de wordcloud com os tokens mais frequentes.
      - Análise de sentimentos.
      - Modelagem de tópicos.
      - Visualização do horário de postagem.
    """
    st.write("### Identificação de Padrões nos Posts de Maior Engajamento")
    
    # Palavras mais frequentes
    st.write("#### Palavras Mais Frequentes")
    generate_wordcloud(top_posts['tokens'])
    
    # Análise de Sentimentos
    st.write("#### Análise de Sentimentos")
    sentiment_data = analyzeSentiment(top_posts)
    st.dataframe(sentiment_data[['texto_original', 'neg', 'neu', 'pos', 'compound']])
    
    # Modelagem de Tópicos
    st.write("#### Modelagem de Tópicos")
    topics = topicModeling(top_posts, num_topics=3, passes=5)
    for topic in topics:
        st.write(f"Tópico {topic[0]}: {topic[1]}")
    
    # Horário de Postagem
    st.write("#### Horário de Postagem")
    top_posts['data_hora'] = pd.to_datetime(top_posts['data_hora'])
    post_hours = top_posts['data_hora'].dt.hour.value_counts().sort_index()
    st.line_chart(post_hours)

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
            posts = collectPosts(actor, limit, iterations, language_code)

            if posts:
                st.write(f"Total de posts coletados: {len(posts)}")
                df = pd.DataFrame(posts)
                
                # Permite baixar o CSV dos posts coletados
                st.write("### Baixar Dados como CSV")
                csv = df.to_csv(index=False)
                st.download_button(label="Baixar CSV", data=csv, file_name="dados_posts.csv", mime="text/csv")
                
                # Exibe a WordCloud dos tokens
                st.write("### WordCloud das Palavras Mais Frequentes")
                generate_wordcloud(df['tokens'])
                
                # Evolução temporal de engajamento
                st.write("### Evolução Temporal de Engajamento")
                df['data_hora'] = pd.to_datetime(df['data_hora'])
                temporal_data = df.groupby(df['data_hora'].dt.date)['total'].sum()
                st.line_chart(temporal_data)
                
                # Previsão de engajamento utilizando ARIMA
                st.write("### Previsão de Engajamento para os Próximos Dias")
                train_arima(df, forecast_days)
                
                # Distribuição dos valores (comentários, likes, compartilhamentos, repostagens)
                st.write("### Distribuição dos Valores")
                distribution_values(df)
                
                # Análise de correlação entre os atributos
                st.write("### Correlação Entre os Atributos")
                analyze_correlation(df)
                
                # Exibe os tokens com maior engajamento
                st.write("### Tokens com Mais Engajamento")
                top_tokens = get_top_tokens(df)
                st.dataframe(top_tokens)
                
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
                analyze_post_features(df)
                
                # Identificação de padrões nos posts de maior engajamento
                identify_patterns(top_posts)
            else:
                st.error("Nenhum dado encontrado para o usuário informado.")
        else:
            st.error("Por favor, insira o @ do usuário.")