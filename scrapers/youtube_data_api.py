"""
YouTube Data API v3 - Para metadados de vídeos
Complementa o scraper de transcrições com dados públicos
"""
import requests
import os
from typing import Dict, Optional

def get_video_metadata(video_id: str) -> Optional[Dict]:
    """
    Busca metadados públicos de um vídeo usando YouTube Data API v3
    
    Args:
        video_id: ID do vídeo (ex: 'bfKu9LVqC4Q')
    
    Returns:
        Dict com metadados ou None se falhar
    """
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        return None
    
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        
        params = {
            'part': 'snippet,statistics,contentDetails',
            'id': video_id,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('items'):
            return None
        
        item = data['items'][0]
        snippet = item.get('snippet', {})
        statistics = item.get('statistics', {})
        content_details = item.get('contentDetails', {})
        
        # Processa duração (formato ISO 8601: PT1M30S = 1min 30s)
        duration_iso = content_details.get('duration', 'PT0S')
        duration_seconds = parse_iso_duration(duration_iso)
        
        return {
            'title': snippet.get('title'),
            'description': snippet.get('description'),
            'channel_title': snippet.get('channelTitle'),
            'channel_id': snippet.get('channelId'),
            'published_at': snippet.get('publishedAt'),
            'tags': snippet.get('tags', []),
            'category_id': snippet.get('categoryId'),
            'thumbnails': snippet.get('thumbnails', {}),
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
            'duration_seconds': duration_seconds,
            'duration_iso': duration_iso,
        }
        
    except Exception as e:
        # Falha silenciosa - não quebra o scraper principal
        return None

def parse_iso_duration(duration: str) -> int:
    """
    Converte duração ISO 8601 para segundos
    Exemplo: PT1M30S = 90 segundos
    """
    import re
    
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)
    
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

def get_channel_info(channel_id: str) -> Optional[Dict]:
    """
    Busca informações de um canal
    
    Args:
        channel_id: ID do canal
    
    Returns:
        Dict com dados do canal ou None
    """
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        return None
    
    try:
        url = "https://www.googleapis.com/youtube/v3/channels"
        
        params = {
            'part': 'snippet,statistics',
            'id': channel_id,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('items'):
            return None
        
        item = data['items'][0]
        snippet = item.get('snippet', {})
        statistics = item.get('statistics', {})
        
        return {
            'title': snippet.get('title'),
            'description': snippet.get('description'),
            'custom_url': snippet.get('customUrl'),
            'published_at': snippet.get('publishedAt'),
            'thumbnails': snippet.get('thumbnails', {}),
            'subscriber_count': int(statistics.get('subscriberCount', 0)),
            'video_count': int(statistics.get('videoCount', 0)),
            'view_count': int(statistics.get('viewCount', 0)),
        }
        
    except Exception as e:
        return None
