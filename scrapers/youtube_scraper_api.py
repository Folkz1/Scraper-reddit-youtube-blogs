"""
Scraper alternativo usando YouTube Transcript API com suporte a proxies
"""
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re
from typing import Dict
import os
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

async def scrape_youtube_with_api(url: str, max_duration: int = 180) -> Dict:
    """
    Scrape usando YouTube Transcript API com proxies
    Prioridade: Apify Residential > Apify Datacenter > Proxies Gratuitos > Direto
    """
    video_id = extract_video_id(url)
    
    attempts = []
    
    # 1. Tenta com Apify Residential (melhor para YouTube)
    apify_residential = proxy_manager.get_apify_proxy("RESIDENTIAL")
    if apify_residential:
        print("✅ Apify Residential proxy configurado")
        attempts.append(("Apify Residential", apify_residential))
    else:
        print("⚠️ Apify token não encontrado - configure APIFY_API_TOKEN no .env")
    
    # 2. Tenta com Apify Datacenter (mais barato)
    apify_datacenter = proxy_manager.get_apify_proxy("DATACENTER")
    if apify_datacenter:
        print("✅ Apify Datacenter proxy configurado")
        attempts.append(("Apify Datacenter", apify_datacenter))
    
    # 3. Adiciona 3 proxies gratuitos
    for _ in range(3):
        proxy = proxy_manager.get_random_proxy()
        if proxy:
            attempts.append(("Proxy Gratuito", proxy))
    
    # 4. Tenta sem proxy (direto)
    attempts.append(("Direto (sem proxy)", None))
    
    print(f"📊 Total de {len(attempts)} tentativas configuradas")
    
    last_error = None
    
    for attempt_num, (proxy_name, proxy_dict) in enumerate(attempts):
        try:
            print(f"🔄 Tentativa {attempt_num + 1}/{len(attempts)}: {proxy_name}")
            
            # Configura proxy se disponível
            if proxy_dict:
                # Monkey patch para adicionar proxy ao youtube_transcript_api
                import requests
                original_get = requests.get
                
                def get_with_proxy(*args, **kwargs):
                    kwargs['proxies'] = proxy_dict
                    kwargs['timeout'] = 10
                    return original_get(*args, **kwargs)
                
                requests.get = get_with_proxy
            
            # Tenta pegar transcrição
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Restaura requests.get original
            if proxy_dict:
                requests.get = original_get
            
            # Prioriza legendas manuais em português
            try:
                transcript = transcript_list.find_manually_created_transcript(['pt', 'pt-BR'])
                is_auto = False
            except:
                # Fallback para legendas automáticas em português
                try:
                    transcript = transcript_list.find_generated_transcript(['pt', 'pt-BR'])
                    is_auto = True
                except:
                    # Fallback para inglês
                    try:
                        transcript = transcript_list.find_transcript(['en'])
                        is_auto = transcript.is_generated
                    except:
                        # Pega qualquer legenda disponível
                        available = list(transcript_list._manually_created_transcripts.keys()) or list(transcript_list._generated_transcripts.keys())
                        if available:
                            transcript = transcript_list.find_transcript([available[0]])
                            is_auto = transcript.is_generated
                        else:
                            raise NoTranscriptFound(video_id, [], None)
            
            # Pega os dados da transcrição
            transcript_data = transcript.fetch()
            
            # Processa transcrição limitando pela duração
            transcript_text = []
            total_duration = 0
            
            for entry in transcript_data:
                start_time = entry['start']
                
                if start_time >= max_duration:
                    break
                
                text = entry['text'].strip()
                if text:
                    transcript_text.append(text)
                    total_duration = start_time + entry.get('duration', 0)
            
            full_text = ' '.join(transcript_text)
            
            print(f"✅ Sucesso com: {proxy_name}")
            
            # Busca metadados básicos
            return {
                "title": f"Vídeo YouTube {video_id}",
                "video_id": video_id,
                "transcript": full_text,
                "duration_scraped": min(total_duration, max_duration),
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_auto_generated": is_auto,
                "url": url,
                "word_count": len(full_text.split()),
                "channel": "Unknown",
                "duration_total": 0,
                "method": "youtube_transcript_api_with_proxy"
            }
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            # Erros que não adianta tentar com outro proxy
            raise Exception(f"Este vídeo não possui legendas disponíveis: {str(e)}")
        
        except Exception as e:
            last_error = str(e)
            print(f"❌ Falhou: {last_error[:100]}")
            
            # Restaura requests.get se necessário
            if proxy_dict and 'original_get' in locals():
                import requests
                requests.get = original_get
            
            # Continua para próximo proxy
            continue
    
    # Se chegou aqui, todas as tentativas falharam
    raise Exception(f"Todas as tentativas falharam. Último erro: {last_error}")
