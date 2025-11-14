# 📸 Sistema de Imagens de Celebridades

Sistema completo para buscar, analisar com IA e processar imagens de famosos para Instagram.

## 🎯 O que faz?

1. **Busca** imagens no Google Custom Search
2. **IA analisa** e escolhe a melhor (Gemini 2.5 Flash)
3. **Crop automático** para 1:1 (Instagram)
4. **Retorna base64** pronto para usar

## 🚀 Endpoint

```bash
POST /celebrity-image
```

### Request

```json
{
  "celebrity_name": "Jojo Todynho",
  "num_results": 5  // opcional, padrão: 5
}
```

### Response - Sucesso

```json
{
  "success": true,
  "data": {
    "celebrity": "Jojo Todynho",
    "images_found": 5,
    "best_image": {
      "url": "https://example.com/jojo.jpg",
      "reason": "Rosto claro, iluminação profissional, fundo neutro",
      "confidence": 0.95,
      "issues": []
    },
    "image_1x1_base64": "data:image/jpeg;base64,/9j/4AAQ...",
    "dimensions": {
      "original": {
        "width": 1920,
        "height": 1080
      },
      "cropped": {
        "width": 1080,
        "height": 1080
      }
    }
  },
  "error": null
}
```

### Response - Erro

```json
{
  "success": false,
  "data": {},
  "error": "Nenhuma imagem encontrada para 'Nome Inexistente'"
}
```

## 🔧 Configuração

### 1. Google Custom Search API

**Passo 1: Criar API Key**
1. Acesse: https://console.cloud.google.com/apis/credentials
2. Crie um projeto (se não tiver)
3. Clique em "Criar credenciais" → "Chave de API"
4. Copie a chave

**Passo 2: Criar Search Engine**
1. Acesse: https://programmablesearchengine.google.com/
2. Clique em "Add"
3. Nome: "Celebrity Image Search"
4. Sites to search: "Search the entire web"
5. Image search: ON
6. SafeSearch: ON
7. Copie o "Search engine ID"

**Passo 3: Configurar no .env**
```bash
GOOGLE_API_KEY=sua_api_key_aqui
GOOGLE_SEARCH_ENGINE_ID=seu_search_engine_id_aqui
```

### 2. OpenRouter API

Já configurado! Usando sua key:
```bash
OPENROUTER_API_KEY=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
```

## 💰 Custos

### Google Custom Search API
- **Grátis**: 100 buscas/dia
- **Pago**: $5 por 1000 buscas adicionais
- **Estimativa**: ~$15/mês para 10 posts/dia

### OpenRouter (Gemini 2.5 Flash)
- **Modelo**: `google/gemini-2.0-flash-exp:free`
- **Custo**: GRÁTIS! 🎉
- Limite: Razoável para uso moderado

**Total estimado: ~$15/mês** (apenas Google Search)

## 📖 Uso no n8n

### Workflow Completo

```
1. Scraper API (/scrape) → Extrai artigo
   ↓
2. Gemini → Extrai nome do famoso
   ↓
3. Scraper API (/celebrity-image) → Busca e processa imagem
   ↓
4. Microserviço Overlay → Adiciona texto
   ↓
5. Instagram → Posta
```

### Exemplo HTTP Request Node

```json
{
  "method": "POST",
  "url": "https://seu-scraper.com/celebrity-image",
  "authentication": "None",
  "sendBody": true,
  "bodyContentType": "json",
  "jsonBody": {
    "celebrity_name": "={{ $json.celebrity_name }}"
  }
}
```

### Processar Resposta

```javascript
// Code Node
const response = $json;

if (response.success) {
  return {
    json: {
      celebrity: response.data.celebrity,
      image_base64: response.data.image_1x1_base64,
      confidence: response.data.best_image.confidence,
      ai_reason: response.data.best_image.reason
    }
  };
}

// Se falhou, retorna vazio
return [];
```

## 🎨 Integração com seu Workflow Atual

### Adicionar ANTES do "Criar imagem"

```json
{
  "nodes": [
    {
      "name": "Extrair Famoso",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "parameters": {
        "promptType": "define",
        "text": "Analise este texto e extraia o nome da pessoa famosa mencionada. Se houver múltiplas, escolha a mais relevante. Retorne APENAS o nome, sem explicações: {{ $json.article_content }}"
      }
    },
    {
      "name": "Buscar Imagem Famoso",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://seu-scraper.com/celebrity-image",
        "jsonBody": {
          "celebrity_name": "={{ $json.output }}"
        }
      }
    },
    {
      "name": "IF - Tem Famoso?",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.success }}",
              "value2": true
            }
          ]
        }
      }
    }
  ]
}
```

