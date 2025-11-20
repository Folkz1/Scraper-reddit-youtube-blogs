# 🗞️ Gerenciador de Feeds RSS - Documentação

## 📋 Visão Geral

Interface web para adicionar e gerenciar fontes de notícias RSS automaticamente. O sistema:

✅ Descobre RSS feeds automaticamente  
✅ Valida se consegue extrair notícias  
✅ Testa scraping HTML como fallback  
✅ Salva no PostgreSQL  
✅ Interface web bonita e funcional  

---

## 🚀 Como Usar

### 1. Configurar Banco de Dados

Adicione a URL do PostgreSQL no `.env`:

```env
DATABASE_URL=postgres://postgres:99d74b03160029761260@72.61.32.25:5432/postgres?sslmode=disable
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Iniciar o Servidor

```bash
python app.py
```

O servidor vai iniciar em: `http://localhost:8001`

### 4. Acessar a Interface Web

Abra no navegador:

```
http://localhost:8001/feed-manager
```

---

## 🎯 Funcionalidades

### ➕ Adicionar Nova Fonte

1. **Cole a URL** do site ou RSS feed
2. **Clique em "Validar Fonte"**
   - Sistema descobre RSS automaticamente
   - Testa se consegue extrair notícias
   - Mostra exemplos de notícias encontradas
   - Calcula score de validação (0-10)
3. **Clique em "Adicionar ao Banco"**
   - Salva na tabela `approved_sources`
   - Fonte fica disponível para uso

### 📚 Gerenciar Fontes

- **Visualizar todas as fontes** cadastradas
- **Ativar/Desativar** fontes
- **Deletar** fontes
- **Ver metadados**: score, tipo (RSS/HTML), data de criação

---

## 🔧 API Endpoints

### `GET /api/sources`

Lista todas as fontes cadastradas.

**Resposta:**
```json
{
  "success": true,
  "sources": [
    {
      "id": 1,
      "name": "FitFeed",
      "url": "https://fitfeed.com.br/feed",
      "type": "rss",
      "active": true,
      "validation_score": 10,
      "validated_at": "2025-11-10T22:52:13.892Z",
      "created_at": "2025-11-10T22:52:13.892Z"
    }
  ],
  "total": 1
}
```

### `POST /api/sources/validate`

Valida uma fonte antes de adicionar (NÃO salva no banco).

**Request:**
```json
{
  "url": "https://exemplo.com.br",
  "name": "Blog Exemplo"
}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "url": "https://exemplo.com.br",
    "rss_found": [
      {
        "url": "https://exemplo.com.br/feed",
        "entries_count": 15,
        "title": "Blog Exemplo"
      }
    ],
    "validation_score": 10,
    "can_scrape_html": false,
    "sample_news": [
      {
        "title": "Notícia 1",
        "url": "https://exemplo.com.br/noticia-1",
        "summary": "Resumo da notícia...",
        "pubDate": "2025-11-19T10:00:00",
        "source": "Blog Exemplo"
      }
    ],
    "recommended_url": "https://exemplo.com.br/feed",
    "recommended_name": "Blog Exemplo"
  }
}
```

### `POST /api/sources/add`

Adiciona uma fonte ao banco de dados (valida antes).

**Request:**
```json
{
  "url": "https://exemplo.com.br",
  "name": "Blog Exemplo"
}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "source": {
      "id": 10,
      "url": "https://exemplo.com.br/feed",
      "name": "Blog Exemplo",
      "type": "rss",
      "validation_score": 10,
      "validated_at": "2025-11-19T10:00:00",
      "active": true,
      "created_at": "2025-11-19T10:00:00"
    },
    "validation": { ... }
  }
}
```

### `DELETE /api/sources/{id}`

Deleta uma fonte.

**Resposta:**
```json
{
  "success": true,
  "message": "Fonte deletada com sucesso"
}
```

### `PATCH /api/sources/{id}/toggle`

Ativa/desativa uma fonte.

**Resposta:**
```json
{
  "success": true,
  "active": false,
  "message": "Fonte desativada com sucesso"
}
```

---

## 🎨 Interface Web

### Tela Principal

