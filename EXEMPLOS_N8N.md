# 🔗 Integração com n8n

Exemplos práticos de como usar o Scraper API no n8n.

## 📋 Workflow Básico

### 1. HTTP Request Node

Configuração básica para scraping:

```json
{
  "method": "POST",
  "url": "http://seu-vps:8001/scrape",
  "authentication": "None",
  "sendBody": true,
  "bodyContentType": "json",
  "jsonBody": "={{ $json }}"
}
```

### 2. Body do Request

```json
{
  "url": "={{ $json.article_url }}",
  "type": "auto"
}
```

## 🎯 Casos de Uso

### Newsletter Automática

**Workflow:**
1. **Webhook** - Recebe lista de URLs
2. **Split In Batches** - Processa URLs em lotes
3. **HTTP Request** - Scraper API
4. **Code** - Processa resposta
5. **OpenAI** - Gera resumo
6. **Email** - Envia newsletter

**HTTP Request (Scraper):**
```json
{
  "method": "POST",
  "url": "http://seu-vps:8001/scrape",
  "body": {
    "url": "={{ $json.url }}"
  }
}
```

**Code Node (Processar):**
```javascript
// Verifica se scraping foi bem-sucedido
if (!$json.success) {
  return [];
}

// Extrai dados
const data = $json.data;

return {
  json: {
    title: data.title,
    content: data.content,
    word_count: data.word_count,
    url: data.url,
    type: $json.type
  }
};
```

### Monitoramento de Reddit

**Workflow:**
1. **Schedule Trigger** - A cada hora
2. **HTTP Request** - Busca posts do Reddit
3. **Filter** - Filtra por score mínimo
4. **HTTP Request** - Scraper API
5. **Slack** - Notifica time

**Scraper Request:**
```json
{
  "url": "={{ $json.reddit_url }}",
  "type": "reddit",
  "max_comments": 10,
  "sort_comments": "top"
}
```

**Filter Node:**
```javascript
// Apenas posts com mais de 100 upvotes
return $json.data.score > 100;
```

### Transcrição de YouTube

**Workflow:**
1. **Webhook** - Recebe URL do YouTube
2. **HTTP Request** - Scraper API
3. **OpenAI** - Analisa transcrição
4. **Google Sheets** - Salva resultado

**Scraper Request:**
```json
{
  "url": "={{ $json.youtube_url }}",
  "type": "youtube"
}
```

**OpenAI Prompt:**
```
Analise esta transcrição de vídeo e extraia:
1. Principais pontos discutidos
2. Conclusões
3. Ações recomendadas

Transcrição:
{{ $json.data.transcript }}
```

## 🔄 Tratamento de Erros

### Error Workflow

```javascript
// No Code Node após HTTP Request
if (!$json.success) {
  // Log do erro
  console.error('Scraping falhou:', $json.error);
  
  // Retorna estrutura padrão
  return {
    json: {
      title: 'Erro ao fazer scraping',
      content: '',
      error: $json.error,
      url: $input.first().json.url
    }
  };
}

return $json.data;
```

### Retry Logic

Configure no HTTP Request Node:
- **Retry On Fail**: true
- **Max Tries**: 3
- **Wait Between Tries**: 1000ms

## 📊 Exemplos Completos

### 1. Agregador de Notícias

```json
{
  "nodes": [
    {
      "name": "Lista de URLs",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "return [\n  {json: {url: 'https://techcrunch.com/...'}},\n  {json: {url: 'https://arstechnica.com/...'}}\n];"
      }
    },
    {
      "name": "Scraper API",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8001/scrape",
        "jsonBody": "={{ {\"url\": $json.url} }}"
      }
    },
    {
      "name": "Processar",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "if ($json.success) {\n  return {\n    json: {\n      title: $json.data.title,\n      summary: $json.data.content.substring(0, 200) + '...',\n      url: $json.data.url\n    }\n  };\n}\nreturn [];"
      }
    }
  ]
}
```

### 2. Monitor de Subreddit

```json
{
  "nodes": [
    {
      "name": "Schedule",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hoursInterval": 1}]
        }
      }
    },
    {
      "name": "Reddit Posts",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://www.reddit.com/r/programming/hot.json?limit=10"
      }
    },
    {
      "name": "Loop Posts",
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": {
        "batchSize": 1
      }
    },
    {
      "name": "Scraper",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8001/scrape",
        "jsonBody": "={{ {\"url\": $json.data.url, \"type\": \"reddit\", \"max_comments\": 5} }}"
      }
    }
  ]
}
```

## 🎨 Dicas e Truques

### 1. Cache de Resultados

Use o **Cache Node** do n8n para evitar scraping duplicado:

```javascript
// Antes do HTTP Request
const cacheKey = `scraper_${$json.url}`;
const cached = $cache.get(cacheKey);

if (cached) {
  return {json: cached};
}

// Depois do Scraper
if ($json.success) {
  $cache.set(cacheKey, $json.data, 3600); // 1 hora
}
```

### 2. Batch Processing

Para processar muitas URLs:

```javascript
// Split In Batches Node
{
  "batchSize": 5,
  "options": {
    "reset": false
  }
}
```

### 3. Timeout Handling

```javascript
// HTTP Request Node
{
  "timeout": 30000,  // 30 segundos
  "ignoreResponseCode": true
}
```

### 4. Formatação de Conteúdo

```javascript
// Code Node - Limpar HTML residual
const content = $json.data.content
  .replace(/\s+/g, ' ')  // Remove espaços múltiplos
  .replace(/\n{3,}/g, '\n\n')  // Remove quebras múltiplas
  .trim();

return {
  json: {
    ...$json.data,
    content: content
  }
};
```

## 🔐 Autenticação (Opcional)

Se você adicionar autenticação na API:

```json
{
  "authentication": "headerAuth",
  "headerAuth": {
    "name": "Authorization",
    "value": "Bearer seu-token-aqui"
  }
}
```

## 📈 Monitoramento

### Webhook de Status

Crie um workflow que monitora a saúde da API:

```json
{
  "nodes": [
    {
      "name": "Schedule",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "minutes", "minutesInterval": 5}]
        }
      }
    },
    {
      "name": "Health Check",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://seu-vps:8001/health"
      }
    },
    {
      "name": "Check Status",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.status }}",
              "value2": "healthy"
            }
          ]
        }
      }
    },
    {
      "name": "Alert",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "text": "⚠️ Scraper API está offline!"
      }
    }
  ]
}
```

## 🚀 Performance

### Paralelização

Use **Execute Workflow** para processar em paralelo:

1. Workflow principal divide URLs
2. Sub-workflow processa cada URL
3. Merge dos resultados

### Rate Limiting

```javascript
// Code Node - Delay entre requests
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
await delay(1000);  // 1 segundo entre requests
```

## 📞 Suporte

Problemas com a integração? Abra uma issue no [GitHub](https://github.com/Folkz1/Scraper-reddit-youtube-blogs/issues)!
