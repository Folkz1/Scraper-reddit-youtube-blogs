import requests
import base64
from io import BytesIO
from PIL import Image
from typing import Dict, List, Optional
import os
import re

# Google Custom Search API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

# OpenRouter API
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY não configurada no .env")

# Mapeamento de apelidos/nomes artísticos para nomes reais
CELEBRITY_NAME_MAPPING = {
    # Bodybuilders BR
    "cbum": "Chris Bumstead",
    "ramon dino": "Ramon Dino",
    "ramondinopro": "Ramon Dino",
    "renato cariani": "Renato Cariani",
    "renatocariani": "Renato Cariani",
    "julio balestrin": "Julio Balestrin",
    "juliobalestrinoficial": "Julio Balestrin",
    "fabio giga": "Fábio Giga",
    "fabiogigapro": "Fábio Giga",
    "gordao da xj": "Gordão da XJ",
    "gordaodaxj00": "Gordão da XJ",
    "toguro": "Toguro",
    "paulo muzy": "Paulo Muzy",
    "paulomuzy": "Paulo Muzy",
    "leandro twin": "Leandro Twin",
    "leandrotwin": "Leandro Twin",
    "leo stronda": "Leo Stronda",
    "leostrondaoficial": "Leo Stronda",
    "horse": "Caio Bottura",
    "caio bottura": "Caio Bottura",
    "caiobottura": "Caio Bottura",
    "rafael brandao": "Rafael Brandão",
    "rafaelbrandaopro": "Rafael Brandão",
    "vivi winkler": "Vivi Winkler",
    "viviwinkler": "Vivi Winkler",
    "carol vaz": "Carol Vaz",
    "teamcarolvaz": "Carol Vaz",
    "gracyanne barbosa": "Gracyanne Barbosa",
    "graoficial": "Gracyanne Barbosa",
    "eva andressa": "Eva Andressa",
    "tenente breno": "Tenente Breno",
    "tenente maromba": "Tenente Maromba",
    "sardinha": "Fernando Sardinha",
    "fernandosardinha": "Fernando Sardinha",
    "felipe franco": "Felipe Franco",
    "felipefrancopro": "Felipe Franco",
    "will detilli": "Will Detilli",
    "willdetilli": "Will Detilli",
    "alex dos anabolizantes": "Alex dos Anabolizantes",
    "maria luiza": "Maria Luiza Mendes",
    "malulofit": "Maria Luiza Mendes",
    "gabriel arones": "Gabriel Arones",
    "laercio refundini": "Laercio Refundini",
    "laerciorefundini": "Laercio Refundini",
    "dudu haluch": "Dudu Haluch",
    "bruna lima": "Bruna Lima",
    "xoobruna": "Bruna Lima",
    "pantera": "Pantera Culturista",
    "panteraculturista": "Pantera Culturista",
    "gorila": "Gorila Motivação Maromba",
    # Internacionais
    "ronnie coleman": "Ronnie Coleman",
    "jay cutler": "Jay Cutler",
    "arnold schwarzenegger": "Arnold Schwarzenegger",
    "arnold": "Arnold Schwarzenegger",
}

def normalize_celebrity_name(name: str) -> str:
    """
    Normaliza nome de celebridade removendo @ e caracteres especiais
    """
    # Remove @ e espaços extras
    name = name.strip().lower()
    name = name.replace('@', '')
    name = re.sub(r'\s+', ' ', name)
    
    # Busca no mapeamento
    if name in CELEBRITY_NAME_MAPPING:
        return CELEBRITY_NAME_MAPPING[name]
    
    # Se não encontrou, retorna capitalizado
    return name.title()

def generate_search_queries(celebrity_name: str) -> List[str]:
    """
    Gera múltiplas queries de busca para aumentar chances de sucesso
    """
    normalized_name = normalize_celebrity_name(celebrity_name)
    
    queries = [
        # Query 1: Nome + bodybuilder
        f"{normalized_name} bodybuilder photo",
        # Query 2: Nome + portrait profissional
        f"{normalized_name} portrait professional photo",
        # Query 3: Nome + fitness
        f"{normalized_name} fitness athlete photo",
        # Query 4: Nome + headshot
        f"{normalized_name} headshot high quality",
    ]
    
    return queries

