import yt_dlp
import re
from typing import Dict
import os

# Importa scraper alternativo
try:
    from .youtube_scraper_api import scrape_youtube_with_api
    HAS_API_SCRAPER = True
    print("✅ youtube_scraper_api importado com sucesso")
except ImportError as e:
    HAS_API_SCRAPER = False
    print(f"⚠️ Não foi possível importar youtube_scraper_api: {e}")
except Exception as e:
    HAS_API_SCRAPER = False
    print(f"❌ Erro ao importar youtube_scraper_api: {e}")

def extract_video_id(url: str) -> str:
    """Extrai o ID do vídeo de uma URL do YouTube"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
        r'youtube\.com\/shorts\/([^&\n?#]+)',  # Suporte a Shorts
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError("URL do YouTube inválida")

async def scrape_youtube(url: str, max_duration: int = 180) -> Dict:
    """
    Scrape de transcrição do YouTube
    Tenta API primeiro (mais confiável em VPS), fallback para yt-dlp
    max_duration: duração máxima em segundos (padrão: 180 = 3 minutos)
    """
    
    # Tenta API com proxies primeiro (melhor para VPS)
    if HAS_API_SCRAPER:
        try:
            print("=" * 60)
            print("🎯 Iniciando youtube-transcript-api com proxies")
            print("=" * 60)
            result = await scrape_youtube_with_api(url, max_duration)
            print("=" * 60)
            print("✅ youtube-transcript-api SUCESSO!")
            print("=" * 60)
            return result
        except Exception as api_error:
            # Se API falhar, tenta yt-dlp
            print("=" * 60)
            print(f"⚠️ youtube-transcript-api FALHOU: {str(api_error)[:200]}")
            print("🔄 Tentando yt-dlp como fallback...")
            print("=" * 60)
    
    # Fallback: yt-dlp (pode ser bloqueado em VPS)
    try:
        # Extrai ID do vídeo
        video_id = extract_video_id(url)
        
        # Configuração do yt-dlp com headers para parecer navegador real
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['pt', 'pt-BR', 'en'],
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'extractor_retries': 3,
            # Headers para parecer navegador real
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            # Cookies (opcional - pode ajudar)
            'cookiefile': None,
            'nocheckcertificate': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extrai informações do vídeo
            info = ydl.extract_info(url, download=False)
            
            if not info:
                raise Exception("Não foi possível obter informações do vídeo")
            
            # Pega legendas disponíveis
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            
            # Prioriza legendas manuais, depois automáticas
            all_subs = {**automatic_captions, **subtitles}
            
            if not all_subs:
                raise Exception("Este vídeo não possui legendas disponíveis")
            
            # Escolhe idioma (pt-BR > pt > en > primeiro disponível)
            chosen_lang = None
            for lang in ['pt-BR', 'pt', 'en']:
                if lang in all_subs:
                    chosen_lang = lang
                    break
            
            if not chosen_lang:
                chosen_lang = list(all_subs.keys())[0]
            
            # Pega a legenda no formato JSON
            subtitle_data = all_subs[chosen_lang]
            
            # Procura formato JSON3
            subtitle_url = None
            for fmt in subtitle_data:
                if fmt.get('ext') == 'json3':
                    subtitle_url = fmt.get('url')
                    break
            
            if not subtitle_url:
                # Fallback para qualquer formato
                subtitle_url = subtitle_data[0].get('url')
            
            if not subtitle_url:
                raise Exception("Não foi possível obter URL das legendas")
            
            # Baixa as legendas
            import requests
            response = requests.get(subtitle_url, timeout=15)
            response.raise_for_status()
            subtitle_json = response.json()
            
            # Processa legendas (formato JSON3 do YouTube)
            transcript_text = []
            total_duration = 0
            
            if 'events' in subtitle_json:
                for event in subtitle_json['events']:
                    start_time = event.get('tStartMs', 0) / 1000  # Converte para segundos
                    
                    if start_time >= max_duration:
                        break
                    
                    if 'segs' in event:
                        for seg in event['segs']:
                            text = seg.get('utf8', '').strip()
                            if text and text != '\n':
                                transcript_text.append(text)
                                total_duration = start_time
            
            # Junta o texto
            full_text = ' '.join(transcript_text)
            
            # Metadados
            return {
                "title": info.get('title', f'Vídeo YouTube {video_id}'),
                "video_id": video_id,
                "transcript": full_text,
                "duration_scraped": min(total_duration, max_duration),
                "language": chosen_lang,
                "language_code": chosen_lang,
                "is_auto_generated": chosen_lang in automatic_captions,
                "url": url,
                "word_count": len(full_text.split()),
                "channel": info.get('channel', 'Unknown'),
                "duration_total": info.get('duration', 0)
            }
    
    except Exception as e:
        raise Exception(f"Erro ao buscar transcrição do YouTube: {str(e)}")
