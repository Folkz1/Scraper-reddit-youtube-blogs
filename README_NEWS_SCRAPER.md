# 📰 News Scraper - RSS + Fallback HTML

Endpoint para scraping de notícias com suporte a RSS feeds e fallback para scraping HTML quando RSS não está disponível.

## 🎯 O que faz

1. **Tenta RSS primeiro** (alta confiabilidade)
2. **Fallback para HTML** se RSS falhar
3. **Filtra por data** (últimas 24h por padrão)
4. **Remove duplicatas** baseado em links já processados
5. **Normaliza dados** em formato consistente

## 🚀 Como usar

### Endpoint

```
POST /scrape-news
```

### Payload

```json
{
  "url": "https://www.foodnavigator-usa.com/arc/outboundfeeds/rss/",
  "existing_links": [],
  "hours_window": 24,
  "max_summary_length": 500
}
```

### Parâmetros

- `url` (obrigatório): URL do RSS feed ou blog
- `existing_links` (opcional): Array de URLs já processadas
- `hours_window` (opcional): Janela de tempo em horas (padrão: 24)
- `max_summary_length` (opcional): Tamanho máximo do resumo (padrão: 500)

### Resposta

```json
{
  "success": true,
  "data": {
    "news_list": [
      {
        "title": "Título da notícia",
        "url": "https://...",
        "summary": "Resumo da notícia...",
        "pubDate": "2025-11-19T10:30:00",
        "source": "Nome da fonte"
      }
    ],
    "total_found": 20,
    "total_unique": 15,
    "source_type": "rss",
    "hours_window": 24,
    "url": "https://..."
  },
  "error": null
}
```

## 📊 Feeds Descobertos

### ✅ Feeds RSS Validados (Novos)

1. **Lifespan.io Life Extension News**
   - URL: `https://www.lifespan.io/news/category/life-extension-news/feed/`
   - Status: ✅ Validado (10 entries)

2. **FoodNavigator USA**
   - URL: `https://www.foodnavigator-usa.com/arc/outboundfeeds/rss/`
   - Status: ✅ Validado (20 entries)

### ⚠️ Sites que Precisam HTML Scraping

Estes sites não têm RSS público ou estão bloqueados:

1. **Nutrition UK News**
   - URL: `https://www.nutrition.org.uk/news`
   - Método: HTML scraping

2. **MobiHealthNews South Korea**
   - URL: `https://www.mobihealthnews.com/tag/south-korea`
   - Método: HTML scraping

3. **Medical Korea Latest News**
   - URL: `https://www.medicalkorea.or.kr/en/latestnews`
   - Método: HTML scraping

4. **Blue Zones**
   - URL: `https://www.bluezones.com`
   - Método: HTML scraping

5. **New Nutrition**
   - URL: `https://www.new-nutrition.com`
   - Método: HTML scraping

### 📋 Feeds Já no Banco (18 feeds)

Veja `feeds_final_para_n8n.json` para lista completa.

## 🧪 Testando

### 1. Inicie o microserviço

```bash
cd microservico_scraper
python app.py
```

### 2. Execute os testes

```bash
python test_news_scraper.py
```

### 3. Teste manual com curl

```bash
curl -X POST http://localhost:8001/scrape-news \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://lifespan.io/feed",
    "hours_window": 24
  }'
```

## 📝 Exemplo de Uso no n8n

### Node 1: Buscar Links Existentes (Postgres)

```sql
SELECT json_agg(source_news_url) AS links
FROM instagram_posts
WHERE created_at >= date_trunc('day', NOW())
  AND created_at < date_trunc('day', NOW()) + INTERVAL '1 day';
```

### Node 2: HTTP Request ao Microserviço

```json
{
  "method": "POST",
  "url": "http://localhost:8001/scrape-news",
  "body": {
    "url": "{{ $json.rss_url }}",
    "existing_links": "{{ $('Buscar Links').first().json.links || [] }}",
    "hours_window": 24,
    "max_summary_length": 200
  }
}
```

### Node 3: Processar Resposta

```javascript
const response = $input.first().json;

if (response.success) {
  const newsList = response.data.news_list;
  
  return newsList.map(news => ({
    json: {
      title: news.title,
      url: news.url,
      summary: news.summary,
      pubDate: news.pubDate,
      source: news.source,
      source_type: response.data.source_type
    }
  }));
}

return [];
```

## 🔧 Configuração

### Dependências

Adicione ao `requirements.txt`:

```
feedparser==6.0.10
```

Instale:

```bash
pip install feedparser
```

### Estrutura de Arquivos

```
microservico_scraper/
├── app.py                          # API principal (endpoint adicionado)
├── scrapers/
│   └── news_scraper.py            # Lógica de scraping
├── test_news_scraper.py           # Testes
├── feeds_final_para_n8n.json      # Lista completa de feeds
└── README_NEWS_SCRAPER.md         # Esta documentação
```

## 💡 Dicas

### Alta Confiabilidade

Para máxima confiabilidade, **sempre use RSS feeds** quando disponíveis:

- WordPress: `/feed` ou `/feed/`
- Categorias: `/category/nome/feed/`
- Tags: `/tag/nome/feed`

### Descobrir RSS Automaticamente

Use o script `discover_rss_feeds.py` para encontrar feeds:

```bash
python discover_rss_feeds.py
```

### Fallback HTML

O scraping HTML funciona melhor em:
- Sites WordPress
- Blogs com estrutura semântica (`<article>`, `<time>`)
- Sites com classes CSS descritivas

Pode falhar em:
- Sites com JavaScript pesado (SPA)
- Sites com proteção anti-bot
- Estruturas HTML não padronizadas

## 🎯 Próximos Passos

1. ✅ Adicionar os 2 novos feeds validados ao banco
2. ⚠️ Testar HTML scraping nos 5 sites sem RSS
3. 🔄 Integrar com workflow n8n existente
4. 📊 Monitorar taxa de sucesso por fonte

## 📞 Suporte

Se um feed não funcionar:

1. Verifique se a URL está correta
2. Teste manualmente no navegador
3. Use `validate_all_feeds.py` para debug
4. Considere usar HTML scraping como fallback
