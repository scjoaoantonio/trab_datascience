import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from blueskyApi import collectPosts

def get_top_tokens(df):
    token_engagement = {}
    for _, row in df.iterrows():
        for token in row['tokens']:
            if token not in token_engagement:
                token_engagement[token] = 0
            token_engagement[token] += row['total']
    return pd.DataFrame(list(token_engagement.items()), columns=['Token', 'Engajamento']).sort_values(by='Engajamento', ascending=False).head(10)

def usersPage():
    st.title("Analisar Posts de um Usuário")

    actor = st.text_input("Digite o @ do usuário:", value="cruzeiro.com.br", key="actor_input")
    limit = st.number_input("Quantidade de posts por iteração:", min_value=1, max_value=100, value=10, key="limit_input")
    iterations = st.number_input("Número de iterações:", min_value=1, max_value=10, value=3, key="iterations_input")


    if st.button("Analisar", key="analyze_button"):
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

                # Tokens com mais engajamento
                st.write("### Tokens com Mais Engajamento")
                top_tokens = get_top_tokens(df)
                st.dataframe(top_tokens)

                # Baixar CSV
                st.write("### Baixar Dados como CSV")
                csv = df.to_csv(index=False)
                st.download_button(label="Baixar CSV", data=csv, file_name="dados_posts.csv", mime="text/csv")

                # Posts com mais engajamento
                st.write("### Posts com Mais Engajamento")
                top_posts = df.sort_values(by='total', ascending=False).head(5)

                for _, row in top_posts.iterrows():
                    st.write(f"**Nome:** {row['author_displayName']} - **Usuário:** {row['author_handle']}")
                    st.write(f"**Texto Original:** {row['texto_original']}")

                    # Verificar se há imagens associadas ao post
                    embed = row.get("record", {}).get("embed", {})
                    if embed.get("$type") == "app.bsky.embed.images#view":
                        for image in embed.get("images", []):
                            image_url = image.get("fullsize", "")
                            if image_url:
                                st.image(image_url, caption="Imagem do Post", use_column_width=True)

                    st.write(f"**Engajamento Total:** {row['total']}\n---")





                # Gráfico de evolução temporal
                st.write("### Evolução Temporal de Engajamento")
                df['data_hora'] = pd.to_datetime(df['data_hora'])
                temporal_data = df.groupby(df['data_hora'].dt.date)['total'].sum()
                st.line_chart(temporal_data)

            else:
                st.error("Nenhum dado encontrado para o usuário informado.")
        else:
            st.error("Por favor, insira o @ do usuário.")
