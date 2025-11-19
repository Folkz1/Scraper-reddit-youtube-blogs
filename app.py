from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, Literal
import uvicorn
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

from scrapers.web_scraper import scrape_article
from scrapers.youtube_scraper import scrape_youtube, extract_video_id
from scrapers.reddit_scraper import scrape_reddit
from scrapers.celebrity_scraper import scrape_celebrity_image
from scrapers.youtube_data_api import get_video_metadata, get_channel_info
from scrapers.news_scraper import scrape_news

app = FastAPI(
    title="Scraper API",
    description="API para scraping de artigos, YouTube e Reddit",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: str
    type: Literal["auto", "article", "youtube", "reddit"] = "auto"
    max_comments: Optional[int] = 10
    sort_comments: Optional[Literal["top", "best", "new", "controversial"]] = "top"

class CelebrityImageRequest(BaseModel):
    celebrity_name: str
    num_results: Optional[int] = 5

class ScrapeResponse(BaseModel):
    success: bool
    type: str
    data: dict
    error: Optional[str] = None

class CelebrityImageResponse(BaseModel):
    success: bool
    data: dict
    error: Optional[str] = None

class NewsRequest(BaseModel):
    url: str
    existing_links: Optional[list[str]] = []
    hours_window: Optional[int] = 24
    max_summary_length: Optional[int] = 500

class NewsResponse(BaseModel):
    success: bool
    data: dict
    error: Optional[str] = None

class YouTubeMetadataRequest(BaseModel):
    url: str

class YouTubeMetadataResponse(BaseModel):
    success: bool
    data: dict
    error: Optional[str] = None

def detect_url_type(url: str) -> str:
    """Detecta automaticamente o tipo de URL"""
    url_lower = url.lower()
    
    if "youtube.com/watch" in url_lower or "youtu.be/" in url_lower or "youtube.com/shorts/" in url_lower:
        return "youtube"
    elif "reddit.com/r/" in url_lower and "/comments/" in url_lower:
        return "reddit"
    else:
        return "article"

@app.get("/")
async def root():
    return {
        "service": "Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "/scrape": "POST - Scrape de URLs (artigos, YouTube, Reddit)",
            "/youtube/metadata": "POST - Metadados de vídeos do YouTube (views, likes, etc)",
            "/celebrity-image": "POST - Busca e processa imagem de celebridade",
            "/scrape-news": "POST - Scrape de notícias (RSS + fallback HTML)",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape(request: ScrapeRequest):
    try:
        # Auto-detecta tipo se necessário
        scrape_type = request.type
        if scrape_type == "auto":
            scrape_type = detect_url_type(request.url)
        
        # Executa scraper apropriado
        if scrape_type == "youtube":
            data = await scrape_youtube(request.url)
        elif scrape_type == "reddit":
            data = await scrape_reddit(
                request.url,
                max_comments=request.max_comments,
                sort_by=request.sort_comments
            )
        else:  # article
            data = await scrape_article(request.url)
        
        return ScrapeResponse(
            success=True,
            type=scrape_type,
            data=data
        )
    
    except Exception as e:
        return ScrapeResponse(
            success=False,
            type=scrape_type if 'scrape_type' in locals() else "unknown",
            data={},
            error=str(e)
        )

@app.post("/youtube/metadata", response_model=YouTubeMetadataResponse)
async def get_youtube_metadata(request: YouTubeMetadataRequest):
    """
    Busca metadados públicos de um vídeo do YouTube
    
    Retorna:
    - Views, likes, comentários
    - Título, descrição, tags
    - Data de publicação
    - Informações do canal
    - Thumbnail de alta qualidade
    - Duração do vídeo
    
    Requer: YOUTUBE_API_KEY configurada no .env
    """
    try:
        # Extrai video_id da URL
        video_id = extract_video_id(request.url)
        
        # Busca metadados
        metadata = get_video_metadata(video_id)
        
        if not metadata:
            raise Exception("Não foi possível obter metadados. Verifique se YOUTUBE_API_KEY está configurada.")
        
        # Busca informações do canal (opcional)
        channel_info = None
        if metadata.get('channel_id'):
            channel_info = get_channel_info(metadata['channel_id'])
        
        # Monta resposta
        response_data = {
            "video_id": video_id,
            "url": request.url,
            **metadata
        }
        
        if channel_info:
            response_data['channel_info'] = channel_info
        
        return YouTubeMetadataResponse(
            success=True,
            data=response_data,
            error=None
        )
    
    except Exception as e:
        return YouTubeMetadataResponse(
            success=False,
            data={},
            error=str(e)
        )

@app.post("/celebrity-image", response_model=CelebrityImageResponse)
async def get_celebrity_image(request: CelebrityImageRequest):
    """
    Busca, analisa com IA e processa imagem de celebridade
    
    - Busca imagens no Google Custom Search
    - IA (Gemini) escolhe a melhor imagem
    - Faz crop para 1:1 (Instagram)
    - Retorna base64 pronto para usar
    """
    try:
        data = await scrape_celebrity_image(
            request.celebrity_name,
            request.num_results
        )
        
        return CelebrityImageResponse(
            success=True,
            data=data,
            error=None
        )
    
    except Exception as e:
        return CelebrityImageResponse(
            success=False,
            data={},
            error=str(e)
        )

@app.post("/scrape-news", response_model=NewsResponse)
async def get_news(request: NewsRequest):
    """
    Scrape de notícias com RSS + fallback HTML
    
    - Tenta ler RSS feed primeiro (alta confiabilidade)
    - Se falhar, faz scraping do HTML do blog
    - Filtra por janela de tempo (padrão 24h)
    - Remove duplicatas baseado em links existentes
    - Retorna lista normalizada
    
    Parâmetros:
    - url: URL do RSS feed ou blog
    - existing_links: Lista de URLs já processadas (opcional)
    - hours_window: Janela de tempo em horas (padrão 24h)
    - max_summary_length: Tamanho máximo do resumo (padrão 500)
    
    Retorna:
    - news_list: Lista de notícias com title, url, summary, pubDate, source
    - total_found: Total de notícias encontradas
    - total_unique: Total após remover duplicatas
    - source_type: 'rss' ou 'html_scraping'
    """
    try:
        data = await scrape_news(
            url=request.url,
            existing_links=request.existing_links,
            hours_window=request.hours_window,
            max_summary_length=request.max_summary_length
        )
        
        return NewsResponse(
            success=True,
            data=data,
            error=None
        )
    
    except Exception as e:
        return NewsResponse(
            success=False,
            data={},
            error=str(e)
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