### Fluxo Condicional

```
IF tem famoso mencionado?
  ├─ SIM → Usa imagem do famoso
  └─ NÃO → Gera imagem com Gemini (seu workflow atual)
```

## 🔍 Como a IA Escolhe

O Gemini analisa cada imagem com base em:

1. **Rosto claro e visível** (peso: 40%)
2. **Iluminação profissional** (peso: 25%)
3. **Fundo adequado** (peso: 15%)
4. **Sem watermarks** (peso: 10%)
5. **Expressão adequada** (peso: 5%)
6. **Qualidade geral** (peso: 5%)

### Exemplo de Análise

```json
{
  "best_index": 2,
  "confidence": 0.92,
  "reason": "Rosto perfeitamente iluminado, fundo neutro cinza, expressão profissional, alta resolução",
  "issues": ["pequeno logo no canto inferior direito"]
}
```

## 🎯 Casos de Uso

### 1. Notícia sobre Atleta

```
Artigo: "Cbum vence Mr. Olympia 2024"
  ↓
Busca: "Cbum official photo high quality"
  ↓
IA escolhe: Foto do pódio, iluminação dramática
  ↓
Crop 1:1 + Overlay com título
  ↓
Post Instagram
```

### 2. Fofoca Fitness

```
Artigo: "Jojo Todynho revela uso de anabolizantes"
  ↓
Busca: "Jojo Todynho official photo high quality"
  ↓
IA escolhe: Foto profissional, boa iluminação
  ↓
Crop 1:1 + Overlay com manchete
  ↓
Post Instagram
```

### 3. Entrevista com Especialista

```
Artigo: "Dr. Fulano explica suplementação"
  ↓
Busca: "Dr. Fulano official photo high quality"
  ↓
IA escolhe: Foto profissional em consultório
  ↓
Crop 1:1 + Overlay com citação
  ↓
Post Instagram
```

## ⚠️ Limitações

### O que NÃO funciona bem:

- ❌ Nomes muito genéricos ("João Silva")
- ❌ Pessoas não famosas (sem fotos públicas)
- ❌ Nomes com grafia incorreta
- ❌ Múltiplas pessoas com mesmo nome

### Soluções:

1. **Nome completo**: Use "Chris Bumstead" em vez de "Cbum"
2. **Contexto**: "Ramon Dino bodybuilder" em vez de só "Ramon"
3. **Fallback**: Se não achar, use imagem gerada

## 🧪 Testar Localmente

```bash
# Instalar Pillow
pip install Pillow==10.1.0

# Rodar servidor
python app.py

# Testar endpoint
curl -X POST http://localhost:8001/celebrity-image \
  -H "Content-Type: application/json" \
  -d '{"celebrity_name": "Jojo Todynho"}'
```

## 📊 Monitoramento

### Métricas Importantes

- Taxa de sucesso de busca
- Confidence média da IA
- Tempo de processamento
- Erros comuns

### Logs

```python
# O endpoint já loga automaticamente:
# - Celebridade buscada
# - Número de imagens encontradas
# - Confidence da escolha
# - Tempo de processamento
```

## 🔐 Segurança

### Boas Práticas

1. ✅ Nunca commite as API keys no Git
2. ✅ Use variáveis de ambiente
3. ✅ SafeSearch sempre ON
4. ✅ Valide nomes de entrada
5. ✅ Rate limiting no Google API

### Proteção contra Abuso

```python
# Adicione rate limiting se necessário
from fastapi import HTTPException
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/celebrity-image")
@limiter.limit("10/minute")
async def get_celebrity_image(...):
    ...
```

## 🚀 Próximas Melhorias

- [ ] Cache de imagens (evitar buscar mesma pessoa)
- [ ] Suporte a múltiplas pessoas
- [ ] Detecção automática de famosos no texto
- [ ] Fallback para Bing Image Search
- [ ] Filtros de qualidade mais avançados
- [ ] Suporte a GIFs/vídeos

## 📞 Suporte

Problemas? Abra uma issue no [GitHub](https://github.com/Folkz1/Scraper-reddit-youtube-blogs/issues)!

---

**Feito com ❤️ para criar posts virais no Instagram!** 🚀
