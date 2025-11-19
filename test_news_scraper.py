"""
Teste do endpoint /scrape-news
"""

import requests
import json

# URL do microserviço (ajuste se necessário)
BASE_URL = "http://localhost:8001"

def test_rss_feed():
    """Testa com um feed RSS válido"""
    print("\n" + "="*70)
    print("🧪 TESTE 1: RSS Feed (FoodNavigator USA)")
    print("="*70)
    
    payload = {
        "url": "https://www.foodnavigator-usa.com/arc/outboundfeeds/rss/",
        "existing_links": [],
        "hours_window": 24,
        "max_summary_length": 200
    }
    
    response = requests.post(f"{BASE_URL}/scrape-news", json=payload)
    result = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Success: {result['success']}")
    
    if result['success']:
        data = result['data']
        print(f"Source Type: {data['source_type']}")
        print(f"Total Found: {data['total_found']}")
        print(f"Total Unique: {data['total_unique']}")
        print(f"\n📰 Primeiras 3 notícias:")
        for i, news in enumerate(data['news_list'][:3], 1):
            print(f"\n{i}. {news['title']}")
            print(f"   URL: {news['url']}")
            print(f"   Summary: {news['summary'][:100]}...")
            print(f"   Date: {news['pubDate']}")
    else:
        print(f"Error: {result.get('error')}")

def test_html_scraping():
    """Testa com um site sem RSS (fallback HTML)"""
    print("\n" + "="*70)
    print("🧪 TESTE 2: HTML Scraping (Nutrition UK)")
    print("="*70)
    
    payload = {
        "url": "https://www.nutrition.org.uk/news",
        "existing_links": [],
        "hours_window": 72,  # 3 dias para ter mais chances
        "max_summary_length": 200
    }
    
    response = requests.post(f"{BASE_URL}/scrape-news", json=payload)
    result = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Success: {result['success']}")
    
    if result['success']:
        data = result['data']
        print(f"Source Type: {data['source_type']}")
        print(f"Total Found: {data['total_found']}")
        print(f"Total Unique: {data['total_unique']}")
        print(f"\n📰 Primeiras 3 notícias:")
        for i, news in enumerate(data['news_list'][:3], 1):
            print(f"\n{i}. {news['title']}")
            print(f"   URL: {news['url']}")
            print(f"   Summary: {news['summary'][:100]}...")
    else:
        print(f"Error: {result.get('error')}")

def test_with_existing_links():
    """Testa filtro de links existentes"""
    print("\n" + "="*70)
    print("🧪 TESTE 3: Com Links Existentes (Lifespan.io)")
    print("="*70)
    
    # Primeiro busca sem filtro
    payload1 = {
        "url": "https://lifespan.io/feed",
        "existing_links": [],
        "hours_window": 168  # 7 dias
    }
    
    response1 = requests.post(f"{BASE_URL}/scrape-news", json=payload1)
    result1 = response1.json()
    
    if result1['success']:
        first_batch = result1['data']['news_list']
        print(f"Primeira busca: {len(first_batch)} notícias")
        
        # Pega os primeiros 5 links
        existing = [news['url'] for news in first_batch[:5]]
        print(f"Marcando {len(existing)} como já processadas")
        
        # Busca novamente com links existentes
        payload2 = {
            "url": "https://lifespan.io/feed",
            "existing_links": existing,
            "hours_window": 168
        }
        
        response2 = requests.post(f"{BASE_URL}/scrape-news", json=payload2)
        result2 = response2.json()
        
        if result2['success']:
            second_batch = result2['data']['news_list']
            print(f"Segunda busca: {len(second_batch)} notícias (deve ser {len(first_batch) - len(existing)})")
            print(f"✅ Filtro funcionando: {len(second_batch) == len(first_batch) - len(existing)}")

def test_all_feeds_from_db():
    """Testa alguns feeds que estão no banco"""
    print("\n" + "="*70)
    print("🧪 TESTE 4: Feeds do Banco de Dados")
    print("="*70)
    
    feeds_to_test = [
        "https://fitfeed.com.br/feed",
        "https://saude.abril.com.br/feed",
        "https://www.tuasaude.com/feed/",
        "https://lifespan.io/feed"
    ]
    
    for feed_url in feeds_to_test:
        print(f"\n📡 Testando: {feed_url}")
        
        payload = {
            "url": feed_url,
            "hours_window": 24
        }
        
        try:
            response = requests.post(f"{BASE_URL}/scrape-news", json=payload, timeout=10)
            result = response.json()
            
            if result['success']:
                data = result['data']
                print(f"   ✅ {data['total_unique']} notícias ({data['source_type']})")
            else:
                print(f"   ❌ Erro: {result.get('error')}")
        except Exception as e:
            print(f"   ❌ Exceção: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DO ENDPOINT /scrape-news")
    print("Certifique-se de que o microserviço está rodando em http://localhost:8001")
    
    try:
        # Verifica se o serviço está rodando
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Microserviço está rodando\n")
            
            test_rss_feed()
            test_html_scraping()
            test_with_existing_links()
            test_all_feeds_from_db()
            
            print("\n" + "="*70)
            print("✅ TESTES CONCLUÍDOS")
            print("="*70)
        else:
            print("❌ Microserviço não está respondendo corretamente")
    
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao microserviço")
        print("   Execute: python app.py")
