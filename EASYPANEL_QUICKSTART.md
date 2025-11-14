# ⚡ Easypanel - Quick Start

## 🎯 Configuração Rápida (2 minutos)

### 1. Criar App no Easypanel

```
Project: scrapers
Service: reddit-youtube-blogs
Type: App (Github)
```

### 2. Configurar Source

```
Repository: https://github.com/Folkz1/Scraper-reddit-youtube-blogs
Branch: main
Auto Deploy: ✅ ON
```

### 3. Configurar Build

```
Build Type: Dockerfile
Dockerfile Path: .Dockerfile
```

### 4. Variáveis de Ambiente (Opcional)

```bash
REDDIT_CLIENT_ID=uW99M0wWMsV4BixNiGSXBg
REDDIT_CLIENT_SECRET=mnXuX3Ep4j1FhP4Ol6kYVALmH9uL1g
REDDIT_USER_AGENT=ScraperBot/1.0
```

### 5. Configurar Domínio

```
Port: 8001
Domain: scraper-api.seudominio.com (ou use o gerado)
```

### 6. Deploy

Clique em **"Deploy"** e aguarde 2-3 minutos.

## ✅ Testar

```bash
curl https://seu-dominio.com/health
```

## 📚 Documentação Completa

Veja [DEPLOY_EASYPANEL.md](DEPLOY_EASYPANEL.md) para guia detalhado.

---

**Pronto!** Sua API está no ar! 🚀
