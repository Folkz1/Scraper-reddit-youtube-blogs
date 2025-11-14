"""
Teste do endpoint de busca de imagens de celebridades
"""
import requests
import json
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8001"

def test_celebrity_image(celebrity_name: str):
    """Testa busca de imagem de celebridade"""
    print(f"\n{'='*60}")
    print(f"🔍 Testando busca de imagem: {celebrity_name}")
    print(f"{'='*60}\n")
    
    payload = {
        "celebrity_name": celebrity_name,
        "num_results": 5
    }
    
    try:
        print("📡 Enviando request...")
        response = requests.post(
            f"{BASE_URL}/celebrity-image",
            json=payload,
            timeout=60  # Pode demorar um pouco
        )
        
        print(f"Status: {response.status_code}\n")
        
        data = response.json()
        
        if data['success']:
            print(f"✅ Sucesso!\n")
            
            result = data['data']
            
            print(f"👤 Celebridade: {result['celebrity']}")
            print(f"🖼️  Imagens encontradas: {result['images_found']}")
            print(f"\n🎯 Melhor imagem escolhida pela IA:")
            print(f"   URL: {result['best_image']['url'][:80]}...")
            print(f"   Confiança: {result['best_image']['confidence']*100:.1f}%")
            print(f"   Razão: {result['best_image']['reason']}")
            
            if result['best_image']['issues']:
                print(f"   ⚠️  Problemas: {', '.join(result['best_image']['issues'])}")
            
            print(f"\n📐 Dimensões:")
            print(f"   Original: {result['dimensions']['original']['width']}x{result['dimensions']['original']['height']}")
            print(f"   Cropada: {result['dimensions']['cropped']['width']}x{result['dimensions']['cropped']['height']}")
            
            # Verifica se tem base64
            base64_data = result['image_1x1_base64']
            base64_size = len(base64_data)
            print(f"\n📦 Base64 gerado: {base64_size:,} caracteres")
            print(f"   Primeiros 50 chars: {base64_data[:50]}...")
            
            # Salva resultado completo
            filename = f"test_celebrity_{celebrity_name.replace(' ', '_')}.json"
            with open(f"microservico_scraper/{filename}", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resposta completa salva em: {filename}")
            
            # Salva imagem base64 separada para testar
            img_filename = f"test_celebrity_{celebrity_name.replace(' ', '_')}.txt"
            with open(f"microservico_scraper/{img_filename}", 'w') as f:
                f.write(base64_data)
            print(f"🖼️  Base64 da imagem salvo em: {img_filename}")
            print(f"   (Cole no navegador ou use em <img src='...'> para visualizar)")
            
        else:
            print(f"❌ Erro: {data.get('error')}")
            print(f"\nDetalhes completos:")
            print(json.dumps(data, indent=2))
    
    except requests.exceptions.Timeout:
        print("❌ Timeout! A busca demorou muito (>60s)")
        print("Isso pode acontecer se:")
        print("  - Google API está lento")
        print("  - OpenRouter/Gemini está lento")
        print("  - Download da imagem está lento")
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro: API não está rodando!")
        print("Execute primeiro: python app.py")
    except Exception as e:
        print(f"\n❌ Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Teste do Celebrity Image Endpoint")
    print("=" * 60)
    
    # Lista de celebridades para testar
    celebrities = [
        "Jojo Todynho",
        "Chris Bumstead",
        "Ramon Dino",
    ]
    
    print("\nCelebridades disponíveis para teste:")
    for i, celeb in enumerate(celebrities, 1):
        print(f"{i}. {celeb}")
    print("4. Testar outro nome")
    print("0. Sair")
    
    while True:
        choice = input("\nEscolha uma opção (0-4): ").strip()
        
        if choice == "0":
            print("👋 Até logo!")
            break
        
        elif choice in ["1", "2", "3"]:
            idx = int(choice) - 1
            test_celebrity_image(celebrities[idx])
        
        elif choice == "4":
            name = input("Digite o nome da celebridade: ").strip()
            if name:
                test_celebrity_image(name)
            else:
                print("❌ Nome inválido")
        
        else:
            print("❌ Opção inválida")
        
        print("\n" + "=" * 60)
