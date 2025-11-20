"""
Teste de descoberta de RSS para Reddit e YouTube
"""

from discover_rss_feeds import discover_rss_feed

# URLs de teste
test_urls = [
    # Reddit
    "https://www.reddit.com/r/Maromba/",
    "https://reddit.com/r/fitness",
    "https://www.reddit.com/r/bodybuilding",
    
    # YouTube (nomes de canais)
    "Gorgonoid",
    "Leandro Twin",
    "Renato Cariani",
    
    # YouTube (URLs)
    "https://www.youtube.com/@Gorgonoid",
    "https://www.youtube.com/channel/UCLfCo17TCjx7qf-JMhQioLQ",
    
    # Blogs
    "https://treinomestre.com.br/",
    "https://fitfeed.com.br",
]

print("=" * 60)
print("🧪 TESTE DE DESCOBERTA DE RSS")
print("=" * 60)

for url in test_urls:
    result = discover_rss_feed(url)
    
    if result["status"] == "found":
        print(f"\n✅ {url}")
        for feed in result["rss_found"]:
            print(f"   RSS: {feed['url']}")
            print(f"   Título: {feed['title']}")
            print(f"   Entries: {feed['entries_count']}")
    else:
        print(f"\n❌ {url}")
        print(f"   Status: {result['status']}")

print("\n" + "=" * 60)
print("✅ TESTE CONCLUÍDO")
print("=" * 60)
