"""
Script de diagnóstico para VPS
Verifica se tudo está configurado corretamente
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("🔍 DIAGNÓSTICO DO SCRAPER NA VPS")
print("=" * 60)

# Carrega .env
load_dotenv()

print("\n1️⃣ Verificando variáveis de ambiente:")
print("-" * 60)

# Apify
apify_token = os.getenv('APIFY_API_TOKEN')
if apify_token:
    print(f"✅ APIFY_API_TOKEN: {apify_token[:20]}...{apify_token[-10:]}")
else:
    print("❌ APIFY_API_TOKEN: NÃO CONFIGURADO")
    print("   Configure no .env: APIFY_API_TOKEN=seu_token")

# Reddit
reddit_id = os.getenv('REDDIT_CLIENT_ID')
reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
if reddit_id and reddit_secret:
    print(f"✅ REDDIT: Configurado")
else:
    print("⚠️ REDDIT: Não configurado (opcional)")

# Google
google_key = os.getenv('GOOGLE_API_KEY')
google_cx = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
if google_key and google_cx:
    print(f"✅ GOOGLE: Configurado")
else:
    print("⚠️ GOOGLE: Não configurado (opcional)")

print("\n2️⃣ Verificando bibliotecas:")
print("-" * 60)

try:
    import youtube_transcript_api
    print(f"✅ youtube-transcript-api: {youtube_transcript_api.__version__}")
except ImportError:
    print("❌ youtube-transcript-api: NÃO INSTALADO")
    print("   Execute: pip install youtube-transcript-api")

try:
    import yt_dlp
    print(f"✅ yt-dlp: Instalado")
except ImportError:
    print("❌ yt-dlp: NÃO INSTALADO")

try:
    import requests
    print(f"✅ requests: {requests.__version__}")
except ImportError:
    print("❌ requests: NÃO INSTALADO")

print("\n3️⃣ Testando Apify Proxy:")
print("-" * 60)

if apify_token:
    try:
        import requests
        
        # Testa proxy Apify
        proxy_url = f"http://groups-RESIDENTIAL:{apify_token}@proxy.apify.com:8000"
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        print("🔄 Testando conexão com Apify Residential...")
        response = requests.get(
            'https://api.ipify.org?format=json',
            proxies=proxies,
            timeout=15
        )
        
        if response.status_code == 200:
            ip_data = response.json()
            print(f"✅ Apify Proxy FUNCIONANDO!")
            print(f"   IP usado: {ip_data.get('ip')}")
        else:
            print(f"❌ Apify retornou status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar Apify: {str(e)}")
else:
    print("⏭️ Pulando teste (token não configurado)")

print("\n4️⃣ Testando YouTube Transcript API:")
print("-" * 60)

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    
    print("🔄 Testando busca de transcrição...")
    video_id = "dQw4w9WgXcQ"  # Rick Roll
    
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    print(f"✅ YouTube Transcript API funcionando!")
    print(f"   Legendas disponíveis para vídeo {video_id}")
    
except Exception as e:
    print(f"❌ Erro: {str(e)}")

print("\n" + "=" * 60)
print("📋 RESUMO:")
print("=" * 60)

if apify_token:
    print("✅ Sistema configurado com Apify Proxy")
    print("   YouTube deve funcionar na VPS!")
else:
    print("❌ Apify não configurado")
    print("   Adicione no .env:")
    print("   APIFY_API_TOKEN=seu_token_do_apify")

print("\n💡 Para aplicar mudanças no .env:")
print("   1. Edite o arquivo .env")
print("   2. Adicione: APIFY_API_TOKEN=seu_token_aqui")
print("   3. Reinicie o serviço: systemctl restart scraper-api")
print("   4. Ou: docker-compose restart")
print("=" * 60)
