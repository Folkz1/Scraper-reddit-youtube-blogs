"""
Valida todos os RSS feeds descobertos
"""

import requests
import feedparser
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Feeds para validar
FEEDS_TO_VALIDATE = [
    {
        "name": "Nutrition UK News",
        "rss_url": "https://www.nutrition.org.uk/news/feed/"
    },
    {
        "name": "MobiHealthNews South Korea",
        "rss_url": "https://www.mobihealthnews.com/tag/south-korea/feed"
    },
    {
        "name": "Lifespan.io Life Extension News",
        "rss_url": "https://www.lifespan.io/news/category/life-extension-news/feed/"
    },
    {
        "name": "Blue Zones",
        "rss_url": "https://www.bluezones.com/feed/"
    },
    {
        "name": "New Nutrition",
        "rss_url": "https://www.new-nutrition.com/feed"
    },
    {
        "name": "FoodNavigator USA",
        "rss_url": "https://www.foodnavigator-usa.com/arc/outboundfeeds/rss/"
    }
]

def validate_feed(name, url):
    """Valida se um feed RSS funciona"""
    print(f"\n🔍 Validando: {name}")
    print(f"   URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False, allow_redirects=True)
        if response.status_code != 200:
            print(f"   ❌ Status: {response.status_code}")
            return None
        
        feed = feedparser.parse(response.content)
        
        if not feed.entries:
            print(f"   ❌ Sem entries")
            return None
        
        print(f"   ✅ OK - {len(feed.entries)} entries")
        print(f"   📰 Título: {feed.feed.get('title', 'N/A')}")
        
        # Mostra primeiro item
        if feed.entries:
            first = feed.entries[0]
            print(f"   📄 Último post: {first.get('title', 'N/A')[:60]}...")
        
        return {
            "name": name,
            "url": url,
            "entries_count": len(feed.entries),
            "feed_title": feed.feed.get('title', name),
            "status": "valid"
        }
    
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

if __name__ == "__main__":
    print("=" * 70)
    print("🔍 VALIDANDO RSS FEEDS")
    print("=" * 70)
    
    valid_feeds = []
    
    for feed_info in FEEDS_TO_VALIDATE:
        result = validate_feed(feed_info["name"], feed_info["rss_url"])
        if result:
            valid_feeds.append(result)
    
    print("\n" + "=" * 70)
    print(f"📊 RESUMO: {len(valid_feeds)}/{len(FEEDS_TO_VALIDATE)} feeds válidos")
    print("=" * 70)
    
    # Gera JSON para n8n
    n8n_format = []
    for feed in valid_feeds:
        n8n_format.append({
            "name": feed["feed_title"],
            "url": feed["url"],
            "type": "rss",
            "validation_score": 10,
            "active": True
        })
    
    print("\n📋 JSON PARA N8N:")
    print("-" * 70)
    print(json.dumps(n8n_format, indent=2, ensure_ascii=False))
    
    # Salva arquivo
    with open('feeds_validados_n8n.json', 'w', encoding='utf-8') as f:
        json.dump(n8n_format, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Arquivo salvo: feeds_validados_n8n.json")
