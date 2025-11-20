"""
Script para descobrir e validar RSS feeds de sites
Suporta: Blogs, Reddit, YouTube
"""

import requests
from bs4 import BeautifulSoup
import feedparser
import json
from urllib.parse import urljoin, urlparse
import urllib3
import re

# Desabilita warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Sites para testar
SITES_TO_TEST = [
    "https://www.nutrition.org.uk/news",
    "https://www.mobihealthnews.com/tag/south-korea",
    "https://www.medicalkorea.or.kr/en/latestnews",
    "https://www.chinadaily.com.cn/life/health",
    "https://www.lifespan.io/news/category/life-extension-news/",
    "https://www.bluezones.com/recipes/",
    "https://www.new-nutrition.com/",
    "https://www.foodnavigator-latam.com/News/",
    "https://www.foodnavigator-usa.com/News/",
    "https://www.nutraingredients.com/Latin-America/",
    "https://www.nutritioninsight.com/news.html"
]

def detect_url_type(url):
    """Detecta o tipo de URL (reddit, youtube, blog)"""
    url_lower = url.lower()
    
    if 'reddit.com/r/' in url_lower:
        return 'reddit'
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    else:
        return 'blog'

def get_reddit_rss(url):
    """
    Converte URL do Reddit em RSS feed
    Exemplos:
    - https://www.reddit.com/r/Maromba/ -> https://www.reddit.com/r/Maromba/.rss
    - https://reddit.com/r/fitness -> https://reddit.com/r/fitness/.rss
    """
    # Remove trailing slash se existir
    url = url.rstrip('/')
    
    # Adiciona .rss no final
    rss_url = f"{url}/.rss"
    
    # Extrai nome do subreddit
    match = re.search(r'/r/([^/]+)', url)
    subreddit_name = match.group(1) if match else 'Unknown'
    
    return {
        "url": rss_url,
        "title": f"r/{subreddit_name}",
        "type": "reddit"
    }

def get_youtube_rss(url):
    """
    Converte URL/nome do YouTube em RSS feed
    Suporta:
    - URL do canal: https://www.youtube.com/@Gorgonoid
    - Nome do canal: Gorgonoid
    - Channel ID: UCLfCo17TCjx7qf-JMhQioLQ
    """
    # Se for apenas um nome (sem http), busca o channel ID
    if not url.startswith('http'):
        # Assume que é nome do canal
        channel_name = url.strip()
        # Tenta buscar o canal
        search_url = f"https://www.youtube.com/results?search_query={channel_name}"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(search_url, headers=headers, timeout=10)
            
            # Procura por channel ID no HTML
            match = re.search(r'"channelId":"([^"]+)"', response.text)
            if match:
                channel_id = match.group(1)
                rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                return {
                    "url": rss_url,
                    "title": channel_name,
                    "type": "youtube"
                }
        except:
            pass
        
        return None
    
    # Se for URL, extrai channel ID ou username
    if '/@' in url:
        # Formato: https://www.youtube.com/@Gorgonoid
        username = url.split('/@')[1].split('/')[0].split('?')[0]
        
        # Busca o channel ID
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            # Procura por channel ID no HTML
            match = re.search(r'"channelId":"([^"]+)"', response.text)
            if match:
                channel_id = match.group(1)
                rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                return {
                    "url": rss_url,
                    "title": username,
                    "type": "youtube"
                }
        except:
            pass
    
    elif 'channel/' in url:
        # Formato: https://www.youtube.com/channel/UCLfCo17TCjx7qf-JMhQioLQ
        channel_id = url.split('channel/')[1].split('/')[0].split('?')[0]
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        return {
            "url": rss_url,
            "title": f"Channel {channel_id[:10]}...",
            "type": "youtube"
        }
    
    return None

