# 🚀 Deploy no Easypanel

Guia completo para fazer deploy do Scraper API no Easypanel.

## 📋 Configuração no Easypanel

### 1️⃣ Criar Novo Projeto

1. Acesse seu Easypanel
2. Clique em **"Create Project"**
3. Nome: `scrapers`

### 2️⃣ Adicionar Serviço

1. Dentro do projeto, clique em **"Add Service"**
2. Escolha **"App"**
3. Escolha **"Github"**

### 3️⃣ Configurar Repositório

**Source:**
- Repository: `https://github.com/Folkz1/Scraper-reddit-youtube-blogs`
- Branch: `main`
- Auto Deploy: ✅ Enabled

**Build:**
- Build Type: `Dockerfile`
- Dockerfile Path: `.Dockerfile` (com ponto no início!)

### 4️⃣ Configurar Variáveis de Ambiente

Na aba **Environment**, adicione:

```bash
# Reddit API (opcional)
REDDIT_CLIENT_ID=uW99M0wWMsV4BixNiGSXBg
REDDIT_CLIENT_SECRET=mnXuX3Ep4j1FhP4Ol6kYVALmH9uL1g
REDDIT_USER_AGENT=ScraperBot/1.0
```

### 5️⃣ Configurar Domínio

**Domains:**
- Adicione um domínio customizado ou use o gerado automaticamente
- Porta: `8001`

**Exemplo:**
- `scraper-api.seudominio.com` → `8001`

### 6️⃣ Deploy

1. Clique em **"Deploy"**
2. Aguarde o build (2-3 minutos)
3. Verifique os logs

## ✅ Verificar Deploy

### Health Check

```bash
curl https://scraper-api.seudominio.com/health
```

Resposta esperada:
```json
{
  "status": "healthy"
}
```

### Teste de Scraping

```bash
curl -X POST https://scraper-api.seudominio.com/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://wellworthy.com/monster-enters-the-female-focused-energy-game-with-flrt/"}'
```

## 📊 Configurações Recomendadas

### Resources

- **CPU**: 0.5 - 1 vCPU
- **Memory**: 512MB - 1GB
- **Replicas**: 1 (pode aumentar para alta demanda)

### Health Check

Configure no Easypanel:
- **Path**: `/health`
- **Port**: `8001`
- **Interval**: `30s`
- **Timeout**: `10s`
- **Retries**: `3`

## 🔄 Auto Deploy

O Easypanel está configurado para fazer deploy automático quando você fizer push no GitHub:

```bash
# No seu PC
cd microservico_scraper
git add .
git commit -m "feat: Nova feature"
git push

# Easypanel detecta e faz deploy automaticamente! 🚀
```

## 🐛 Troubleshooting

### Erro: "no such file or directory: .Dockerfile"

**Solução:** O arquivo precisa se chamar `.Dockerfile` (com ponto no início)

```bash
# No repositório
cp Dockerfile .Dockerfile
git add .Dockerfile
git commit -m "fix: Add .Dockerfile for Easypanel"
git push
```

### Build Falha

**Verificar logs:**
1. Acesse o serviço no Easypanel
2. Clique em **"Logs"**
3. Veja os erros de build

**Problemas comuns:**
- Dependências faltando → Verifique `requirements.txt`
- Porta errada → Deve ser `8001`
- Variáveis de ambiente → Verifique se estão configuradas

### Serviço não responde

**Verificar:**
1. Status do container: Deve estar "Running"
2. Logs do container: Procure por erros
3. Health check: Deve estar passando
4. Domínio: Verifique se está apontando corretamente

### Erro de memória

**Solução:** Aumentar recursos do container
1. Settings → Resources
2. Memory: Aumentar para 1GB ou mais

## 📈 Monitoramento

### Logs em Tempo Real

No Easypanel:
1. Acesse o serviço
2. Clique em **"Logs"**
3. Veja logs em tempo real

### Métricas

Monitore:
- CPU usage
- Memory usage
- Request count
- Response time

## 🔐 Segurança

### Variáveis Sensíveis

Nunca commite no Git:
- ❌ `.env` (já está no .gitignore)
- ✅ `.env.example` (template sem valores reais)

Configure no Easypanel:
- Environment variables são criptografadas
- Não aparecem nos logs

### HTTPS

O Easypanel já fornece HTTPS automático via Let's Encrypt! 🔒

## 🚀 Uso no n8n

Após o deploy, use no n8n:

```json
{
  "method": "POST",
  "url": "https://scraper-api.seudominio.com/scrape",
  "body": {
    "url": "={{ $json.article_url }}"
  }
}
```

## 📝 Checklist de Deploy

- [ ] Repositório conectado ao Easypanel
- [ ] `.Dockerfile` existe no repositório
- [ ] Variáveis de ambiente configuradas
- [ ] Domínio configurado
- [ ] Deploy realizado com sucesso
- [ ] Health check passando
- [ ] Teste de scraping funcionando
- [ ] Auto deploy habilitado

## 🎉 Pronto!

Seu Scraper API está rodando no Easypanel!

**URL da API:** `https://scraper-api.seudominio.com`
**Documentação:** `https://scraper-api.seudominio.com/docs`

---

**Dúvidas?** Abra uma issue no [GitHub](https://github.com/Folkz1/Scraper-reddit-youtube-blogs/issues)
