import streamlit as st

# Importar as funções para as páginas
from user import usersPage
from topic import topicPage

# Configurar o menu principal
st.sidebar.title("Menu")
option = st.sidebar.radio("Navegar para:", ["Analisar Usuário", "Análisar Tema"])

# Exibir a página escolhida
if option == "Analisar Usuário":
    usersPage()
elif option == "Análisar Tema":
    topicPage()
