import nltk
import shutil
import os

# Caminho para os dados do NLTK
nltk_data_path = os.path.join(os.getcwd(), "nltk_data")

# Remover pastas problemáticas
if os.path.exists(nltk_data_path):
    shutil.rmtree(nltk_data_path)

# Baixar os pacotes novamente
nltk.download('punkt', download_dir=nltk_data_path)
nltk.download('stopwords', download_dir=nltk_data_path)

# Adicionar caminho manualmente
nltk.data.path.append(nltk_data_path)

print("Pacotes baixados e armazenados em:", nltk_data_path)