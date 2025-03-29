# Análise e Previsão de Postagens no Bluesky


* Link: https://blueskyspy.streamlit.app/


## Descrição do Projeto

Este projeto tem como objetivo analisar os posts da rede social *Bluesky*. A aplicação interativa foi desenvolvida utilizando *Streamlit* e permite a coleta e visualização de dados, além de oferecer análises avançadas como previsão de engajamento, modelagem de tópicos e análise de sentimentos.

## Tecnologias Utilizadas

O projeto foi implementado em *Python* e utiliza diversas bibliotecas para diferentes propósitos:

- **Interface Gráfica:** Streamlit
- **Manipulação de Dados:** Pandas
- **Visualização de Dados:** Seaborn, Matplotlib, WordCloud, Folium
- **Processamento de Linguagem Natural:** NLTK, VADER, LDA
- **Previsão de Engajamento:** ARIMA
- **Coleta de Dados:** API do Bluesky

## Funcionalidades

A aplicação oferece diversas funcionalidades para uma análise detalhada do engajamento dos posts, incluindo:

- **Coleta de Dados:** Obtém posts da API do *Bluesky* com base no perfil selecionado.
- **Visualização de Palavras Frequentes:** Gera uma nuvem de palavras para destacar termos recorrentes.
- **Análise Temporal do Engajamento:** Identifica padrões de interação ao longo do tempo.
- **Previsão de Engajamento:** Utiliza o modelo ARIMA para prever o desempenho futuro dos posts.
- **Análise de Sentimentos:** Classifica os posts como positivos, negativos ou neutros usando o modelo VADER.
- **Modelagem de Tópicos:** Utiliza *Latent Dirichlet Allocation (LDA)* para identificar os principais temas das postagens.

## Resultados Obtidos

A análise realizada com base nos posts do *The New York Times* no *Bluesky* gerou os seguintes insights:

### 1. Análise Temporal do Engajamento

- Existe uma correlação positiva entre o número de caracteres e o engajamento.
- O engajamento é maior entre 00h e 06h, reduzindo durante o dia e aumentando novamente à noite.
- A previsão indica uma estabilização do engajamento em torno de 40.000 interações.

### 2. Análise de Sentimentos

- A maioria das postagens apresenta um tom neutro.
- Há um leve viés para sentimentos negativos.

### 3. Análise de Tópicos

- Os principais tópicos abordados incluem política e administração pública.
- O nome "Trump" aparece em vários tópicos analisados.

## Como Executar o Projeto

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   ```
2. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a aplicação:
   ```bash
   streamlit run app.py
   ```

## Conclusão

Este projeto fornece insights detalhados sobre o engajamento das postagens no *Bluesky*, permitindo uma melhor compreensão dos padrões de interação e previsões mais precisas sobre o sucesso de novas publicações. O modelo pode ser expandido para outras redes sociais e aprimorado com técnicas avançadas de previsão e processamento de linguagem natural.

## Autor
João Antônio Santos Carvalho - 2025
