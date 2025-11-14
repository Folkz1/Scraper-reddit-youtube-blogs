"""
Testa se os imports estão funcionando
Execute na VPS: python test_import.py
"""

print("=" * 60)
print("🔍 TESTE DE IMPORTS")
print("=" * 60)

print("\n1️⃣ Testando youtube_transcript_api...")
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    print("✅ YouTubeTranscriptApi importado")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n2️⃣ Testando proxy_manager...")
try:
    from scrapers.proxy_manager import proxy_manager
    print("✅ proxy_manager importado")
    
    # Testa se Apify está configurado
    apify_proxy = proxy_manager.get_apify_proxy("RESIDENTIAL")
    if apify_proxy:
        print(f"✅ Apify proxy configurado: {apify_proxy['http'][:50]}...")
    else:
        print("❌ Apify proxy NÃO configurado (token ausente)")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n3️⃣ Testando youtube_scraper_api...")
try:
    from scrapers.youtube_scraper_api import scrape_youtube_with_api
    print("✅ scrape_youtube_with_api importado")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n4️⃣ Testando youtube_scraper (principal)...")
try:
    from scrapers.youtube_scraper import scrape_youtube, HAS_API_SCRAPER
    print(f"✅ scrape_youtube importado")
    print(f"   HAS_API_SCRAPER = {HAS_API_SCRAPER}")
    
    if not HAS_API_SCRAPER:
        print("⚠️ API scraper não está disponível!")
        print("   Vai usar yt-dlp (que está sendo bloqueado)")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("📋 CONCLUSÃO:")
print("=" * 60)

try:
    from scrapers.youtube_scraper import HAS_API_SCRAPER
    if HAS_API_SCRAPER:
        print("✅ Sistema configurado corretamente!")
        print("   YouTube deve funcionar com Apify")
    else:
        print("❌ API scraper não disponível")
        print("   Verifique os erros acima")
except:
    print("❌ Erro crítico nos imports")

print("=" * 60)
