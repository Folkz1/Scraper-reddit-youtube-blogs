# 🚀 Microserviço de Scraper - Comece Aqui

## ✨ O que é?

API REST para extrair conteúdo de:
- 📰 **Artigos web** - Qualquer blog/site
- 🎥 **YouTube** - Transcrição dos primeiros 3 minutos
- 🔴 **Reddit** - Posts e comentários

## 🎯 Por que usar?

Substitui aquele código JavaScript complexo e frágil do n8n por uma API simples e confiável.

**Antes (n8n):**
```javascript
// 200 linhas de regex frágil que quebra com cada site diferente
const html = $input.first().json.data || '';
function getFirstMatch(regex, str) { ... }
// ... mais 150 linhas ...
```

**Depois (n8n):**
```json
{
  "method": "POST",
  "url": "http://seu-vps:8001/scrape",
  "body": {
    "url": "{{ $json.article_url }}"
  }
}
```

## 🏃 Quick Start

### 1️⃣ Testar Localmente (2 minutos)

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
python app.py

# Em outro terminal, testar
python test.py
```

Acesse: http://localhost:8001/docs

### 2️⃣ Deploy na VPS (5 minutos)

```bash
# Na VPS
git clone seu-repo
cd microservico_scraper

# Com Docker
docker-compose up -d

# Testar
curl http://localhost:8001/health
```

Veja guia completo: [DEPLOY_VPS.md](DEPLOY_VPS.md)

## 📖 Como Usar

### Endpoint Principal

```bash
POST /scrape
```

### Exemplos

**Auto-detecção (recomendado):**
```bash
curl -X POST http://localhost:8001/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://exemplo.com/artigo"}'
```

**Artigo web:**
```json
{
  "url": "https://wellworthy.com/monster-enters-the-female-focused-energy-game-with-flrt/",
  "type": "article"
}
```

**YouTube (primeiros 3 minutos):**
```json
{
  "url": "https://www.youtube.com/watch?v=8jPQjjsBbIc",
  "type": "youtube"
}
```

**Reddit (top 10 comentários):**
```json
{
  "url": "https://www.reddit.com/r/Python/comments/abc123/titulo/",
  "type": "reddit",
  "max_comments": 10,
  "sort_comments": "top"
}
```

### Respostas

**Sucesso:**
```json
{
  "success": true,
  "type": "article",
  "data": {
    "title": "Título do artigo",
    "content": "Conteúdo extraído...",
    "word_count": 1500,
    "url": "https://..."
  }
}
```

**Erro:**
```json
{
  "success": false,
  "type": "article",
  "data": {},
  "error": "Descrição do erro"
}
```

## 🔧 Configuração

### Reddit (Opcional)

Para melhor performance no Reddit, crie credenciais:

1. Acesse: https://www.reddit.com/prefs/apps
2. Clique em "create another app..."
3. Escolha "script"
4. Configure no `.env`:

```bash
REDDIT_CLIENT_ID=seu_id
REDDIT_CLIENT_SECRET=seu_secret
REDDIT_USER_AGENT=ScraperBot/1.0
```

**Nota:** Funciona sem credenciais para uso básico!

## 📊 Estrutura do Projeto

```
microservico_scraper/
├── app.py                    # FastAPI app principal
├── requirements.txt          # Dependências
├── Dockerfile               # Container Docker
├── docker-compose.yml       # Orquestração
├── .env.example            # Exemplo de configuração
├── scrapers/
│   ├── web_scraper.py      # Artigos (trafilatura)
│   ├── youtube_scraper.py  # YouTube (yt-dlp)
│   └── reddit_scraper.py   # Reddit (praw)
├── test.py                 # Testes gerais
├── test_reddit.py          # Teste específico Reddit
├── README.md               # Documentação completa
├── DEPLOY_VPS.md          # Guia de deploy
└── COMECE_AQUI.md         # Este arquivo
```

## 🎨 Tecnologias

- **FastAPI** - Framework web moderno
- **trafilatura** - Extração inteligente de artigos
- **yt-dlp** - Download de legendas do YouTube
- **praw** - API oficial do Reddit
- **Docker** - Containerização

## 🔥 Features

✅ Auto-detecção de tipo de URL
✅ Extração inteligente de conteúdo
✅ Suporte a múltiplos idiomas
✅ Legendas automáticas do YouTube
✅ Top comentários do Reddit
✅ API REST documentada (Swagger)
✅ Docker ready
✅ Fácil de deployar

## 📚 Documentação

- **README.md** - Documentação completa da API
- **DEPLOY_VPS.md** - Guia de deploy na VPS
- **Swagger UI** - http://localhost:8001/docs (quando rodando)

## 🧪 Testes

```bash
# Teste geral (artigos + YouTube)
python test.py

# Teste específico Reddit
python test_reddit.py

# Teste direto YouTube
python test_youtube_direct.py
```

## 🌐 Uso no n8n

### HTTP Request Node

```json
{
  "method": "POST",
  "url": "http://seu-vps:8001/scrape",
  "authentication": "None",
  "requestMethod": "POST",
  "sendBody": true,
  "bodyContentType": "json",
  "jsonBody": {
    "url": "={{ $json.article_url }}"
  }
}
```

### Processar Resposta

```javascript
// Acessar dados
const title = $json.data.title;
const content = $json.data.content;
const wordCount = $json.data.word_count;

// Verificar sucesso
if ($json.success) {
  return $json.data;
} else {
  throw new Error($json.error);
}
```

## 🆘 Troubleshooting

### Porta 8001 em uso
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux
sudo lsof -i :8001
sudo kill -9 <PID>
```

### YouTube não funciona
- Alguns vídeos não têm legendas
- YouTube pode bloquear IPs de VPS
- Tente com vídeos populares (TED Talks, etc)

### Reddit não funciona
- Verifique credenciais no `.env`
- Funciona sem credenciais para leitura básica
- Limite de rate: ~60 requests/minuto sem auth

## 💡 Próximos Passos

1. ✅ Testar localmente
2. ✅ Fazer deploy na VPS
3. ✅ Integrar com n8n
4. ✅ Criar workflow de newsletter
5. 🚀 Profit!

## 🤝 Suporte

- Documentação: [README.md](README.md)
- Deploy: [DEPLOY_VPS.md](DEPLOY_VPS.md)
- API Docs: http://localhost:8001/docs

---

**Pronto para começar?** Execute `python app.py` e acesse http://localhost:8001/docs! 🚀
