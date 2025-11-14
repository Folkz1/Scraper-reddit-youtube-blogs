"""
Teste para verificar se Apify Proxy está funcionando
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_youtube_video():
    """Testa vídeo normal do YouTube"""
    
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"🔍 Testando vídeo YouTube: {url}\n")
    
    payload = {
        "url": url,
        "type": "auto"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/scrape", json=payload, timeout=60)
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
            print(f"📺 Canal: {result.get('channel', 'N/A')}")
            
            transcript = result.get('transcript', '')
            if transcript:
                print(f"\n📝 Transcrição (primeiros 300 chars):")
                print(transcript[:300])
                if len(transcript) > 300:
                    print("...")
            
            # Salva resultado
            with open('test_apify_result.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado salvo em: test_apify_result.json")
            
        else:
            print(f"\n❌ Erro: {data.get('error')}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    test_youtube_video()
