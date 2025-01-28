import streamlit as st

# Importar as funções para as páginas
from user import usersPage
from topic import topicPage
from network import networkPage

# Configurar o menu principal
st.sidebar.title("Menu")
option = st.sidebar.radio("Navegar para:", ["Analisar Usuário", "Analisar Tema", "Analisar Rede"])

# Exibir a página escolhida
if option == "Analisar Usuário":
    usersPage()
elif option == "Analisar Tema":
    topicPage()
elif option == "Analisar Rede":
    networkPage()