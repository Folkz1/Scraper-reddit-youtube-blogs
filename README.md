# 🔍 Scraper API - Reddit, YouTube & Blogs

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

API REST simples e poderosa para extrair conteúdo de artigos web, vídeos do YouTube e posts do Reddit. Perfeita para integração com n8n, Make, Zapier ou qualquer automação.

## ✨ Features

- 📰 **Artigos Web** - Extração inteligente de qualquer blog/site usando trafilatura
- 🎥 **YouTube** - Transcrição automática de vídeos (primeiros 3 minutos)
- 🔴 **Reddit** - Posts completos com top comentários
- 🤖 **Auto-detecção** - Identifica automaticamente o tipo de URL
- ⚡ **FastAPI** - API REST rápida com documentação automática (Swagger)
- 🐳 **Docker Ready** - Deploy fácil com Docker Compose
- 🌍 **Multi-idioma** - Suporte a português, inglês e outros idiomas

## 🎯 Por que usar?

Substitui código complexo e frágil por uma API simples e confiável:

**Antes:**
```javascript
// 200+ linhas de regex frágil que quebra com cada site diferente
const html = $input.first().json.data || '';
function extractContent(html) { /* ... */ }
```

**Depois:**
```bash
curl -X POST http://localhost:8001/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://exemplo.com/artigo"}'
```

## 🚀 Quick Start

### Opção 1: Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/Folkz1/Scraper-reddit-youtube-blogs.git
cd Scraper-reddit-youtube-blogs

# Rode com Docker Compose
docker-compose up -d

# Acesse a documentação
open http://localhost:8001/docs
```

### Opção 2: Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
python app.py

# Acesse: http://localhost:8001
```

## 📸 Screenshots

### Swagger UI (Documentação Interativa)
Acesse `http://localhost:8001/docs` para testar a API diretamente no navegador.

### Exemplo de Resposta

```json
{
  "success": true,
  "type": "article",
  "data": {
    "title": "Monster enters the female-focused energy game with FLRT",
    "content": "Monster Beverage is joining the female-focused energy drink movement...",
    "word_count": 144,
    "author": "John Doe",
    "language": "en"
  }
}
```

## 🐳 Docker

```bash
# Build
docker build -t scraper-api .

# Run
docker run -p 8001:8001 scraper-api
```

## 📖 Uso

### Endpoint Principal

```bash
POST /scrape
Content-Type: application/json

{
  "url": "https://exemplo.com/artigo",
  "type": "auto",  # auto, article, youtube, reddit
  "max_comments": 10,  # apenas para Reddit
  "sort_comments": "top"  # top, best, new, controversial
}
```

### Exemplos

**Artigo Web:**
```bash
curl -X POST http://localhost:8001/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://wellworthy.com/monster-enters-the-female-focused-energy-game-with-flrt/"}'
```

**YouTube:**
```bash
curl -X POST http://localhost:8001/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=UF8uR6Z6KLc"}'
```

**Reddit:**
```bash
curl -X POST http://localhost:8001/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.reddit.com/r/programming/comments/abc123/titulo/",
    "max_comments": 5
  }'
```

## 🧪 Testes

```bash
# Certifique-se que a API está rodando
python app.py

# Em outro terminal
python test.py
```

## 🔑 Configuração Reddit (Opcional)

Para melhor performance no Reddit, crie credenciais:

1. Acesse: https://www.reddit.com/prefs/apps
2. Clique em "create another app..."
3. Escolha "script"
4. Copie client_id e client_secret
5. Configure no `.env`:

```bash
REDDIT_CLIENT_ID=seu_client_id
REDDIT_CLIENT_SECRET=seu_secret
REDDIT_USER_AGENT=ScraperBot/1.0
```

**Nota:** Funciona sem credenciais para uso básico!

## 📊 Respostas

### Artigo Web
```json
{
  "success": true,
  "type": "article",
  "data": {
    "title": "Título do artigo",
    "content": "Conteúdo extraído...",
    "url": "https://...",
    "word_count": 1500,
    "author": "Nome do autor",
    "date": "2024-01-15",
    "language": "pt"
  }
}
```

### YouTube
```json
{
  "success": true,
  "type": "youtube",
  "data": {
    "title": "Título do vídeo",
    "video_id": "abc123",
    "transcript": "Transcrição...",
    "duration_scraped": 180,
    "language": "Portuguese",
    "language_code": "pt",
    "is_auto_generated": false,
    "word_count": 450
  }
}
```

### Reddit
```json
{
  "success": true,
  "type": "reddit",
  "data": {
    "title": "Título do post",
    "author": "username",
    "subreddit": "programming",
    "selftext": "Conteúdo do post...",
    "score": 1234,
    "num_comments": 56,
    "comments": [
      {
        "author": "user1",
        "body": "Comentário...",
        "score": 89,
        "created_utc": "2024-01-15T10:30:00"
      }
    ]
  }
}
```

## 🌐 Deploy VPS

```bash
# Na VPS
git clone seu-repo
cd microservico_scraper

# Com Docker
docker build -t scraper-api .
docker run -d -p 8001:8001 --name scraper scraper-api

# Ou direto
pip install -r requirements.txt
nohup python app.py &
```

## 📚 Documentação

- **[COMECE_AQUI.md](COMECE_AQUI.md)** - Guia rápido de início
- **[DEPLOY_VPS.md](DEPLOY_VPS.md)** - Deploy completo na VPS
- **[EXEMPLOS_N8N.md](EXEMPLOS_N8N.md)** - Integração com n8n
- **Swagger UI** - http://localhost:8001/docs (documentação interativa)

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

## 📝 Roadmap

- [ ] Suporte a Twitter/X
- [ ] Suporte a LinkedIn
- [ ] Cache de resultados (Redis)
- [ ] Rate limiting
- [ ] Webhook para processar em background
- [ ] Suporte a PDFs
- [ ] API de batch processing

## ⭐ Star History

Se este projeto te ajudou, considere dar uma ⭐!

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🙏 Agradecimentos

- [trafilatura](https://github.com/adbar/trafilatura) - Extração de artigos
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Download de legendas do YouTube
- [praw](https://github.com/praw-dev/praw) - Reddit API
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web

---

**Feito com ❤️ para a comunidade de automação**
