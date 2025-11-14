import requests
import json

# URL base da API
BASE_URL = "http://localhost:8001"

def test_health():
    """Testa health check"""
    print("\n🔍 Testando health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_youtube():
    """Testa scraping do YouTube"""
    print("\n🎥 Testando YouTube scraper...")
    
    # Vídeo de exemplo com legendas (TED Talk popular)
    test_url = "https://www.youtube.com/watch?v=8jPQjjsBbIc"
    
    payload = {
        "url": test_url,
        "type": "auto"
    }
    
    response = requests.post(f"{BASE_URL}/scrape", json=payload)
    print(f"Status: {response.status_code}")
    
    data = response.json()
    if data['success']:
        print(f"✅ Sucesso!")
        print(f"Tipo: {data['type']}")
        print(f"Título: {data['data'].get('title', 'N/A')}")
        print(f"Idioma: {data['data'].get('language', 'N/A')}")
        print(f"Duração extraída: {data['data'].get('duration_scraped', 0)}s")
        print(f"Palavras: {data['data'].get('word_count', 0)}")
        print(f"Transcrição (primeiros 200 chars): {data['data'].get('transcript', '')[:200]}...")
    else:
        print(f"❌ Erro: {data.get('error')}")

def test_reddit():
    """Testa scraping do Reddit"""
    print("\n🔴 Testando Reddit scraper...")
    
    # Post popular de exemplo
    test_url = "https://www.reddit.com/r/programming/comments/1234567/example/"
    
    payload = {
        "url": test_url,
        "type": "auto",
        "max_comments": 5
    }
    
    response = requests.post(f"{BASE_URL}/scrape", json=payload)
    print(f"Status: {response.status_code}")
    
    data = response.json()
    if data['success']:
        print(f"✅ Sucesso!")
        print(f"Tipo: {data['type']}")
        print(f"Título: {data['data'].get('title', 'N/A')}")
        print(f"Subreddit: r/{data['data'].get('subreddit', 'N/A')}")
        print(f"Score: {data['data'].get('score', 0)}")
        print(f"Comentários: {len(data['data'].get('comments', []))}")
    else:
        print(f"❌ Erro: {data.get('error')}")

def test_article():
    """Testa scraping de artigo"""
    print("\n📰 Testando Article scraper...")
    
    # Artigo de exemplo
    test_url = "https://wellworthy.com/monster-enters-the-female-focused-energy-game-with-flrt/"
    
    payload = {
        "url": test_url,
        "type": "auto"
    }
    
    response = requests.post(f"{BASE_URL}/scrape", json=payload)
    print(f"Status: {response.status_code}")
    
    data = response.json()
    if data['success']:
        print(f"✅ Sucesso!")
        print(f"Tipo: {data['type']}")
        print(f"Título: {data['data'].get('title', 'N/A')}")
        print(f"Palavras: {data['data'].get('word_count', 0)}")
        print(f"Conteúdo (primeiros 200 chars): {data['data'].get('content', '')[:200]}...")
    else:
        print(f"❌ Erro: {data.get('error')}")

if __name__ == "__main__":
    print("🚀 Iniciando testes do Scraper API")
    print("=" * 50)
    
    try:
        test_health()
        test_article()
        test_youtube()
        # test_reddit()  # Descomente quando tiver uma URL válida
        
        print("\n" + "=" * 50)
        print("✅ Testes concluídos!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro: API não está rodando!")
        print("Execute primeiro: python app.py")
    except Exception as e:
        print(f"\n❌ Erro nos testes: {str(e)}")
