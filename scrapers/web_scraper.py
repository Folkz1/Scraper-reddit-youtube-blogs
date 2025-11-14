import trafilatura
from bs4 import BeautifulSoup
import requests
from typing import Dict

async def scrape_article(url: str) -> Dict:
    """
    Scrape de artigos web usando trafilatura (biblioteca especializada)
    Fallback para BeautifulSoup se necessário
    """
    try:
        # Valida URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL inválida: deve começar com http:// ou https://")
        
        # Download do HTML com timeout
        downloaded = trafilatura.fetch_url(url, timeout=15)
        
        if not downloaded:
            raise Exception("Não foi possível baixar a página")
        
        # Extração com trafilatura (melhor para artigos)
        content = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            no_fallback=False
        )
        
        # Extrai metadados
        metadata = trafilatura.extract_metadata(downloaded)
        
        # Conta palavras
        word_count = len(content.split()) if content else 0
        
        return {
            "title": metadata.title if metadata and metadata.title else "Sem título",
            "content": content or "",
            "url": url,
            "word_count": word_count,
            "author": metadata.author if metadata and metadata.author else None,
            "date": metadata.date if metadata and metadata.date else None,
            "language": metadata.language if metadata and metadata.language else "unknown"
        }
    
    except Exception as e:
        # Fallback: BeautifulSoup
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts e styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Tenta pegar título
            title = soup.find('title')
            title_text = title.get_text() if title else "Sem título"
            
            # Pega todo o texto
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return {
                "title": title_text,
                "content": text,
                "url": url,
                "word_count": len(text.split()),
                "author": None,
                "date": None,
                "language": "unknown"
            }
        except Exception as fallback_error:
            raise Exception(f"Erro no scraping: {str(e)}. Fallback também falhou: {str(fallback_error)}")
