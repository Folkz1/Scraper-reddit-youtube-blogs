import requests
import json
from dotenv import load_dotenv

load_dotenv()

# URL base da API
BASE_URL = "http://localhost:8001"

def test_reddit():
    """Testa scraping do Reddit"""
    print("\n🔴 Testando Reddit scraper...")
    
    # Post popular de exemplo (r/Python - post fixo do subreddit)
    # Este é um post real e popular
    test_url = "https://www.reddit.com/r/Python/comments/1h0ixwi/what_are_you_working_on_this_week/"
    
    payload = {
        "url": test_url,
        "type": "auto",
        "max_comments": 5,
        "sort_comments": "top"
    }
    
    print(f"URL: {test_url}")
    print(f"Buscando top {payload['max_comments']} comentários...")
    
    response = requests.post(f"{BASE_URL}/scrape", json=payload)
    print(f"\nStatus: {response.status_code}")
    
    data = response.json()
    
    if data['success']:
        print(f"✅ Sucesso!")
        print(f"\nTipo: {data['type']}")
        print(f"Título: {data['data'].get('title', 'N/A')}")
        print(f"Subreddit: r/{data['data'].get('subreddit', 'N/A')}")
        print(f"Autor: {data['data'].get('author', 'N/A')}")
        print(f"Score: {data['data'].get('score', 0)} upvotes")
        print(f"Total de comentários: {data['data'].get('num_comments', 0)}")
        print(f"Comentários extraídos: {len(data['data'].get('comments', []))}")
        print(f"Palavras totais: {data['data'].get('word_count', 0)}")
        
        # Mostra conteúdo do post
        selftext = data['data'].get('selftext', '')
        if selftext:
            print(f"\n📝 Conteúdo do post (primeiros 200 chars):")
            print(f"{selftext[:200]}...")
        
        # Mostra alguns comentários
        comments = data['data'].get('comments', [])
        if comments:
            print(f"\n💬 Top comentários:")
            for i, comment in enumerate(comments[:3], 1):
                print(f"\n{i}. {comment['author']} ({comment['score']} upvotes):")
                print(f"   {comment['body'][:150]}...")
        
        # Salva resposta completa para debug
        with open('microservico_scraper/test_reddit_response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resposta completa salva em: test_reddit_response.json")
        
    else:
        print(f"❌ Erro: {data.get('error')}")
        print(f"\nDetalhes: {json.dumps(data, indent=2)}")

if __name__ == "__main__":
    print("🚀 Teste do Reddit Scraper")
    print("=" * 50)
    
    try:
        test_reddit()
        print("\n" + "=" * 50)
        print("✅ Teste concluído!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro: API não está rodando!")
        print("Execute primeiro: python app.py")
    except Exception as e:
        print(f"\n❌ Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()
