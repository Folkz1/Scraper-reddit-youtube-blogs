import requests
import json

print("🧪 Teste rápido do endpoint /celebrity-image\n")

url = "http://localhost:8001/celebrity-image"
payload = {"celebrity_name": "Jojo Todynho"}

print(f"📡 Enviando request para: {url}")
print(f"📦 Payload: {json.dumps(payload, indent=2)}\n")

try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"✅ Status: {response.status_code}\n")
    
    data = response.json()
    
    if data.get('success'):
        print("🎉 SUCESSO!\n")
        print(f"👤 Celebridade: {data['data']['celebrity']}")
        print(f"🖼️  Imagens encontradas: {data['data']['images_found']}")
        print(f"🎯 Confiança da IA: {data['data']['best_image']['confidence']*100:.1f}%")
        print(f"💡 Razão: {data['data']['best_image']['reason']}")
        print(f"📦 Base64 gerado: {len(data['data']['image_1x1_base64']):,} caracteres")
    else:
        print(f"❌ Erro: {data.get('error')}")
        
except Exception as e:
    print(f"❌ Erro: {str(e)}")
