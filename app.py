from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, Literal
import uvicorn
import os
from dotenv import load_dotenv
import asyncpg
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv()

from scrapers.web_scraper import scrape_article
from scrapers.youtube_scraper import scrape_youtube, extract_video_id
from scrapers.reddit_scraper import scrape_reddit
from scrapers.celebrity_scraper import scrape_celebrity_image
from scrapers.youtube_data_api import get_video_metadata, get_channel_info
from scrapers.news_scraper import scrape_news

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgres://postgres:99d74b03160029761260@72.61.32.25:5432/postgres?sslmode=disable')

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

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database helper
async def get_db_connection():
    """Cria conexão com PostgreSQL"""
    return await asyncpg.connect(DATABASE_URL)

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

class AddSourceRequest(BaseModel):
    url: str
    name: Optional[str] = None
    type: Optional[str] = "rss"

class AddSourceResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

class SourceListResponse(BaseModel):
    success: bool
    sources: list
    total: int

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

@app.get("/feed-manager", response_class=HTMLResponse)
async def feed_manager_page():
    """Página web para gerenciar feeds RSS"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/sources", response_model=SourceListResponse)
async def list_sources():
    """Lista todas as fontes RSS cadastradas"""
    try:
        conn = await get_db_connection()
        try:
            rows = await conn.fetch("""
                SELECT id, name, url, type, active, validation_score, 
                       validated_at, created_at
                FROM approved_sources
                ORDER BY created_at DESC
            """)
            
            sources = [dict(row) for row in rows]
            
            return SourceListResponse(
                success=True,
                sources=sources,
                total=len(sources)
            )
        finally:
            await conn.close()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sources/validate", response_model=AddSourceResponse)
async def validate_source(request: AddSourceRequest):
    """
    Valida uma fonte RSS/HTML antes de adicionar
    
    - Descobre RSS feed automaticamente
    - Suporta: Blogs, Reddit, YouTube
    - Testa scraping HTML como fallback
    - Retorna score de validação (0-10)
    - NÃO salva no banco (apenas valida)
    """
    try:
        from discover_rss_feeds import discover_rss_feed
        
        # Tenta descobrir RSS
        discovery_result = discover_rss_feed(request.url)
        
        validation_data = {
            "url": request.url,
            "rss_found": discovery_result.get("rss_found", []),
            "method": discovery_result.get("method"),
            "status": discovery_result.get("status"),
            "validation_score": 0,
            "can_scrape_html": False,
            "sample_news": [],
            "source_type": "blog"  # blog, reddit, youtube
        }
        
        # Detecta tipo de fonte
        if 'reddit.com/r/' in request.url.lower():
            validation_data["source_type"] = "reddit"
        elif 'youtube.com' in request.url.lower() or 'youtu.be' in request.url.lower():
            validation_data["source_type"] = "youtube"
        
        # Se encontrou RSS, testa
        if discovery_result["rss_found"]:
            best_feed = discovery_result["rss_found"][0]
            rss_url = best_feed["url"]
            
            # Define score baseado no tipo (mesmo sem testar scraping)
            if validation_data["source_type"] == "reddit":
                validation_data["validation_score"] = 9  # Reddit RSS é confiável
            elif validation_data["source_type"] == "youtube":
                validation_data["validation_score"] = 10  # YouTube RSS é perfeito
            else:
                validation_data["validation_score"] = 10  # Blog RSS é perfeito
            
            validation_data["recommended_url"] = rss_url
            validation_data["recommended_name"] = best_feed.get("title", request.name or "")
            
            # Tenta buscar exemplos (mas não falha se não encontrar)
            try:
                news_result = await scrape_news(rss_url, hours_window=168)  # 7 dias
                if news_result["news_list"]:
                    validation_data["sample_news"] = news_result["news_list"][:3]
            except Exception as e:
                print(f"Erro ao buscar exemplos: {e}")
                # Mantém score mesmo sem exemplos
        
        # Se não encontrou RSS, testa HTML scraping (apenas para blogs)
        elif validation_data["source_type"] == "blog":
            news_result = await scrape_news(request.url, hours_window=168)
            
            if news_result["news_list"]:
                validation_data["validation_score"] = 7  # Score menor para HTML
                validation_data["can_scrape_html"] = True
                validation_data["sample_news"] = news_result["news_list"][:3]
                validation_data["recommended_url"] = request.url
                validation_data["recommended_name"] = request.name or ""
        
        return AddSourceResponse(
            success=True,
            data=validation_data
        )
    
    except Exception as e:
        return AddSourceResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/sources/add", response_model=AddSourceResponse)
async def add_source(request: AddSourceRequest):
    """
    Adiciona uma nova fonte RSS ao banco de dados
    
    - Valida antes de adicionar
    - Salva em approved_sources
    - Retorna dados da fonte criada
    """
    try:
        # Valida primeiro
        validation = await validate_source(request)
        
        if not validation.success or validation.data["validation_score"] == 0:
            return AddSourceResponse(
                success=False,
                error="Fonte não passou na validação. Não foi possível extrair notícias."
            )
        
        # Prepara dados
        url_to_save = validation.data.get("recommended_url", request.url)
        name_to_save = validation.data.get("recommended_name", request.name or "")
        type_to_save = "rss" if validation.data["rss_found"] else "html"
        score = validation.data["validation_score"]
        
        # Salva no banco
        conn = await get_db_connection()
        try:
            # Verifica se já existe
            existing = await conn.fetchrow(
                "SELECT id FROM approved_sources WHERE url = $1",
                url_to_save
            )
            
            if existing:
                return AddSourceResponse(
                    success=False,
                    error="Esta fonte já está cadastrada."
                )
            
            # Insere
            row = await conn.fetchrow("""
                INSERT INTO approved_sources 
                (url, name, type, validation_score, validated_at, active, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, url, name, type, validation_score, validated_at, active, created_at
            """, url_to_save, name_to_save, type_to_save, score, 
                datetime.now(), True, datetime.now())
            
            return AddSourceResponse(
                success=True,
                data={
                    "source": dict(row),
                    "validation": validation.data
                }
            )
        
        finally:
            await conn.close()
    
    except Exception as e:
        return AddSourceResponse(
            success=False,
            error=str(e)
        )

@app.delete("/api/sources/{source_id}")
async def delete_source(source_id: int):
    """Deleta uma fonte RSS"""
    try:
        conn = await get_db_connection()
        try:
            result = await conn.execute(
                "DELETE FROM approved_sources WHERE id = $1",
                source_id
            )
            
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Fonte não encontrada")
            
            return {"success": True, "message": "Fonte deletada com sucesso"}
        
        finally:
            await conn.close()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/sources/{source_id}/toggle")
async def toggle_source(source_id: int):
    """Ativa/desativa uma fonte RSS"""
    try:
        conn = await get_db_connection()
        try:
            row = await conn.fetchrow(
                "UPDATE approved_sources SET active = NOT active WHERE id = $1 RETURNING active",
                source_id
            )
            
            if not row:
                raise HTTPException(status_code=404, detail="Fonte não encontrada")
            
            return {
                "success": True,
                "active": row["active"],
                "message": f"Fonte {'ativada' if row['active'] else 'desativada'} com sucesso"
            }
        
        finally:
            await conn.close()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
