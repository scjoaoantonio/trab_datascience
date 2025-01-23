import requests

# Endpoint público do Bluesky
url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"

# Parâmetros (apenas o essencial)
params = {
    "q": "cruzeiro"
}

# Cabeçalhos (com autenticação, se necessário)
headers = {
    "User-Agent": "MinhaAplicacao/1.0",
    # "Authorization": f"Bearer {seu_token}"  # Descomente e insira o token, se necessário
}

# Fazer a requisição
response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    print("Dados recebidos com sucesso:", response.json())
else:
    print(f"Erro: {response.status_code} - {response.text}")
