"""
Testa se o proxy do Apify está REALMENTE sendo usado
"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

APIFY_TOKEN = os.getenv('APIFY_API_TOKEN')

print("=" * 60)
print("🔍 TESTE REAL DE PROXY APIFY")
print("=" * 60)

if not APIFY_TOKEN:
    print("❌ Token do Apify não encontrado no .env")
    exit(1)

print(f"\n✅ Token encontrado: {APIFY_TOKEN[:20]}...{APIFY_TOKEN[-10:]}")

# Configura proxy Apify Residential
# Formato Apify: http://groups-RESIDENTIAL:PROXY_PASSWORD@proxy.apify.com:8000
APIFY_PROXY_PASSWORD = os.getenv('APIFY_PROXY_PASSWORD') or APIFY_TOKEN
proxy_url = f"http://groups-RESIDENTIAL:{APIFY_PROXY_PASSWORD}@proxy.apify.com:8000"
proxies = {
    'http': proxy_url,
    'https': proxy_url
}

print(f"\n📡 Proxy configurado: {proxy_url[:60]}...")

# Teste 1: Verifica IP sem proxy
print("\n" + "=" * 60)
print("1️⃣ Teste SEM proxy (IP real)")
print("=" * 60)
try:
    response = requests.get('https://api.ipify.org?format=json', timeout=10)
    ip_sem_proxy = response.json()['ip']
    print(f"✅ IP sem proxy: {ip_sem_proxy}")
except Exception as e:
    print(f"❌ Erro: {e}")
    ip_sem_proxy = None

# Teste 2: Verifica IP COM proxy Apify
print("\n" + "=" * 60)
print("2️⃣ Teste COM proxy Apify Residential")
print("=" * 60)
try:
    response = requests.get(
        'https://api.ipify.org?format=json',
        proxies=proxies,
        timeout=15
    )
    ip_com_proxy = response.json()['ip']
    print(f"✅ IP com proxy Apify: {ip_com_proxy}")
    
    if ip_sem_proxy and ip_com_proxy != ip_sem_proxy:
        print(f"✅ PROXY FUNCIONANDO! IPs diferentes")
    else:
        print(f"⚠️ IPs iguais - proxy pode não estar funcionando")
        
except Exception as e:
    print(f"❌ Erro ao usar proxy Apify: {e}")
    print(f"   Possíveis causas:")
    print(f"   - Token inválido ou expirado")
    print(f"   - Sem créditos no Apify")
    print(f"   - Proxy bloqueado pela VPS")

# Teste 3: Tenta acessar YouTube com proxy
print("\n" + "=" * 60)
print("3️⃣ Teste de acesso ao YouTube COM proxy")
print("=" * 60)
try:
    response = requests.get(
        'https://www.youtube.com',
        proxies=proxies,
        timeout=15,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    print(f"✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ YouTube acessível via proxy Apify!")
        if 'Sign in' in response.text or 'bot' in response.text.lower():
            print(f"⚠️ Mas detectou mensagem de bot no HTML")
        else:
            print(f"✅ Sem mensagem de bloqueio detectada")
    else:
        print(f"❌ YouTube retornou status {response.status_code}")
        
except Exception as e:
    print(f"❌ Erro ao acessar YouTube: {e}")

print("\n" + "=" * 60)
print("📋 CONCLUSÃO")
print("=" * 60)
print("Se os IPs forem diferentes e YouTube retornar 200,")
print("o proxy Apify está funcionando corretamente.")
print("=" * 60)
