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
from scrapers.youtube_scraper import scrape_youtube
from scrapers.reddit_scraper import scrape_reddit
from scrapers.celebrity_scraper import scrape_celebrity_image

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

def detect_url_type(url: str) -> str:
    """Detecta automaticamente o tipo de URL"""
    url_lower = url.lower()
    
    if "youtube.com/watch" in url_lower or "youtu.be/" in url_lower:
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
