# Deploy Rapido para VPS

## 1. Commit das Alteracoes

```bash
# Adicione os arquivos (cookies.txt NAO sera commitado - esta no .gitignore)
git add .
git commit -m "feat: adiciona suporte a proxy Apify e cookies do YouTube"
git push origin main
```

## 2. Copie o Cookie para VPS

### Opcao A: Via SCP (Recomendado)

```bash
# Substitua pelo IP/dominio da sua VPS
scp cookies.txt root@seu-dominio-vps.com:/tmp/cookies.txt
```

### Opcao B: Via Easypanel (se usar)

1. Acesse o painel do Easypanel
2. Va em seu projeto
3. Clique em "Files" ou "Terminal"
4. Faca upload do cookies.txt para /tmp/

## 3. Na VPS - Configure

```bash
# Conecte na VPS
ssh root@seu-dominio-vps.com

# Encontre o container
docker ps

# Copie o cookie para dentro do container
docker cp /tmp/cookies.txt nome-do-container:/app/cookies.txt

# Verifique
docker exec nome-do-container ls -la /app/cookies.txt
```

## 4. Configure Variaveis de Ambiente

### Via Easypanel:

1. Va em "Environment Variables"
2. Adicione/atualize:
   ```
   APIFY_PROXY_PASSWORD=sua_senha_do_proxy_apify_aqui
   YOUTUBE_COOKIES_PATH=/app/cookies.txt
   ```
3. Clique em "Save"

### Via SSH (se nao usar Easypanel):

```bash
# Edite o .env
nano /caminho/do/projeto/.env

# Adicione:
APIFY_PROXY_PASSWORD=sua_senha_do_proxy_apify_aqui
YOUTUBE_COOKIES_PATH=/app/cookies.txt

# Salve: Ctrl+X, Y, Enter
```

## 5. Reinicie o Servico

### Via Easypanel:
- Clique em "Restart"

### Via Docker Compose:
```bash
cd /caminho/do/projeto
docker-compose down
docker-compose up -d
```

### Via Docker direto:
```bash
docker restart nome-do-container
```

## 6. Teste

```bash
# Teste via API
curl -X POST https://seu-dominio.com/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/shorts/bfKu9LVqC4Q", "type": "auto"}'
```

## Checklist

- [ ] Commit feito
- [ ] Push para GitHub
- [ ] VPS fez pull/rebuild
- [ ] cookies.txt copiado para /app/cookies.txt
- [ ] Variaveis de ambiente configuradas
- [ ] Servico reiniciado
- [ ] Teste funcionando

## Resultado Esperado

```json
{
  "success": true,
  "type": "youtube",
  "data": {
    "title": "Qual a MELHOR REFEICAO apos o CARDIO em JEJUM?",
    "video_id": "bfKu9LVqC4Q",
    "transcript": "...",
    "word_count": 58,
    "duration_scraped": 16.9
  }
}
```

## Troubleshooting

### "cookies.txt nao encontrado"
```bash
# Verifique
docker exec nome-container ls -la /app/

# Copie novamente
docker cp /tmp/cookies.txt nome-container:/app/cookies.txt
```

### "Ainda da erro 429"
- Aguarde alguns minutos (rate limit)
- Teste com outro video

### "Variavel nao carregada"
```bash
# Verifique
docker exec nome-container env | grep YOUTUBE

# Se nao aparecer, reconstrua
docker-compose down
docker-compose up -d --build
```