```
┌─────────────────────────────────────────────┐
│  🗞️ Gerenciador de Feeds RSS                │
│  Adicione e gerencie fontes automaticamente │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  ➕ Adicionar Nova Fonte                     │
│                                             │
│  URL do Site ou RSS Feed                    │
│  [https://exemplo.com.br              ]     │
│  Cole a URL do site. O sistema vai          │
│  descobrir o RSS automaticamente!           │
│                                             │
│  Nome da Fonte (opcional)                   │
│  [Blog de Nutrição                    ]     │
│  Se deixar vazio, será detectado            │
│  automaticamente                            │
│                                             │
│  [🔍 Validar Fonte] [✅ Adicionar ao Banco] │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Resultado da Validação              │   │
│  │ Score: 10/10 ✅                     │   │
│  │ RSS Feed Encontrado!                │   │
│  │ 📰 Notícias Encontradas (3 exemplos)│   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  📚 Fontes Cadastradas          [🔄 Atualizar]│
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ FitFeed                             │   │
│  │ https://fitfeed.com.br/feed         │   │
│  │ [RSS] [✅ Ativa] [Score: 10/10]     │   │
│  │ 📅 Criado: 10/11/2025               │   │
│  │ [⏸️ Desativar] [🗑️ Deletar]         │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Saúde Abril                         │   │
│  │ https://saude.abril.com.br/feed     │   │
│  │ [RSS] [✅ Ativa] [Score: 10/10]     │   │
│  │ 📅 Criado: 10/11/2025               │   │
│  │ [⏸️ Desativar] [🗑️ Deletar]         │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 🧪 Como Funciona a Validação

### 1. Descoberta de RSS

O sistema tenta encontrar RSS feed automaticamente:

**Método 1: URLs comuns**
- `/feed`
- `/feed/`
- `/rss`
- `/rss.xml`
- `/atom.xml`
- `/index.xml`

**Método 2: Busca no HTML**
- Tags `<link type="application/rss+xml">`
- Tags `<link type="application/atom+xml">`
- Links `<a>` com texto "RSS" ou "Feed"

### 2. Validação de Conteúdo

Após encontrar o feed, o sistema:

1. **Faz parse do RSS** com `feedparser`
2. **Extrai notícias** dos últimos 7 dias
3. **Calcula score**:
   - **10/10**: RSS funcionando perfeitamente
   - **7/10**: HTML scraping funcionando
   - **0/10**: Não conseguiu extrair notícias

### 3. Fallback HTML

Se não encontrar RSS, tenta scraping do HTML:

- Procura tags `<article>`
- Procura divs com classes: `post`, `article`, `entry`, `blog-post`
- Extrai: título, link, resumo, data
- Score: 7/10 (menos confiável que RSS)

---

## 📊 Estrutura do Banco de Dados

### Tabela: `approved_sources`

```sql
CREATE TABLE approved_sources (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR,
    url VARCHAR NOT NULL,
    name VARCHAR,
    type VARCHAR,  -- 'rss' ou 'html'
    validation_score INTEGER,
    validated_at TIMESTAMP,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎯 Exemplos de Uso

### Exemplo 1: Adicionar Blog com RSS

```
1. Cole URL: https://fitfeed.com.br
2. Clique "Validar Fonte"
   ✅ RSS encontrado: https://fitfeed.com.br/feed
   ✅ Score: 10/10
   ✅ 15 notícias encontradas
3. Clique "Adicionar ao Banco"
   ✅ Fonte adicionada com sucesso!
```

### Exemplo 2: Adicionar Blog sem RSS

```
1. Cole URL: https://blog-sem-rss.com.br
2. Clique "Validar Fonte"
   ⚠️ RSS não encontrado
   ✅ HTML scraping funciona
   ✅ Score: 7/10
   ✅ 8 notícias encontradas
3. Clique "Adicionar ao Banco"
   ✅ Fonte adicionada (tipo: html)
```

### Exemplo 3: Site Incompatível

```
1. Cole URL: https://site-incompativel.com
2. Clique "Validar Fonte"
   ❌ RSS não encontrado
   ❌ HTML scraping falhou
   ❌ Score: 0/10
   ❌ Nenhuma notícia encontrada
3. Botão "Adicionar" fica desabilitado
```

---

## 🔒 Segurança

- ✅ Validação de URLs
- ✅ Proteção contra duplicatas
- ✅ Confirmação antes de deletar
- ✅ CORS configurado
- ✅ Tratamento de erros

---

## 🚀 Deploy

### Desenvolvimento

```bash
python app.py
```

### Produção (com Gunicorn)

```bash
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["python", "app.py"]
```

---

## 📝 Notas

- **Score 10/10**: RSS perfeito, use sem medo
- **Score 7/10**: HTML scraping, pode ter inconsistências
- **Score 0/10**: Não adicione, não vai funcionar

- **Tipo RSS**: Mais confiável, estruturado
- **Tipo HTML**: Menos confiável, pode quebrar se o site mudar

---

## 🆘 Troubleshooting

### Erro: "Fonte não passou na validação"

**Causa**: Site não tem RSS e HTML scraping falhou

**Solução**:
1. Verifique se o site tem RSS feed
2. Tente adicionar `/feed` ou `/rss` na URL
3. Procure link "RSS" no site

### Erro: "Esta fonte já está cadastrada"

**Causa**: URL já existe no banco

**Solução**:
1. Verifique a lista de fontes
2. Use a fonte existente
3. Ou delete e adicione novamente

### Erro de conexão com banco

**Causa**: DATABASE_URL incorreta ou banco offline

**Solução**:
1. Verifique `.env`
2. Teste conexão: `psql $DATABASE_URL`
3. Verifique firewall/VPN

---

## ✅ Checklist de Instalação

- [ ] Python 3.11+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] `.env` configurado com DATABASE_URL
- [ ] Tabela `approved_sources` existe no banco
- [ ] Servidor rodando (`python app.py`)
- [ ] Interface acessível em `http://localhost:8001/feed-manager`
- [ ] Teste: adicionar uma fonte de exemplo

---

**Criado em:** 19/11/2025  
**Versão:** 1.0.0  
**Status:** ✅ Pronto para uso
