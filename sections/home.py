import streamlit as st
from PIL import Image
import pandas as pd

# ----------------------------
# Função Principal da Página
# ----------------------------

def mainPage():
    # Estilizando com CSS
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0E1117;
        }
        h1, h2, h3, p {
            color: white;
        }
        .card {
            background-color: #1A1D24;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        .engajamento {
            font-size: 1.5em;
            color: #FF6F61;
        }
        .positivo {
            font-size: 1.5em;
            color: #90ee90;
        }
        .negativo {
            font-size: 1.5em;
            color: #FF6F61;
        }
        .texto {
            font-size: 1.2em;
            color: #F0F0F0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Título da página
    st.title("📊 Análise de Posts - NYTIMES")

    # Carregar imagens
    image_wordcloud = Image.open("img/wordcloud.png")
    image_likes = Image.open("img/likes.png")
    image_comentarios = Image.open("img/comentarios.png")
    image_compartilhamentos = Image.open("img/compartilhamentos.png")
    image_repostagem = Image.open("img/repostagem.png")
    image_correlacao = Image.open("img/correlação.png")
    image_engChar = Image.open("img/engChar.png")
    image_engHora = Image.open("img/engHora.png")
    image_engPrevisao = Image.open("img/engPrevisao.jpeg")
    image_engTempo = Image.open("img/engTempo.jpeg")
    image_engWordcloud = Image.open("img/engWordcloud.png")
    image_modelagem = Image.open("img/modelagem.jpeg")
    image_vader = Image.open("img/vader.jpeg")

    # ----------------------------
    # 🌍 WordCloud - Palavras Mais Frequentes
    # ----------------------------
    st.header("🌍 Palavras Mais Frequentes")
    st.write("As palavras mais recorrentes nos posts analisados.")
    st.image(image_wordcloud, caption="WordCloud das Palavras Mais Frequentes", use_container_width=True)

    # ----------------------------
    # 📊 Análise de Engajamento (Likes, Comentários, Compartilhamentos, Repostagens)
    # ----------------------------

    # Posts com mais engajamento
    posts = [
        {
            "titulo": "The New York Times",
            "user": "@nytimes",
            "engajamento": 19816,
            "texto": "Breaking News: Finland seized an oil tanker it suspected of involvement in damaging undersea cables and suggested it could be part of a Russian shadow fleet."
        },
        {
            "titulo": "The New York Times",
            "user": "@nytimes",
            "engajamento": 17908,
            "texto": "Breaking News: The Palisades and Eaton fires in Los Angeles County, two of the deadliest fires in California history, have reached 100% containment."
        },
        {
            "titulo": "The New York Times",
            "user": "@nytimes",
            "engajamento": 16718,
            "texto": "The Tulsa Race Massacre was not committed by an uncontrolled mob but was the result of “a coordinated, military-style attack” by white citizens, the Justice Department said."
        },
        {
            "titulo": "The New York Times",
            "user": "@nytimes",
            "engajamento": 13307,
            "texto": "Conan O’Brien will be awarded the 26th annual Mark Twain Prize for American Humor in March, the John F. Kennedy Center for the Performing Arts announced Thursday."
        },
        # {
        #     "titulo": "The New York Times",
        #     "user": "@nytimes",
        #     "engajamento": 12663,
        #     "texto": "UnitedHealthcare has been accused of using algorithms to deny treatments and refusing coverage of nursing care to stroke patients."
        # },
    ]

    # Adicionando cards para os posts com mais engajamento em duas colunas
    st.header("🌟 Posts com Maior Engajamento")
    cols = st.columns(2)  # Criando duas colunas
    for i, post in enumerate(posts):
        with cols[i % 2]:  # Distribui os posts alternadamente entre as colunas
            st.markdown(
                f"""
                <div class="card">
                    <strong>{post['user']}</strong>
                    <h3>{post['titulo']} - <span class="engajamento">{post['engajamento']}</span></h3>
                    <p class="texto">{post['texto']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.header("📊 Análise de Engajamento")
    st.write("Visualização dos principais indicadores de engajamento.")

    cols = st.columns(2)
    with cols[0]:
        st.image(image_likes, caption="Distribuição de Likes", use_container_width=True)
    with cols[1]:
        st.image(image_comentarios, caption="Distribuição de Comentários", use_container_width=True)

    cols = st.columns(2)
    with cols[0]:
        st.image(image_compartilhamentos, caption="Distribuição de Compartilhamentos", use_container_width=True)
    with cols[1]:
        st.image(image_repostagem, caption="Distribuição de Repostagens", use_container_width=True)

    # ----------------------------
    # 🔥 Correlação entre Métricas
    # ----------------------------

    st.header("🔥 Correlação Entre Métricas de Engajamento")
    st.write("Mapa de calor mostrando a correlação entre diferentes métricas de engajamento.")
    st.image(image_correlacao, caption="Mapa de Correlação", use_container_width=True)

    # ----------------------------
    # 📅 Análise Temporal do Engajamento
    # ----------------------------
    st.header("📅 Análise Temporal do Engajamento")
    st.write("Como o engajamento varia ao longo do tempo e por características do post.")

    cols = st.columns(2)
    with cols[0]:
        st.image(image_engChar, caption="Engajamento vs. Número de Caracteres", use_container_width=True)
    with cols[1]:
        st.image(image_engHora, caption="Engajamento Médio por Hora do Dia", use_container_width=True)

    cols = st.columns(2)
    with cols[0]:
        st.image(image_engTempo, caption="Tendência do Engajamento ao Longo do Tempo", use_container_width=True)
    with cols[1]:
        st.image(image_engPrevisao, caption="Previsão do Engajamento Futuro", use_container_width=True)

    # ----------------------------
    # 🌟 Posts com Maior Engajamento
    # ----------------------------
    st.header("🌟 Posts com Maior Engajamento")
    cols = st.columns(2)  # Criando duas colunas
    for i, post in enumerate(posts):
        with cols[i % 2]:  # Distribui os posts alternadamente entre as colunas
            st.markdown(
                f"""
                <div class="card">
                    <strong>{post['user']}</strong>
                    <h3>{post['titulo']} <span class="engajamento">{post['engajamento']}</span></h3>
                    <p class="texto">{post['texto']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


    # ----------------------------
    # 🌍 WordCloud - Engajamento
    # ----------------------------
    st.header("🌍 Palavras Frequentes em Posts Mais Engajados")
    st.write("Quais palavras aparecem com mais frequência em posts que tiveram alto engajamento?")
    st.image(image_engWordcloud, caption="WordCloud de Postagens com Maior Engajamento", use_container_width=True)

    # ----------------------------
    # 💬 Análise de Sentimentos
    # ----------------------------
    st.header("💬 Análise de Sentimentos")
    st.write("Distribuição dos sentimentos dos posts usando o modelo VADER.")
    st.image(image_vader, caption="Distribuição dos Sentimentos", use_container_width=True)


    # Postagens mais positivas
    postagens_positivas = [
        {
            "texto": "kendrick lamars like u win record year th annual grammy award...",
            "score": 0.9732
        },
        {
            "texto": "beyoncé win grammy best country album cowboy carter...",
            "score": 0.969
        },
        # {
        #     "texto": "going honoring hero honoring greatest people country...",
        #     "score": 0.9584
        # },
    ]

    # Postagens mais negativas
    postagens_negativas = [
        {
            "texto": "coffee tea consumption may associated reduced risk head neck cancer...",
            "score": -0.9618
        },
        {
            "texto": "senate tuesday expected begin voting whether sanction international criminal court...",
            "score": -0.9595
        },
        # {
        #     "texto": "thursday deadline looming decide whether take trump administration...",
        #     "score": -0.9371
        # },
    ]

    # Adicionando cards para postagens mais positivas em duas colunas
    st.subheader("Postagens Mais Positivas:")
    cols = st.columns(2)  # Criando duas colunas
    for i, post in enumerate(postagens_positivas):
        with cols[i % 2]:  # Distribui os posts alternadamente entre as colunas
            st.markdown(
                f"""
                <div class="card">
                    <b>Score:  <span class="positivo">{post['score']}</span></b>
                    <p class="texto">{post['texto']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Adicionando cards para postagens mais negativas em duas colunas
    st.subheader("Postagens Mais Negativas:")
    cols = st.columns(2)  # Criando duas colunas
    for i, post in enumerate(postagens_negativas):
        with cols[i % 2]:  # Distribui os posts alternadamente entre as colunas
            st.markdown(
                f"""
                <div class="card">
                    <b>Score:  <span class="negativo">{post['score']}</span></b>
                    <p class="texto">{post['texto']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Informações sobre Sentimentos por Estado
    st.subheaderheader("📍 Análise de Sentimentos por Estado")
    st.write("Com base na análise de sentimentos, destacamos os estados com as avaliações mais positivas e negativas.")
        
    st.markdown(
        """
        <div class="card">
            <h3>NYT - Estado com Sentimento Mais Positivo</h3>
            <p class="positivo"><strong>New Hampshire (0.26)</strong></p>
        </div>
        <div class="card">
            <h3>NYT - Estado com Sentimento Mais Negativo</h3>
            <p class="negativo"><strong>Mississippi (-0.59)</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # ----------------------------
    # 🏷️ Modelagem de Tópicos
    # ----------------------------
    st.header("🏷️ Modelagem de Tópicos")
    st.write("Nesta seção, apresentamos a identificação de padrões e temas mais frequentes nos posts analisados através do modelo LDA (Latent Dirichlet Allocation). Abaixo, estão os cinco tópicos mais relevantes identificados pelo modelo:")

    # Criando uma tabela para melhor visualização
    tópicos = {
        "Tópico": [
            "Tópico 0",
            "Tópico 1",
            "Tópico 2",
            "Tópico 3",
            "Tópico 4",
        ],
        "Temas Principais": [
            "Política e Transporte Aéreo: ('trump', 'helicopter', 'airport')",
            "Governo e Agências Federais: ('president', 'official', 'agency')",
            "Governo e Políticas Públicas: ('federal', 'government', 'department')",
            "Administração Presidencial: ('administration', 'people', 'first')",
            "Ordem Executiva e Casa Branca: ('order', 'white', 'house')",
        ]
    }

    # Adicionando a imagem da modelagem de tópicos
    st.image(image_modelagem, caption="Visualização da Modelagem de Tópicos", use_container_width=True)
    # Exibindo os tópicos em formato de tabela
    st.write(pd.DataFrame(tópicos).set_index("Tópico"))