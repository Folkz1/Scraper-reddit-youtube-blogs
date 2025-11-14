# 📋 Formatos de Resposta da API

Documentação completa de todos os JSONs possíveis retornados pela API.

## 🎯 Estrutura Base

Todas as respostas seguem este formato:

```json
{
  "success": boolean,
  "type": "article" | "youtube" | "reddit",
  "data": {},
  "error": string | null
}
```

---

## 📰 Artigo Web (Article)

### Request
```json
{
  "url": "https://exemplo.com/artigo",
  "type": "article"
}
```

### Response - Sucesso
```json
{
  "success": true,
  "type": "article",
  "data": {
    "title": "Monster enters the female-focused energy game with FLRT",
    "content": "Monster Beverage is joining the female-focused energy drink movement with FLRT, a new zero-sugar brand launching in late Q1 2026. Each 12-ounce can contains 200mg of caffeine and skips artificial colors and flavors...",
    "url": "https://wellworthy.com/monster-enters-the-female-focused-energy-game-with-flrt/",
    "word_count": 144,
    "author": "John Doe",
    "date": "2024-01-15",
    "language": "en"
  },
  "error": null
}
```

### Campos do Article

| Campo | Tipo | Descrição | Pode ser null? |
|-------|------|-----------|----------------|
| `title` | string | Título do artigo | Não |
| `content` | string | Conteúdo completo extraído | Não |
| `url` | string | URL original | Não |
| `word_count` | number | Contagem de palavras | Não |
| `author` | string | Autor do artigo | Sim |
| `date` | string | Data de publicação (ISO) | Sim |
| `language` | string | Idioma detectado | Não |

---

## 🎥 YouTube

### Request
```json
{
  "url": "https://www.youtube.com/watch?v=8jPQjjsBbIc",
  "type": "youtube"
}
```

### Response - Sucesso
```json
{
  "success": true,
  "type": "youtube",
  "data": {
    "title": "How to stay calm when you know you'll be stressed | Daniel Levitin | TED",
    "video_id": "8jPQjjsBbIc",
    "transcript": "Tradutor: Paulo Ludwig Revisor: Fernando Gonçalves Há alguns anos, invadi minha própria casa. Tinha acabado de chegar, era cerca de meia noite no inverno de Montreal...",
    "duration_scraped": 179.13,
    "language": "Portuguese (Brazil)",
    "language_code": "pt-BR",
    "is_auto_generated": false,
    "url": "https://www.youtube.com/watch?v=8jPQjjsBbIc",
    "word_count": 453,
    "channel": "TED",
    "duration_total": 720
  },
  "error": null
}
```

### Campos do YouTube

| Campo | Tipo | Descrição | Pode ser null? |
|-------|------|-----------|----------------|
| `title` | string | Título do vídeo | Não |
| `video_id` | string | ID do vídeo no YouTube | Não |
| `transcript` | string | Transcrição dos primeiros 3 minutos | Não |
| `duration_scraped` | number | Duração extraída em segundos (máx 180) | Não |
| `language` | string | Nome do idioma | Não |
| `language_code` | string | Código do idioma (pt-BR, en, etc) | Não |
| `is_auto_generated` | boolean | Se é legenda automática ou manual | Não |
| `url` | string | URL original | Não |
| `word_count` | number | Contagem de palavras da transcrição | Não |
| `channel` | string | Nome do canal | Não |
| `duration_total` | number | Duração total do vídeo em segundos | Não |

---

## 🔴 Reddit

### Request
```json
{
  "url": "https://www.reddit.com/r/Python/comments/1h0ixwi/what_are_you_working_on_this_week/",
  "type": "reddit",
  "max_comments": 5,
  "sort_comments": "top"
}
```

### Response - Sucesso
```json
{
  "success": true,
  "type": "reddit",
  "data": {
    "title": "What are you working on this week?",
    "author": "AutoModerator",
    "subreddit": "Python",
    "selftext": "Tell /r/python what you're working on this week! You can be bragging, grousing, sharing your passion, or explaining your pain. Talk about your current project or your pet project; whatever you want to share.",
    "url": "https://www.reddit.com/r/Python/comments/1h0ixwi/what_are_you_working_on_this_week/",
    "score": 42,
    "upvote_ratio": 0.95,
    "num_comments": 87,
    "created_utc": "2024-11-14T10:00:00",
    "is_self": true,
    "link_url": null,
    "comments": [
      {
        "author": "user123",
        "body": "I'm building a web scraper using BeautifulSoup and it's going great! Learning a lot about HTML parsing.",
        "score": 15,
        "created_utc": "2024-11-14T11:30:00",
        "replies_count": 3
      },
      {
        "author": "pythondev",
        "body": "Working on a FastAPI project for my company. Really enjoying the async capabilities!",
        "score": 12,
        "created_utc": "2024-11-14T12:00:00",
        "replies_count": 1
      }
    ],
    "word_count": 245
  },
  "error": null
}
```

### Campos do Reddit

| Campo | Tipo | Descrição | Pode ser null? |
|-------|------|-----------|----------------|
| `title` | string | Título do post | Não |
| `author` | string | Autor do post | Não |
| `subreddit` | string | Nome do subreddit (sem r/) | Não |
| `selftext` | string | Conteúdo do post (se for texto) | Sim |
| `url` | string | URL original | Não |
| `score` | number | Upvotes - downvotes | Não |
| `upvote_ratio` | number | Ratio de upvotes (0-1) | Não |
| `num_comments` | number | Total de comentários | Não |
| `created_utc` | string | Data de criação (ISO) | Não |
| `is_self` | boolean | Se é post de texto (true) ou link (false) | Não |
| `link_url` | string | URL externa se for post de link | Sim |
| `comments` | array | Array de comentários | Não |
| `word_count` | number | Total de palavras (post + comentários) | Não |

