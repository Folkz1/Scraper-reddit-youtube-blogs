"""
Script de teste para o Feed Manager
Testa validação e adição de fontes
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_validate_source():
    """Testa validação de fonte"""
    print("\n🔍 Testando validação de fonte...")
    
    response = requests.post(
        f"{BASE_URL}/api/sources/validate",
        json={
            "url": "https://fitfeed.com.br",
            "name": "FitFeed Teste"
        }
    )
    
    data = response.json()
    
    if data["success"]:
        print("✅ Validação bem-sucedida!")
        print(f"   Score: {data['data']['validation_score']}/10")
        print(f"   RSS encontrado: {len(data['data']['rss_found'])} feed(s)")
        print(f"   Notícias encontradas: {len(data['data']['sample_news'])}")
        
        if data['data']['sample_news']:
            print("\n   📰 Exemplo de notícia:")
            news = data['data']['sample_news'][0]
            print(f"   Título: {news['title'][:60]}...")
            print(f"   URL: {news['url']}")
    else:
        print(f"❌ Erro: {data['error']}")
    
    return data

def test_list_sources():
    """Testa listagem de fontes"""
    print("\n📚 Testando listagem de fontes...")
    
    response = requests.get(f"{BASE_URL}/api/sources")
    data = response.json()
    
    if data["success"]:
        print(f"✅ {data['total']} fonte(s) encontrada(s)")
        
        for source in data["sources"][:3]:  # Mostra apenas 3
            print(f"\n   📰 {source['name']}")
            print(f"      URL: {source['url']}")
            print(f"      Tipo: {source['type']}")
            print(f"      Ativa: {'✅' if source['active'] else '❌'}")
            print(f"      Score: {source['validation_score']}/10")
    else:
        print("❌ Erro ao listar fontes")
    
    return data

def test_add_source():
    """Testa adição de fonte"""
    print("\n➕ Testando adição de fonte...")
    
    response = requests.post(
        f"{BASE_URL}/api/sources/add",
        json={
            "url": "https://www.tuasaude.com",
            "name": "Tua Saúde Teste"
        }
    )
    
    data = response.json()
    
    if data["success"]:
        print("✅ Fonte adicionada com sucesso!")
        source = data['data']['source']
        print(f"   ID: {source['id']}")
        print(f"   Nome: {source['name']}")
        print(f"   URL: {source['url']}")
        print(f"   Score: {source['validation_score']}/10")
    else:
        print(f"❌ Erro: {data['error']}")
    
    return data

def test_health():
    """Testa se o servidor está rodando"""
    print("\n🏥 Testando health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando!")
            return True
        else:
            print("❌ Servidor retornou erro")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor está rodando:")
        print("   python app.py")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DO FEED MANAGER")
    print("=" * 60)
    
    # Testa health
    if not test_health():
        exit(1)
    
    # Testa validação
    test_validate_source()
    
    # Testa listagem
    test_list_sources()
    
    # Testa adição (comentado para não duplicar)
    # test_add_source()
    
    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 60)
    print("\n💡 Acesse a interface web em:")
    print(f"   {BASE_URL}/feed-manager")
