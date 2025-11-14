"""Teste direto do YouTube scraper"""
from youtube_transcript_api import YouTubeTranscriptApi

# Vídeos de teste conhecidos com legendas
test_videos = [
    "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up (tem legendas)
    "9bZkp7q19f0",  # Gangnam Style (tem legendas)
    "kJQP7kiw5Fk",  # Luis Fonsi - Despacito (tem legendas)
]

print("🧪 Testando youtube-transcript-api diretamente...\n")

for video_id in test_videos:
    try:
        print(f"📹 Testando vídeo: {video_id}")
        
        # Lista transcrições disponíveis
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        print(f"  ✅ Transcrições disponíveis:")
        for t in transcript_list:
            print(f"     - {t.language} ({t.language_code}) - Auto: {t.is_generated}")
        
        # Tenta pegar uma transcrição
        transcript = transcript_list.find_transcript(['en', 'pt', 'pt-BR'])
        data = transcript.fetch()
        
        print(f"  ✅ Conseguiu buscar {len(data)} snippets")
        print(f"  📝 Primeiros 100 chars: {data[0]['text'][:100] if data else 'vazio'}")
        print()
        
        # Se chegou aqui, funcionou!
        print("✅ YouTube scraper está funcionando!\n")
        break
        
    except Exception as e:
        print(f"  ❌ Erro: {str(e)}\n")
        continue

print("\n🧪 Agora testando via API...")
import requests

try:
    response = requests.post(
        "http://localhost:8001/scrape",
        json={"url": f"https://www.youtube.com/watch?v={test_videos[0]}"}
    )
    
    data = response.json()
    if data['success']:
        print("✅ API funcionando!")
        print(f"Tipo: {data['type']}")
        print(f"Palavras: {data['data'].get('word_count', 0)}")
        print(f"Transcrição: {data['data'].get('transcript', '')[:200]}...")
    else:
        print(f"❌ Erro na API: {data.get('error')}")
        
except Exception as e:
    print(f"❌ Erro ao chamar API: {str(e)}")