def search_celebrity_images(celebrity_name: str, num_results: int = 5) -> List[Dict]:
    """
    Busca imagens de uma celebridade usando Google Custom Search API
    Tenta múltiplas queries para aumentar taxa de sucesso
    """
    try:
        if not GOOGLE_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
            raise Exception(
                "Google API não configurada. "
                "Configure GOOGLE_API_KEY e GOOGLE_SEARCH_ENGINE_ID no arquivo .env"
            )
        
        # Gera múltiplas queries
        queries = generate_search_queries(celebrity_name)
        
        all_images = []
        seen_urls = set()
        
        # Tenta cada query até ter imagens suficientes
        for query in queries:
            if len(all_images) >= num_results:
                break
            
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": GOOGLE_API_KEY,
                    "cx": GOOGLE_SEARCH_ENGINE_ID,
                    "q": query,
                    "searchType": "image",
                    "imgSize": "large",
                    "imgType": "photo",
                    "num": 10,  # Máximo por query
                    "safe": "active"
                }
                
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                
                if "items" not in data:
                    continue
                
                # Domínios problemáticos (relaxados - apenas os piores)
                blocked_domains = [
                    'tiktok.com',
                    'tiktokcdn',
                    'jammable.com',
                ]
                
                for item in data["items"]:
                    image_url = item["link"]
                    
                    # Evita duplicatas
                    if image_url in seen_urls:
                        continue
                    
                    # Filtra apenas domínios muito problemáticos
                    if any(domain in image_url.lower() for domain in blocked_domains):
                        continue
                    
                    # Aceita mais formatos (relaxado)
                    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']
                    has_valid_ext = any(ext in image_url.lower() for ext in valid_extensions)
                    
                    # Aceita URLs sem extensão se tiver indicadores de imagem
                    has_image_indicator = any(word in image_url.lower() for word in ['image', 'img', 'photo', 'picture', 'media'])
                    
                    if not (has_valid_ext or has_image_indicator):
                        continue
                    
                    seen_urls.add(image_url)
                    all_images.append({
                        "url": image_url,
                        "thumbnail": item.get("image", {}).get("thumbnailLink", ""),
                        "width": item.get("image", {}).get("width", 0),
                        "height": item.get("image", {}).get("height", 0),
                        "context": item.get("snippet", ""),
                        "query_used": query
                    })
                    
                    if len(all_images) >= num_results * 2:  # Busca o dobro para ter opções
                        break
                
            except Exception as e:
                # Se uma query falhar, tenta a próxima
                continue
        
        if not all_images:
            raise Exception(f"Nenhuma imagem encontrada após tentar {len(queries)} queries diferentes")
        
        return all_images[:num_results * 2]  # Retorna até o dobro do solicitado
    
    except Exception as e:
        raise Exception(f"Erro ao buscar imagens no Google: {str(e)}")

def download_image_as_base64(url: str) -> Optional[str]:
    """
    Baixa imagem e converte para base64 (data URI)
    """
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'image/*',
            }
        )
        
        if response.status_code != 200:
            return None
        
        # Verifica se é imagem
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            return None
        
        # Converte para base64
        img_base64 = base64.b64encode(response.content).decode()
        
        # Detecta formato
        if 'jpeg' in content_type or 'jpg' in content_type:
            mime = 'image/jpeg'
        elif 'png' in content_type:
            mime = 'image/png'
        elif 'webp' in content_type:
            mime = 'image/webp'
        else:
            mime = 'image/jpeg'  # fallback
        
        return f"data:{mime};base64,{img_base64}"
    
    except:
        return None

def choose_best_image_with_ai(celebrity_name: str, images: List[Dict]) -> Dict:
    """
    Usa Gemini 2.5 Flash via OpenRouter para escolher a melhor imagem
    Baixa as imagens e envia como base64 (igual N8N)
    """
    try:
        # Baixa até 3 imagens como base64
        images_base64 = []
        images_downloaded = []
        
        for img in images[:5]:  # Tenta até 5
            if len(images_base64) >= 3:  # Máximo 3
                break
            
            base64_data = download_image_as_base64(img["url"])
            if base64_data:
                images_base64.append(base64_data)
                images_downloaded.append(img)
        
        if not images_base64:
            raise Exception("Nenhuma imagem pôde ser baixada")
        
        # Prompt que pede para IA reconhecer o famoso
        prompt = f"""Você deve analisar {len(images_base64)} imagens e retornar APENAS um objeto JSON válido.

TAREFA:
1. Identifique se mostra {celebrity_name} (bodybuilder/fitness brasileiro)
2. Escolha a melhor imagem

CRITÉRIOS:
- É {celebrity_name}?
- Rosto claro
- Boa iluminação
- Fundo neutro
- Sem texto excessivo

IMPORTANTE: Retorne APENAS JSON válido, sem texto adicional, sem markdown, sem explicações.

Formato:
{{"best_index": 0, "confidence": 0.9, "is_correct_person": true, "reason": "breve", "issues": []}}"""

        if not OPENROUTER_API_KEY:
            raise Exception(
                "OpenRouter API não configurada. "
                "Configure OPENROUTER_API_KEY no arquivo .env"
            )
        
        # Monta o payload para OpenRouter (formato idêntico ao N8N com base64)
        payload = {
            "model": "google/gemini-2.5-flash-lite",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        *[
                            {
                                "type": "image_url",
                                "image_url": {"url": base64_url}
                            }
                            for base64_url in images_base64
                        ]
                    ]
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://scraper-api.com",
            "X-Title": "Celebrity Image Scraper"
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=45
        )
        
        # Debug: mostra erro detalhado
        if response.status_code != 200:
            error_detail = response.text
            raise Exception(f"OpenRouter {response.status_code}: {error_detail[:200]}")
        
        response.raise_for_status()
        
        result = response.json()
        
        if "error" in result:
            raise Exception(f"OpenRouter error: {result['error']}")
        
        content = result["choices"][0]["message"]["content"]
        
        # Parse do JSON
        import json
        
        analysis = json.loads(content)
        
        # Pega a imagem escolhida
        best_index = analysis.get("best_index", 0)
        best_image = images_downloaded[best_index]
        
        # Verifica se IA confirmou que é a pessoa certa
        is_correct = analysis.get("is_correct_person", True)
        if not is_correct:
            raise Exception(f"IA não reconheceu {celebrity_name} nas imagens")
        
        return {
            "url": best_image["url"],
            "index": best_index,
            "confidence": analysis.get("confidence", 0.8),
            "reason": analysis.get("reason", "Melhor opção disponível"),
            "issues": analysis.get("issues", []),
            "original_width": best_image.get("width", 0),
            "original_height": best_image.get("height", 0),
            "ai_verified": True
        }
    
    except Exception as e:
        # Fallback: escolhe a primeira imagem com boa resolução
        for i, img in enumerate(images):
            if img.get("width", 0) >= 800 and img.get("height", 0) >= 800:
                return {
                    "url": img["url"],
                    "index": i,
                    "confidence": 0.5,
                    "reason": "Fallback: Primeira imagem com boa resolução",
                    "issues": [f"IA não disponível: {str(e)}"],
                    "original_width": img.get("width", 0),
                    "original_height": img.get("height", 0)
                }
        
        # Última opção: primeira imagem
        if images:
            return {
                "url": images[0]["url"],
                "index": 0,
                "confidence": 0.3,
                "reason": "Fallback: Primeira imagem disponível",
                "issues": [f"IA não disponível: {str(e)}"],
                "original_width": images[0].get("width", 0),
                "original_height": images[0].get("height", 0)
            }
        
        raise Exception("Nenhuma imagem disponível")