### Estrutura de Comentário

```json
{
  "author": "username",
  "body": "Texto do comentário...",
  "score": 15,
  "created_utc": "2024-11-14T11:30:00",
  "replies_count": 3
}
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `author` | string | Autor do comentário |
| `body` | string | Texto do comentário |
| `score` | number | Upvotes do comentário |
| `created_utc` | string | Data de criação (ISO) |
| `replies_count` | number | Número de respostas |

---

## ❌ Resposta de Erro

### Quando o scraping falha

```json
{
  "success": false,
  "type": "article",
  "data": {},
  "error": "Erro ao buscar página: Connection timeout"
}
```

### Tipos de Erro Comuns

**Artigos:**
```json
{
  "success": false,
  "type": "article",
  "data": {},
  "error": "Não foi possível baixar a página"
}
```

**YouTube:**
```json
{
  "success": false,
  "type": "youtube",
  "data": {},
  "error": "Este vídeo não possui legendas/transcrições disponíveis"
}
```

**Reddit:**
```json
{
  "success": false,
  "type": "reddit",
  "data": {},
  "error": "Post não encontrado ou foi deletado"
}
```

**URL Inválida:**
```json
{
  "success": false,
  "type": "unknown",
  "data": {},
  "error": "URL do YouTube inválida"
}
```

---

## 🔄 Auto-detecção

Quando `type: "auto"`, a API detecta automaticamente:

### Request
```json
{
  "url": "https://www.youtube.com/watch?v=abc123",
  "type": "auto"
}
```

### Response
```json
{
  "success": true,
  "type": "youtube",  // ← Tipo detectado automaticamente
  "data": { /* ... */ }
}
```

### Regras de Detecção

| URL contém | Tipo detectado |
|------------|----------------|
| `youtube.com/watch` ou `youtu.be/` | `youtube` |
| `reddit.com/r/` + `/comments/` | `reddit` |
| Qualquer outra | `article` |

---

## 📊 Exemplos de Uso no n8n

### Processar Resposta de Artigo

```javascript
// Code Node
const response = $json;

if (response.success) {
  return {
    json: {
      title: response.data.title,
      content: response.data.content,
      summary: response.data.content.substring(0, 200) + '...',
      wordCount: response.data.word_count,
      author: response.data.author || 'Desconhecido'
    }
  };
}

// Retorna vazio se falhou
return [];
```

### Processar Resposta de YouTube

```javascript
// Code Node
const response = $json;

if (response.success && response.type === 'youtube') {
  return {
    json: {
      videoTitle: response.data.title,
      transcript: response.data.transcript,
      duration: `${Math.floor(response.data.duration_scraped / 60)}min`,
      language: response.data.language,
      channel: response.data.channel
    }
  };
}

return [];
```

### Processar Resposta de Reddit

```javascript
// Code Node
const response = $json;

if (response.success && response.type === 'reddit') {
  const data = response.data;
  
  // Formata comentários
  const topComments = data.comments
    .slice(0, 3)
    .map(c => `${c.author} (${c.score} upvotes): ${c.body}`)
    .join('\n\n');
  
  return {
    json: {
      title: data.title,
      subreddit: `r/${data.subreddit}`,
      score: data.score,
      postContent: data.selftext,
      topComments: topComments,
      totalComments: data.num_comments
    }
  };
}

return [];
```

---

## 🎨 Campos Opcionais vs Obrigatórios

### Sempre Presentes (em caso de sucesso)

- ✅ `success` (boolean)
- ✅ `type` (string)
- ✅ `data.title` (string)
- ✅ `data.url` (string)
- ✅ `data.word_count` (number)

### Podem ser null/undefined

- ❓ `data.author` (article)
- ❓ `data.date` (article)
- ❓ `data.selftext` (reddit - vazio se for link)
- ❓ `data.link_url` (reddit - null se for texto)
- ❓ `error` (null quando success=true)

---

## 🔍 Validação de Resposta

### TypeScript Interface

```typescript
interface ScraperResponse {
  success: boolean;
  type: 'article' | 'youtube' | 'reddit';
  data: ArticleData | YouTubeData | RedditData;
  error: string | null;
}

interface ArticleData {
  title: string;
  content: string;
  url: string;
  word_count: number;
  author?: string;
  date?: string;
  language: string;
}

interface YouTubeData {
  title: string;
  video_id: string;
  transcript: string;
  duration_scraped: number;
  language: string;
  language_code: string;
  is_auto_generated: boolean;
  url: string;
  word_count: number;
  channel: string;
  duration_total: number;
}

interface RedditData {
  title: string;
  author: string;
  subreddit: string;
  selftext: string;
  url: string;
  score: number;
  upvote_ratio: number;
  num_comments: number;
  created_utc: string;
  is_self: boolean;
  link_url: string | null;
  comments: RedditComment[];
  word_count: number;
}

interface RedditComment {
  author: string;
  body: string;
  score: number;
  created_utc: string;
  replies_count: number;
}
```

---

## 📞 Suporte

Dúvidas sobre os formatos? Abra uma issue no [GitHub](https://github.com/Folkz1/Scraper-reddit-youtube-blogs/issues)!
