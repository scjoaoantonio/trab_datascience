import nltk
import os

nltk_data_path = os.path.join(os.getcwd(), "nltk_data")
os.makedirs(nltk_data_path, exist_ok=True)

nltk.data.path.append(nltk_data_path)

nltk.download('punkt', download_dir=nltk_data_path)
print(nltk.data.find('tokenizers/punkt'))