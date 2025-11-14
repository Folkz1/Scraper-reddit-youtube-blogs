"""
Teste manual interativo do Scraper API
Execute este arquivo para testar URLs manualmente
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_url(url: str, scrape_type: str = "auto", max_comments: int = 10):
    """Testa uma URL específica"""
    print(f"\n{'='*60}")
    print(f"🔍 Testando: {url}")
    print(f"Tipo: {scrape_type}")
    print(f"{'='*60}\n")
    
    payload = {
        "url": url,
        "type": scrape_type,
        "max_comments": max_comments
    }
    
    try:
        response = requests.post(f"{BASE_URL}/scrape", json=payload, timeout=30)
        data = response.json()
        
        if data['success']:
            print(f"✅ Sucesso! Tipo detectado: {data['type']}\n")
            
            # Mostra dados principais
            result_data = data['data']
            print(f"📌 Título: {result_data.get('title', 'N/A')}")
            print(f"📊 Palavras: {result_data.get('word_count', 0)}")
            
            # Específico por tipo
            if data['type'] == 'youtube':
                print(f"🎥 Duração extraída: {result_data.get('duration_scraped', 0)}s")
                print(f"🌍 Idioma: {result_data.get('language', 'N/A')}")
                print(f"\n📝 Transcrição (primeiros 300 chars):")
                print(result_data.get('transcript', '')[:300] + "...")
                
            elif data['type'] == 'reddit':
                print(f"🔴 Subreddit: r/{result_data.get('subreddit', 'N/A')}")
                print(f"⬆️ Score: {result_data.get('score', 0)}")
                print(f"💬 Comentários: {len(result_data.get('comments', []))}")
                
                selftext = result_data.get('selftext', '')
                if selftext:
                    print(f"\n📝 Post (primeiros 300 chars):")
                    print(selftext[:300] + "...")
                
                comments = result_data.get('comments', [])
                if comments:
                    print(f"\n💬 Top comentário:")
                    print(f"   {comments[0]['author']} ({comments[0]['score']} upvotes):")
                    print(f"   {comments[0]['body'][:200]}...")
                    
            else:  # article
                print(f"👤 Autor: {result_data.get('author', 'N/A')}")
                print(f"🌍 Idioma: {result_data.get('language', 'N/A')}")
                print(f"\n📝 Conteúdo (primeiros 300 chars):")
                print(result_data.get('content', '')[:300] + "...")
            
            # Salva resposta completa
            filename = f"test_result_{data['type']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resposta completa salva em: {filename}")
            
        else:
            print(f"❌ Erro: {data.get('error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: API não está rodando!")
        print("Execute: python app.py")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def main():
    print("🚀 Teste Manual do Scraper API")
    print("="*60)
    
    # Exemplos de URLs para testar
    examples = {
        "1": {
            "name": "Artigo Web",
            "url": "https://wellworthy.com/monster-enters-the-female-focused-energy-game-with-flrt/",
            "type": "article"
        },
        "2": {
            "name": "YouTube (TED Talk)",
            "url": "https://www.youtube.com/watch?v=8jPQjjsBbIc",
            "type": "youtube"
        },
        "3": {
            "name": "Reddit Post",
            "url": "https://www.reddit.com/r/Python/comments/1h0ixwi/what_are_you_working_on_this_week/",
            "type": "reddit"
        }
    }
    
    print("\nExemplos disponíveis:")
    for key, example in examples.items():
        print(f"{key}. {example['name']}")
    print("4. URL customizada")
    print("0. Sair")
    
    while True:
        choice = input("\nEscolha uma opção (0-4): ").strip()
        
        if choice == "0":
            print("👋 Até logo!")
            break
            
        elif choice in examples:
            example = examples[choice]
            test_url(example['url'], example['type'])
            
        elif choice == "4":
            url = input("Digite a URL: ").strip()
            if url:
                scrape_type = input("Tipo (auto/article/youtube/reddit) [auto]: ").strip() or "auto"
                test_url(url, scrape_type)
            else:
                print("❌ URL inválida")
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()
