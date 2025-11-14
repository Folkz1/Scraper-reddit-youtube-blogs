"""
Teste direto na VPS
"""
import requests
import json

VPS_URL = "https://scrapers-reddit-youtube-blogs.7exngm.easypanel.host"

def test_youtube_short():
    """Testa YouTube Short na VPS"""
    
    url = "https://www.youtube.com/shorts/bfKu9LVqC4Q"
    
    print(f"🔍 Testando VPS: {VPS_URL}")
    print(f"📹 URL: {url}\n")
    
    payload = {
        "url": url,
        "type": "auto"
    }
    
    try:
        print("⏳ Enviando request...")
        response = requests.post(
            f"{VPS_URL}/scrape",
            json=payload,
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}\n")
        
        data = response.json()
        
        print(f"Status: {'✅ Sucesso' if data['success'] else '❌ Erro'}")
        print(f"Tipo: {data['type']}")
        
        if data['success']:
            result = data['data']
            print(f"\n📌 Título: {result.get('title', 'N/A')}")
            print(f"🎥 Video ID: {result.get('video_id', 'N/A')}")
            print(f"🌍 Idioma: {result.get('language', 'N/A')}")
            print(f"📊 Palavras: {result.get('word_count', 0)}")
            print(f"⏱️ Duração: {result.get('duration_scraped', 0)}s")
            
            transcript = result.get('transcript', '')
            if transcript:
                print(f"\n📝 Transcrição (primeiros 200 chars):")
                print(transcript[:200])
                if len(transcript) > 200:
                    print("...")
            
            print("\n✅ VPS FUNCIONANDO COM APIFY!")
        else:
            print(f"\n❌ Erro: {data.get('error')}")
            print("\n🔍 Possíveis causas:")
            print("   1. Apify token não está no .env da VPS")
            print("   2. Serviço não foi reiniciado após adicionar token")
            print("   3. Verifique os logs do container/serviço")
            
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")

if __name__ == "__main__":
    test_youtube_short()