def discover_rss_feed(url):
    """
    Tenta descobrir o RSS feed de um site
    Suporta: Blogs, Reddit, YouTube
    """
    print(f"\n🔍 Testando: {url}")
    
    results = {
        "site_url": url,
        "rss_found": [],
        "method": None,
        "status": "not_found"
    }
    
    try:
        # Detecta tipo de URL
        url_type = detect_url_type(url)
        
        # Reddit
        if url_type == 'reddit':
            print(f"  📱 Detectado: Reddit")
            reddit_feed = get_reddit_rss(url)
            
            # Valida o feed
            feed = feedparser.parse(reddit_feed["url"])
            if feed.entries:
                results["rss_found"].append({
                    "url": reddit_feed["url"],
                    "entries_count": len(feed.entries),
                    "title": reddit_feed["title"]
                })
                results["status"] = "found"
                results["method"] = "reddit_rss"
                print(f"  ✅ RSS Reddit: {reddit_feed['url']} ({len(feed.entries)} posts)")
                return results
        
        # YouTube
        elif url_type == 'youtube':
            print(f"  📺 Detectado: YouTube")
            youtube_feed = get_youtube_rss(url)
            
            if youtube_feed:
                # Valida o feed
                feed = feedparser.parse(youtube_feed["url"])
                if feed.entries:
                    results["rss_found"].append({
                        "url": youtube_feed["url"],
                        "entries_count": len(feed.entries),
                        "title": youtube_feed["title"]
                    })
                    results["status"] = "found"
                    results["method"] = "youtube_rss"
                    print(f"  ✅ RSS YouTube: {youtube_feed['url']} ({len(feed.entries)} vídeos)")
                    return results
        
        # Blog (comportamento original)
        print(f"  🌐 Detectado: Blog/Site")
        
        # Tenta variações comuns de RSS
        common_rss_paths = [
            "/feed",
            "/feed/",
            "/rss",
            "/rss/",
            "/feed.xml",
            "/rss.xml",
            "/atom.xml",
            "/index.xml",
            "/feeds/posts/default",  # Blogger
            "/blog/feed",
            "/blog/rss",
            "/wp-rss2.php",  # WordPress antigo
            "/wp-feed.php",  # WordPress antigo
            "/?feed=rss2",  # WordPress
            "/?feed=atom",  # WordPress
        ]
        
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        # Testa URLs comuns no domínio base
        for path in common_rss_paths:
            test_url = base_url + path
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(test_url, timeout=5, allow_redirects=True, verify=False, headers=headers)
                if response.status_code == 200:
                    # Valida se é realmente um feed
                    feed = feedparser.parse(response.content)
                    if feed.entries and len(feed.entries) > 0:
                        results["rss_found"].append({
                            "url": test_url,
                            "entries_count": len(feed.entries),
                            "title": feed.feed.get('title', 'N/A')
                        })
                        print(f"  ✅ Encontrado: {test_url} ({len(feed.entries)} entries)")
            except Exception as e:
                pass
        
        # Se não encontrou, busca no HTML
        if not results["rss_found"]:
            print(f"  🔎 Buscando no HTML...")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Procura por links RSS no HTML
            rss_links = soup.find_all('link', type=['application/rss+xml', 'application/atom+xml'])
            
            for link in rss_links:
                rss_url = link.get('href')
                if rss_url:
                    full_url = urljoin(url, rss_url)
                    try:
                        feed = feedparser.parse(full_url)
                        if feed.entries:
                            results["rss_found"].append({
                                "url": full_url,
                                "entries_count": len(feed.entries),
                                "title": feed.feed.get('title', 'N/A')
                            })
                            print(f"  ✅ Encontrado no HTML: {full_url} ({len(feed.entries)} entries)")
                    except:
                        pass
            
            # Procura também por links <a> com texto "RSS" ou "Feed"
            if not results["rss_found"]:
                rss_anchors = soup.find_all('a', href=True, string=lambda s: s and ('rss' in s.lower() or 'feed' in s.lower()))
                for anchor in rss_anchors:
                    rss_url = anchor.get('href')
                    if rss_url:
                        full_url = urljoin(url, rss_url)
                        try:
                            feed = feedparser.parse(full_url)
                            if feed.entries:
                                results["rss_found"].append({
                                    "url": full_url,
                                    "entries_count": len(feed.entries),
                                    "title": feed.feed.get('title', 'N/A')
                                })
                                print(f"  ✅ Encontrado via link: {full_url} ({len(feed.entries)} entries)")
                        except:
                            pass
        
        if results["rss_found"]:
            results["status"] = "found"
            results["method"] = "auto_discovery"
        else:
            print(f"  ❌ Nenhum RSS encontrado")
            results["status"] = "not_found"
    
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 DESCOBRINDO RSS FEEDS")
    print("=" * 60)
    
    all_results = []
    
    for site in SITES_TO_TEST:
        result = discover_rss_feed(site)
        all_results.append(result)
    
    # Salva resultados
    with open('rss_discovery_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    
    found_count = sum(1 for r in all_results if r["status"] == "found")
    not_found_count = sum(1 for r in all_results if r["status"] == "not_found")
    
    print(f"✅ RSS Encontrados: {found_count}")
    print(f"❌ Não encontrados: {not_found_count}")
    
    print("\n📋 FEEDS ENCONTRADOS PARA N8N:")
    print("-" * 60)
    
    n8n_feeds = []
    for result in all_results:
        if result["rss_found"]:
            for feed in result["rss_found"]:
                n8n_feeds.append({
                    "name": feed["title"],
                    "url": feed["url"],
                    "site_url": result["site_url"],
                    "entries": feed["entries_count"]
                })
    
    print(json.dumps(n8n_feeds, indent=2, ensure_ascii=False))
    
    print(f"\n💾 Resultados salvos em: rss_discovery_results.json")
