# ---------------------------------------------------
# 📚 Configuração e Download Local dos Recursos NLTK
# ---------------------------------------------------

import nltk
import os

# 📁 Define o caminho absoluto para a pasta 'nltk_data' dentro do diretório atual do projeto
nltk_data_path = os.path.join(os.getcwd(), "nltk_data")

# 🏗️ Cria a pasta 'nltk_data' se ela ainda não existir
os.makedirs(nltk_data_path, exist_ok=True)

# ⬇️ Faz o download do tokenizer de palavras (usado para dividir frases em palavras)
nltk.download("punkt", download_dir=nltk_data_path)

# ⬇️ Faz o download das stopwords (lista de palavras irrelevantes para análise de texto, como "a", "de", "para", etc.)
nltk.download("stopwords", download_dir=nltk_data_path)

# ✅ Confirmação visual no console
print(f"Downloads concluídos em: {nltk_data_path}")
