import streamlit as st
import pandas as pd
import blueskyApi

# Função principal para buscar e processar os posts
def buscar_e_processar_posts(tema, limit):
    textos_gerais = []
    autores_gerais = []

    result = blueskyApi.search_posts(tema, limit)
    if result:
        textos = []
        usuarios = []

        for post in result.get("posts", []):
            record = post.get("record")
            author = post.get("author")

            if record and author:
                textos.append(record.get("text"))
                usuarios.append(author.get("handle"))

        textos_gerais.extend(textos)
        autores_gerais.extend(usuarios)

    # Criar DataFrame com os dados coletados
    data = {"Texto": textos_gerais, "Usuario": autores_gerais}
    df_posts = pd.DataFrame(data)

    # Converter os valores para string e substituir NaN por string vazia
    df_posts['Texto'] = df_posts['Texto'].fillna("").astype(str)

    # Limpeza dos textos
    df_posts['Texto_Limpo'] = (
        df_posts['Texto']
        .str.replace(r'http\S+', '', regex=True)  # Remove links
        .str.replace(r'[^a-zA-Z\s]', '', regex=True)  # Remove caracteres especiais
        .str.lower()  # Converte para minúsculas
    )

    # Remover palavras vazias resultantes da limpeza
    df_posts['Texto_Limpo'] = df_posts['Texto_Limpo'].apply(
        lambda x: " ".join([word for word in x.split()])
    )

    return df_posts

# Página principal da aplicação Streamlit
def topicPage():
    st.title("Busca e Processamento de Posts com Bluesky API")

    # Entrada do usuário para definir as palavras-chave e o limite de posts
    tema = st.text_input("Digite o tema para buscar os posts (exemplo: Cruzeiro):", "Cruzeiro")
    limit = st.number_input("Número máximo de posts por tema:", min_value=1, value=5, step=1)

    # Botão para buscar os posts
    if st.button("Buscar Posts"):
        st.write(f"Buscando posts sobre o tema: **{tema}** com limite de {limit} posts...")
        df_posts = buscar_e_processar_posts([tema], limit)

        if not df_posts.empty:
            # Mostrar os resultados na interface
            st.write("### Resultados da Busca")
            st.dataframe(df_posts)

            # Baixar os dados como arquivo CSV
            csv = df_posts.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar CSV",
                data=csv,
                file_name="posts.csv",
                mime="text/csv",
            )
        else:
            st.write("Nenhum post encontrado para o tema especificado.")
