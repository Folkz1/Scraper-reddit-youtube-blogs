"""
Teste direto da API do OpenRouter
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

print("🧪 Teste da API OpenRouter")
print("=" * 60)
print(f"API Key: {OPENROUTER_API_KEY[:20]}...{OPENROUTER_API_KEY[-10:]}")
print()

# Teste 1: Simples (sem imagem)
print("📝 Teste 1: Request simples (sem imagem)")
print("-" * 60)

payload = {
    "model": "google/gemini-2.5-flash",
    "messages": [
        {
            "role": "user",
            "content": "Responda apenas: OK"
        }
    ]
}

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://scraper-api.com",
    "X-Title": "Celebrity Image Scraper Test"
}

try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        json=payload,
        headers=headers,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        print(f"✅ Sucesso! Resposta: {content}")
    else:
        print(f"❌ Erro {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Erro: {str(e)}")

print()

# Teste 2: Com imagem
print("🖼️  Teste 2: Request com análise de imagem")
print("-" * 60)

# URL de imagem de teste (Jojo Todynho da Wikipedia)
test_image_url = "https://upload.wikimedia.org/wikipedia/commons/f/f8/Jojo_Todynho.png"

payload2 = {
    "model": "google/gemini-2.5-flash",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Descreva esta imagem em uma frase curta."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": test_image_url
                    }
                }
            ]
        }
    ]
}

try:
    print(f"Imagem: {test_image_url}")
    print("Enviando request...")
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        json=payload2,
        headers=headers,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        print(f"✅ Sucesso! Resposta: {content}")
    else:
        print(f"❌ Erro {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Erro: {str(e)}")

print()
print("=" * 60)
print("Teste concluído!")
