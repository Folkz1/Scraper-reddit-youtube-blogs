import requests
import base64
from io import BytesIO
from PIL import Image
from typing import Dict, List, Optional
import os

# Google Custom Search API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

# OpenRouter API
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

def search_celebrity_images(celebrity_name: str, num_results: int = 5) -> List[Dict]:
    """
    Busca imagens de uma celebridade usando Google Custom Search API
    """
    try:
        if not GOOGLE_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
            raise Exception(
                "Google API não configurada. "
                "Configure GOOGLE_API_KEY e GOOGLE_SEARCH_ENGINE_ID no arquivo .env"
            )
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_SEARCH_ENGINE_ID,
            "q": f"{celebrity_name} official photo high quality",
            "searchType": "image",
            "imgSize": "large",
            "imgType": "photo",
            "num": min(num_results * 2, 10),  # Busca mais para compensar filtros (máx 10)
            "safe": "active"
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if "items" not in data:
            return []
        
        # Domínios problemáticos que costumam retornar HTML em vez de imagem
        blocked_domains = [
            'tiktok.com',
            'tiktokcdn',
            'jammable.com',
            'facebook.com',
            'fbsbx.com',
            'instagram.com',
            'cdninstagram.com'
        ]
        
        images = []
        for item in data["items"]:
            image_url = item["link"]
            
            # Filtra URLs problemáticas
            if any(domain in image_url.lower() for domain in blocked_domains):
                continue
            
            # Filtra URLs sem extensão de imagem válida
            if not any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                continue
            
            images.append({
                "url": image_url,
                "thumbnail": item.get("image", {}).get("thumbnailLink", ""),
                "width": item.get("image", {}).get("width", 0),
                "height": item.get("image", {}).get("height", 0),
                "context": item.get("snippet", "")
            })
            
            # Para quando tiver imagens suficientes
            if len(images) >= num_results:
                break
        
        return images
    
    except Exception as e:
        raise Exception(f"Erro ao buscar imagens no Google: {str(e)}")

def choose_best_image_with_ai(celebrity_name: str, images: List[Dict]) -> Dict:
    """
    Usa Gemini 2.0 Flash via OpenRouter para escolher a melhor imagem
    """
    try:
        # Prepara as URLs das imagens
        image_urls = [img["url"] for img in images[:5]]  # Máximo 5 imagens
        
        # Prompt para o Gemini
        prompt = f"""Analise estas {len(image_urls)} imagens de {celebrity_name}.

Escolha a MELHOR imagem para usar em um post de Instagram fitness/notícias.

CRITÉRIOS (em ordem de importância):
1. Rosto CLARO e VISÍVEL (essencial)
2. Boa ILUMINAÇÃO profissional
3. Fundo NEUTRO ou interessante (não distrativo)
4. SEM texto, watermark ou logos visíveis
5. Expressão neutra ou positiva
6. Alta qualidade/resolução
7. Enquadramento adequado (busto ou rosto)

IMPORTANTE:
- Se NENHUMA imagem atender os critérios mínimos, escolha a "menos pior"
- Priorize SEMPRE clareza do rosto
- Evite imagens com muitos elementos distrativos

Retorne APENAS um JSON válido (sem markdown, sem ```json):
{{
  "best_index": 0,
  "confidence": 0.95,
  "reason": "Rosto claro, iluminação profissional, fundo neutro",
  "issues": ["pequeno watermark no canto"]
}}"""

        if not OPENROUTER_API_KEY:
            raise Exception(
                "OpenRouter API não configurada. "
                "Configure OPENROUTER_API_KEY no arquivo .env"
            )
        
        # Monta o payload para OpenRouter
        # Usando modelo pago (mais confiável)
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
                                "image_url": {"url": url}
                            }
                            for url in image_urls
                        ]
                    ]
                }
            ],
            "response_format": {
                "type": "json_object"
            }
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
        best_image = images[best_index]
        
        return {
            "url": best_image["url"],
            "index": best_index,
            "confidence": analysis.get("confidence", 0.8),
            "reason": analysis.get("reason", "Melhor opção disponível"),
            "issues": analysis.get("issues", []),
            "original_width": best_image.get("width", 0),
            "original_height": best_image.get("height", 0)
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
