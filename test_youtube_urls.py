"""
Teste específico das URLs do YouTube fornecidas
"""
import requests
import json

BASE_URL = "http://localhost:8001"

test_urls = [
    {
        "name": "YouTube Short - Cariani",
        "url": "https://www.youtube.com/shorts/bfKu9LVqC4Q"
    },
    {
        "name": "YouTube Video - Falso Magro",
        "url": "https://www.youtube.com/watch?v=xfVzboWfZvM"
    }
]

print("🧪 Testando URLs do YouTube")
print("=" * 60)

for test in test_urls:
    print(f"\n📹 {test['name']}")
    print(f"URL: {test['url']}")
    print("-" * 60)
    
    payload = {
        "url": test['url'],
        "type": "youtube"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/scrape",
            json=payload,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        
        data = response.json()
        
        if data['success']:
            print(f"✅ Sucesso!")
            print(f"\nTítulo: {data['data'].get('title', 'N/A')}")
            print(f"Video ID: {data['data'].get('video_id', 'N/A')}")
            print(f"Idioma: {data['data'].get('language', 'N/A')} ({data['data'].get('language_code', 'N/A')})")
            print(f"Duração extraída: {data['data'].get('duration_scraped', 0)}s")
            print(f"Palavras: {data['data'].get('word_count', 0)}")
            print(f"Auto-gerado: {data['data'].get('is_auto_generated', 'N/A')}")
            
            transcript = data['data'].get('transcript', '')
            if transcript:
                print(f"\n📝 Transcrição (primeiros 300 chars):")
                print(transcript[:300] + "...")
            else:
                print(f"\n⚠️  Transcrição vazia!")
                
        else:
            print(f"❌ Erro: {data.get('error')}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")
    
    print()

print("=" * 60)
print("Teste concluído!")
