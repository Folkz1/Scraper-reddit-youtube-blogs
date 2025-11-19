"""
News Scraper - RSS Feed + Fallback para Scraping de Blog
Tenta ler RSS feed, se falhar faz scraping do HTML do blog
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin, urlparse


def normalize_url(url: str) -> str:
    """Normaliza URL para comparação (lowercase, sem query params, sem trailing slash)"""
    if not url or not isinstance(url, str):
        return ''
    try:
        url = url.strip().lower()
        url = url.split('?')[0]  # Remove query params
        if url.endswith('/'):
            url = url[:-1]
        return url
    except:
        return str(url).strip().lower()


def strip_html(html: str) -> str:
    """Remove tags HTML e limpa texto"""
    if not html:
        return ''
    text = str(html)
    text = re.sub(r'<[^>]+>', '', text)  # Remove tags
    text = text.replace('&nbsp;', ' ').replace('&#160;', ' ')
    text = re.sub(r'\s+', ' ', text)  # Normaliza espaços
    return text.strip()


def try_parse_date(date_str: str) -> Optional[datetime]:
    """Tenta fazer parse de várias formatações de data"""
    if not date_str:
        return None
    
    try:
        # feedparser já retorna struct_time
        if hasattr(date_str, 'tm_year'):
            return datetime(*date_str[:6])
        
        # ISO format
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        pass
    
    try:
        # RFC 2822 format (comum em RSS)
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except:
        pass
    
    return None


def extract_from_rss(url: str, hours_window: int = 24) -> List[Dict]:
    """
    Extrai notícias de RSS feed
    """
    try:
        feed = feedparser.parse(url)
        
        if not feed.entries:
            return []
        
        window_ago = datetime.now() - timedelta(hours=hours_window)
        news_list = []
        
        for entry in feed.entries:
            # Extrai campos com fallbacks
            title = entry.get('title', '')
            link = entry.get('link', entry.get('id', ''))
            
            # Summary com múltiplos fallbacks
            summary = (
                entry.get('summary', '') or 
                entry.get('description', '') or 
                entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
            )
            summary = strip_html(summary)
            
            # Data de publicação
            pub_date_raw = (
                entry.get('published_parsed') or 
                entry.get('updated_parsed') or
                entry.get('published') or
                entry.get('updated')
            )
            
            # Fonte/Autor
            source = (
                entry.get('author', '') or
                entry.get('dc_creator', '') or
                feed.feed.get('title', 'Unknown')
            )
            
            # Parse data
            pub_date = try_parse_date(pub_date_raw) if pub_date_raw else None
            
            # Filtra por janela de tempo
            if pub_date and pub_date < window_ago:
                continue
            
            news_list.append({
                'title': title.strip(),
                'url': link.strip(),
                'summary': summary[:500].strip() + ('...' if len(summary) > 500 else ''),
                'pubDate': pub_date.isoformat() if pub_date else '',
                'source': source.strip()
            })
        
        return news_list
    
    except Exception as e:
        print(f"Erro ao extrair RSS: {e}")
        return []


def extract_from_blog_html(url: str, hours_window: int = 24) -> List[Dict]:
    """
    Fallback: Faz scraping do HTML do blog quando RSS não está disponível
    Tenta identificar posts de blog automaticamente
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        news_list = []
        window_ago = datetime.now() - timedelta(hours=hours_window)
        
        # Estratégia 1: Procura por <article> tags (comum em blogs modernos)
        articles = soup.find_all('article')
        
        # Estratégia 2: Se não achar articles, procura por divs com classes comuns
        if not articles:
            articles = soup.find_all(['div'], class_=re.compile(
                r'post|article|entry|blog-post|news-item|card',
                re.IGNORECASE
            ))
        
        for article in articles[:20]:  # Limita a 20 posts
            try:
                # Extrai título
                title_tag = (
                    article.find(['h1', 'h2', 'h3'], class_=re.compile(r'title|heading|headline', re.IGNORECASE)) or
                    article.find(['h1', 'h2', 'h3']) or
                    article.find('a', class_=re.compile(r'title', re.IGNORECASE))
                )
                
                if not title_tag:
                    continue
                
                title = title_tag.get_text(strip=True)
                
                # Extrai link
                link_tag = title_tag.find('a') if title_tag.name != 'a' else title_tag
                if not link_tag:
                    link_tag = article.find('a', href=True)
                
                if not link_tag or not link_tag.get('href'):
                    continue
                
                link = urljoin(base_url, link_tag['href'])
                
                # Extrai resumo/excerpt
                summary_tag = (
                    article.find(class_=re.compile(r'excerpt|summary|description|content', re.IGNORECASE)) or
                    article.find('p')
                )
                summary = summary_tag.get_text(strip=True) if summary_tag else ''
                summary = summary[:500] + ('...' if len(summary) > 500 else '')
                
                # Extrai data (tenta vários formatos)
                date_tag = article.find(['time', 'span', 'div'], class_=re.compile(r'date|time|published', re.IGNORECASE))
                pub_date = None
                
                if date_tag:
                    date_str = date_tag.get('datetime') or date_tag.get_text(strip=True)
                    pub_date = try_parse_date(date_str)
                
                # Se não encontrou data, assume que é recente (dentro das 24h)
                # Isso é importante para blogs que não mostram data
                if not pub_date:
                    pub_date = datetime.now()
                
                # Filtra por janela de tempo
                if pub_date < window_ago:
                    continue
                
                news_list.append({
                    'title': title,
                    'url': link,
                    'summary': summary,
                    'pubDate': pub_date.isoformat() if pub_date else '',
                    'source': urlparse(url).netloc
                })
            
            except Exception as e:
                print(f"Erro ao processar artigo: {e}")
                continue
        
        return news_list
    
    except Exception as e:
        print(f"Erro ao fazer scraping do blog: {e}")
        return []


async def scrape_news(
    url: str,
    existing_links: List[str] = None,
    hours_window: int = 24,
    max_summary_length: int = 500
) -> Dict:
    """
    Scraper principal de notícias
    
    1. Tenta ler RSS feed
    2. Se falhar, faz scraping do HTML
    3. Filtra por janela de tempo (padrão 24h)
    4. Remove duplicatas baseado em links existentes
    5. Retorna lista normalizada
    
    Args:
        url: URL do RSS feed ou blog
        existing_links: Lista de URLs já processadas (para evitar duplicatas)
        hours_window: Janela de tempo em horas (padrão 24h)
        max_summary_length: Tamanho máximo do resumo
    
    Returns:
        Dict com news_list e metadados
    """
    existing_links = existing_links or []
    existing_set = {normalize_url(link) for link in existing_links}
    
    # Tenta RSS primeiro
    news_list = extract_from_rss(url, hours_window)
    source_type = 'rss'
    
    # Fallback para scraping se RSS falhar
    if not news_list:
        news_list = extract_from_blog_html(url, hours_window)
        source_type = 'html_scraping'
    
    # Remove duplicatas (internas e com existing_links)
    unique_news = []
    seen = set()
    
    for news in news_list:
        normalized = normalize_url(news['url'])
        
        # Pula se já existe ou se já vimos
        if normalized in existing_set or normalized in seen:
            continue
        
        seen.add(normalized)
        
        # Limita tamanho do summary
        if len(news['summary']) > max_summary_length:
            news['summary'] = news['summary'][:max_summary_length].strip() + '...'
        
        unique_news.append(news)
    
    return {
        'news_list': unique_news,
        'total_found': len(news_list),
        'total_unique': len(unique_news),
        'source_type': source_type,
        'hours_window': hours_window,
        'url': url
    }
