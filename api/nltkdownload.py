import nltk
import os

# Define o caminho da pasta nltk_data dentro do diretório do projeto
nltk_data_path = os.path.join(os.getcwd(), "nltk_data")

# Cria a pasta se não existir
os.makedirs(nltk_data_path, exist_ok=True)

# Faz o download dos recursos dentro da pasta local
nltk.download("punkt", download_dir=nltk_data_path)
nltk.download("stopwords", download_dir=nltk_data_path)

print(f"Downloads concluídos em: {nltk_data_path}")
