import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from blueskyApi import collectPosts

st.title("Análise de Posts do Bluesky")

actor = st.text_input("Digite o @ do usuário (exemplo: user.bsky.social):")
limit = st.number_input("Quantidade de posts por iteração:", min_value=1, max_value=100, value=10)
iterations = st.number_input("Número de iterações:", min_value=1, max_value=10, value=1)

if st.button("Analisar"):
    if actor:
        st.write("Coletando dados...")
        posts = collectPosts(actor, limit, iterations)

        if posts:
            st.write(f"Total de posts coletados: {len(posts)}")

            # Criar DataFrame
            df = pd.DataFrame(posts)

            # Gráfico de interações
            st.write("### Interações nos Posts")
            fig, ax = plt.subplots()
            df[['comentarios', 'likes', 'compartilhamentos', 'repostagens']].sum().plot(kind='bar', ax=ax)
            ax.set_ylabel("Quantidade")
            ax.set_title("Interações nos Posts")
            st.pyplot(fig)

            # Palavras mais frequentes
            st.write("### Palavras Mais Frequentes")
            word_count = pd.Series([word for tokens in df['tokens'] for word in tokens]).value_counts().head(10)
            st.bar_chart(word_count)

        else:
            st.error("Nenhum dado encontrado para o usuário informado.")
    else:
        st.error("Por favor, insira o @ do usuário.")