def crop_image_to_square(image_url: str, target_size: int = 1080) -> str:
    """
    Baixa imagem, faz crop centralizado para 1:1 e retorna base64
    """
    try:
        # Download da imagem com headers mais completos
        response = requests.get(
            image_url, 
            timeout=15, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.google.com/'
            },
            allow_redirects=True
        )
        response.raise_for_status()
        
        # Verifica se é realmente uma imagem
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise Exception(f"URL não retornou uma imagem (content-type: {content_type})")
        
        # Abre imagem
        img = Image.open(BytesIO(response.content))
        
        # Converte para RGB se necessário
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Dimensões originais
        width, height = img.size
        
        # Calcula crop centralizado
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        
        # Crop
        img_cropped = img.crop((left, top, right, bottom))
        
        # Resize para tamanho alvo (1080x1080 para Instagram)
        img_final = img_cropped.resize((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Converte para base64
        buffer = BytesIO()
        img_final.save(buffer, format="JPEG", quality=95, optimize=True)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{img_base64}"
    
    except Exception as e:
        raise Exception(f"Erro ao processar imagem: {str(e)}")

async def scrape_celebrity_image(
    celebrity_name: str,
    num_results: int = 5
) -> Dict:
    """
    Pipeline completo: Busca → IA escolhe → Crop 1:1
    """
    try:
        # 1. Busca imagens no Google
        images = search_celebrity_images(celebrity_name, num_results)
        
        if not images:
            raise Exception(f"Nenhuma imagem encontrada para '{celebrity_name}'")
        
        # 2. IA escolhe a melhor
        best_image = choose_best_image_with_ai(celebrity_name, images)
        
        # 3. Crop para 1:1 (com fallback se falhar)
        image_1x1_base64 = None
        last_error = None
        
        # Tenta a imagem escolhida pela IA
        try:
            image_1x1_base64 = crop_image_to_square(best_image["url"])
        except Exception as e:
            last_error = str(e)
            # Fallback: tenta outras imagens em ordem
            for i, img in enumerate(images):
                if i == best_image["index"]:
                    continue  # Já tentamos esta
                try:
                    image_1x1_base64 = crop_image_to_square(img["url"])
                    best_image = {
                        "url": img["url"],
                        "index": i,
                        "reason": f"Fallback: Imagem original falhou ({last_error[:50]})",
                        "confidence": 0.6,
                        "issues": [f"Imagem da IA não processável: {last_error}"],
                        "original_width": img.get("width", 0),
                        "original_height": img.get("height", 0)
                    }
                    break
                except:
                    continue
        
        if not image_1x1_base64:
            raise Exception(f"Nenhuma imagem pôde ser processada. Último erro: {last_error}")
        
        return {
            "celebrity": celebrity_name,
            "images_found": len(images),
            "best_image": {
                "url": best_image["url"],
                "reason": best_image["reason"],
                "confidence": best_image["confidence"],
                "issues": best_image["issues"]
            },
            "image_1x1_base64": image_1x1_base64,
            "dimensions": {
                "original": {
                    "width": best_image["original_width"],
                    "height": best_image["original_height"]
                },
                "cropped": {
                    "width": 1080,
                    "height": 1080
                }
            }
        }
    
    except Exception as e:
        raise Exception(f"Erro no pipeline de imagem: {str(e)}")
