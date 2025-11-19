"""
Teste isolado da OpenRouter API para debug
"""
import requests
import json

import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Teste simples sem imagens primeiro
print("🔍 Testando OpenRouter API...")
print(f"API Key: {OPENROUTER_API_KEY[:20]}...")

# Teste 1: Texto simples
print("\n📝 Teste 1: Mensagem de texto simples (GPT-4o-mini)")
payload = {
    "model": "openai/gpt-4o-mini",
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
    "X-Title": "Celebrity Image Scraper"
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
        result = response.json()
        print(f"✅ Sucesso!")
        print(f"Resposta: {result['choices'][0]['message']['content']}")
    else:
        print(f"❌ Erro {response.status_code}")
        print(f"Resposta: {response.text}")
        
except Exception as e:
    print(f"❌ Exceção: {str(e)}")

# Teste 2: Com imagem
print("\n\n🖼️  Teste 2: Mensagem com imagem (GPT-4o-mini)")
payload_with_image = {
    "model": "openai/gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Descreva esta imagem em uma palavra."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://i.ytimg.com/vi/bJsnw0hb_S0/hq720.jpg"
                    }
                }
            ]
        }
    ]
}

try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        json=payload_with_image,
        headers=headers,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sucesso!")
        print(f"Resposta: {result['choices'][0]['message']['content']}")
    else:
        print(f"❌ Erro {response.status_code}")
        print(f"Resposta: {response.text}")
        
except Exception as e:
    print(f"❌ Exceção: {str(e)}")

# Teste 3: Com JSON response format
print("\n\n📋 Teste 3: Com JSON response format")
payload_json = {
    "model": "google/gemini-2.0-flash-exp:free",
    "messages": [
        {
            "role": "user",
            "content": 'Retorne um JSON com {"status": "ok"}'
        }
    ],
    "response_format": {
        "type": "json_object"
    }
}

try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        json=payload_json,
        headers=headers,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sucesso!")
        print(f"Resposta: {result['choices'][0]['message']['content']}")
    else:
        print(f"❌ Erro {response.status_code}")
        print(f"Resposta: {response.text}")
        
except Exception as e:
    print(f"❌ Exceção: {str(e)}")

print("\n\n✅ Testes concluídos!")
