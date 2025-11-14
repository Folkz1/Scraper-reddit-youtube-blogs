"""
Scraper YouTube usando requests direto (sem youtube-transcript-api)
Acessa a API interna do YouTube para pegar legendas
"""
import requests
import re
from typing import Dict
from .proxy_manager import proxy_manager

def extract_video_id(url: str) -> str:
    """Extrai o ID do vídeo de uma URL do YouTube"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
        r'youtube\.com\/shorts\/([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError("URL do YouTube inválida")

async def scrape_youtube_direct(url: str, max_duration: int = 180) -> Dict:
    """
    Scrape direto da API do YouTube usando requests com proxy
    """
    video_id = extract_video_id(url)
    
    # Tenta com Apify primeiro
    attempts = []
    
    apify_residential = proxy_manager.get_apify_proxy("RESIDENTIAL")
    if apify_residential:
        attempts.append(("Apify Residential", apify_residential))
    
    apify_datacenter = proxy_manager.get_apify_proxy("DATACENTER")
    if apify_datacenter:
        attempts.append(("Apify Datacenter", apify_datacenter))
    
    # Adiciona tentativa sem proxy
    attempts.append(("Direto", None))
    
    last_error = None
    
    for attempt_num, (proxy_name, proxy_dict) in enumerate(attempts):
        try:
            print(f"🔄 Tentativa {attempt_num + 1}/{len(attempts)}: {proxy_name}")
            
            # URL da API de legendas do YouTube
            timedtext_url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang=pt&fmt=json3"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            }
            
            # Faz request com ou sem proxy
            response = requests.get(
                timedtext_url,
                headers=headers,
                proxies=proxy_dict,
                timeout=15
            )
            
            if response.status_code != 200:
                raise Exception(f"Status {response.status_code}")
            
            data = response.json()
            
            # Processa legendas
            transcript_text = []
            total_duration = 0
            
            if 'events' in data:
                for event in data['events']:
                    start_time = event.get('tStartMs', 0) / 1000
                    
                    if start_time >= max_duration:
                        break
                    
                    if 'segs' in event:
                        for seg in event['segs']:
                            text = seg.get('utf8', '').strip()
                            if text and text != '\n':
                                transcript_text.append(text)
                                total_duration = start_time
            
            full_text = ' '.join(transcript_text)
            
            if not full_text:
                raise Exception("Transcrição vazia")
            
            print(f"✅ Sucesso com: {proxy_name}")
            
            return {
                "title": f"Vídeo YouTube {video_id}",
                "video_id": video_id,
                "transcript": full_text,
                "duration_scraped": min(total_duration, max_duration),
                "language": "pt",
                "language_code": "pt",
                "is_auto_generated": True,
                "url": url,
                "word_count": len(full_text.split()),
                "channel": "Unknown",
                "duration_total": 0,
                "method": "direct_api_with_proxy"
            }
            
        except Exception as e:
            last_error = str(e)
            print(f"❌ Falhou: {last_error[:150]}")
            continue
    
    raise Exception(f"Todas as {len(attempts)} tentativas falharam. Último erro: {last_error}")
