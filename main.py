import streamlit as st

from sections import mainPage, usersPage, topicPage, networkPage
from streamlit_option_menu import option_menu

st.markdown(
    """
    <style> 
    /* Estilizar a barra lateral */
    [data-testid="stSidebar"] {
        background-color: #131722 !important;
    }
    
    /* Estilizar os textos e ícones da barra lateral */
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Estilizar o fundo principal */
    [data-testid="stAppViewContainer"] {
        background-color: #0E1117 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    option = option_menu(
        menu_title = "",
        options = ["Apresentação","Analisar Usuário","Analisar Tema", "Analisar Rede"],
        icons = ["house","gear","activity","envelope"],
        menu_icon = "cast",
        default_index = 0,
        # orientation = "horizontal",
    )

if option == "Apresentação":
    mainPage()
elif option == "Analisar Usuário":
    usersPage()
# elif option == "Analisar Tema":
#     topicPage()
# elif option == "Analisar Rede":
#     networkPage()
