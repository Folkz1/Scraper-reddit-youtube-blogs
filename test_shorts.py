"""
Teste específico para YouTube Shorts
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_shorts():
    """Testa URL de YouTube Shorts"""
    
    # URL do Short que você testou
    url = "https://www.youtube.com/shorts/bfKu9LVqC4Q"
    
    print(f"🔍 Testando YouTube Short: {url}\n")
    
    payload = {
        "url": url,
        "type": "auto"  # Deixa detectar automaticamente
    }
    
    try:
        response = requests.post(f"{BASE_URL}/scrape", json=payload, timeout=30)
        data = response.json()
        
        print(f"Status: {'✅ Sucesso' if data['success'] else '❌ Erro'}")
        print(f"Tipo detectado: {data['type']}")
        
        if data['success']:
            result = data['data']
            print(f"\n📌 Título: {result.get('title', 'N/A')}")
            print(f"🎥 Video ID: {result.get('video_id', 'N/A')}")
            print(f"🌍 Idioma: {result.get('language', 'N/A')}")
            print(f"📊 Palavras: {result.get('word_count', 0)}")
            print(f"⏱️ Duração: {result.get('duration_scraped', 0)}s")
            
            transcript = result.get('transcript', '')
            if transcript:
                print(f"\n📝 Transcrição (primeiros 500 chars):")
                print(transcript[:500])
                if len(transcript) > 500:
                    print("...")
            else:
                print("\n⚠️ Sem transcrição disponível")
            
            # Salva resultado completo
            with open('test_shorts_result.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado completo salvo em: test_shorts_result.json")
            
        else:
            print(f"\n❌ Erro: {data.get('error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: API não está rodando!")
        print("Execute: python app.py")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    test_shorts()
