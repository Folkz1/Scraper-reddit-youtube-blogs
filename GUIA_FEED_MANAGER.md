# 🚀 Guia Rápido - Feed Manager

## ⏱️ Instalação em 5 Minutos

### 1. Configure o Banco de Dados

Crie o arquivo `.env` na pasta `microservico_scraper`:

```bash
DATABASE_URL=postgres://postgres:99d74b03160029761260@72.61.32.25:5432/postgres?sslmode=disable
```

### 2. Instale as Dependências

```bash
cd microservico_scraper
pip install -r requirements.txt
```

### 3. Inicie o Servidor

```bash
python app.py
```

Você verá:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### 4. Acesse a Interface Web

Abra no navegador:

```
http://localhost:8001/feed-manager
```

---

## 🎯 Como Usar

### Adicionar Nova Fonte

1. **Cole a URL** do site (ex: `https://fitfeed.com.br`)
2. **Clique em "🔍 Validar Fonte"**
   - Aguarde 5-10 segundos
   - Sistema vai descobrir o RSS automaticamente
   - Mostra exemplos de notícias encontradas
3. **Clique em "✅ Adicionar ao Banco"**
   - Fonte salva no PostgreSQL
   - Pronta para uso no n8n!

### Gerenciar Fontes

- **⏸️ Desativar**: Fonte fica no banco mas não é usada
- **▶️ Ativar**: Reativa fonte desativada
- **🗑️ Deletar**: Remove permanentemente do banco

---

## 📊 Score de Validação

- **10/10** ✅ - RSS perfeito, use sem medo
- **7/10** ⚠️ - HTML scraping, pode ter inconsistências
- **0/10** ❌ - Não funciona, não adicione

---

## 🧪 Testar

```bash
python test_feed_manager.py
```

---

## 🔗 Endpoints da API

### Listar Fontes
```bash
curl http://localhost:8001/api/sources
```

### Validar Fonte
```bash
curl -X POST http://localhost:8001/api/sources/validate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://fitfeed.com.br"}'
```

### Adicionar Fonte
```bash
curl -X POST http://localhost:8001/api/sources/add \
  -H "Content-Type: application/json" \
  -d '{"url": "https://fitfeed.com.br", "name": "FitFeed"}'
```

---

## 🎨 Preview da Interface

```
┌──────────────────────────────────────────┐
│  🗞️ Gerenciador de Feeds RSS             │
│  Adicione e gerencie fontes              │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  ➕ Adicionar Nova Fonte                  │
│                                          │
│  URL: [https://exemplo.com.br      ]     │
│  Nome: [Blog Exemplo               ]     │
│                                          │
│  [🔍 Validar] [✅ Adicionar]             │
│                                          │
│  ✅ Score: 10/10                         │
│  📰 3 notícias encontradas               │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  📚 Fontes Cadastradas    [🔄 Atualizar] │
│                                          │
│  FitFeed                                 │
│  https://fitfeed.com.br/feed             │
│  [RSS] [✅ Ativa] [Score: 10/10]         │
│  [⏸️ Desativar] [🗑️ Deletar]             │
└──────────────────────────────────────────┘
```

---

## ✅ Checklist

- [ ] `.env` criado com DATABASE_URL
- [ ] Dependências instaladas
- [ ] Servidor rodando
- [ ] Interface acessível
- [ ] Teste: adicionar uma fonte

---

## 🆘 Problemas?

### Servidor não inicia

```bash
# Verifique se a porta 8001 está livre
netstat -ano | findstr :8001

# Ou use outra porta
uvicorn app:app --port 8002
```

### Erro de conexão com banco

```bash
# Teste a conexão
psql postgres://postgres:99d74b03160029761260@72.61.32.25:5432/postgres?sslmode=disable
```

### Validação falha

- Verifique se o site tem RSS feed
- Tente adicionar `/feed` ou `/rss` na URL
- Alguns sites bloqueiam scrapers

---

**Pronto! Agora você pode adicionar fontes RSS automaticamente! 🎉**
