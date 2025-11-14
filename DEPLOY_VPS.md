# 🚀 Deploy na VPS

Guia completo para fazer deploy do microserviço de scraper na sua VPS.

## 📋 Pré-requisitos

- VPS com Ubuntu/Debian
- Docker e Docker Compose instalados
- Porta 8001 disponível

## 🔧 Instalação do Docker (se necessário)

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose -y

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

## 📦 Deploy com Docker Compose (Recomendado)

### 1. Clonar/Enviar código para VPS

```bash
# Opção 1: Via Git
git clone seu-repositorio
cd microservico_scraper

# Opção 2: Via SCP (do seu PC)
scp -r microservico_scraper usuario@seu-vps:/home/usuario/
```

### 2. Configurar variáveis de ambiente (opcional)

```bash
# Copiar exemplo
cp .env.example .env

# Editar com suas credenciais Reddit (opcional)
nano .env
```

### 3. Build e Run

```bash
# Build da imagem
docker-compose build

# Rodar em background
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 4. Testar

```bash
# Health check
curl http://localhost:8001/health

# Teste de scraping
curl -X POST http://localhost:8001/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://wellworthy.com/monster-enters-the-female-focused-energy-game-with-flrt/"}'
```

## 🐳 Deploy com Docker (Manual)

```bash
# Build
docker build -t scraper-api .

# Run
docker run -d \
  --name scraper-api \
  -p 8001:8001 \
  --restart unless-stopped \
  scraper-api

# Ver logs
docker logs -f scraper-api
```

## 🔄 Atualizar o serviço

```bash
# Parar containers
docker-compose down

# Atualizar código (git pull ou scp)
git pull

# Rebuild e restart
docker-compose up -d --build
```

## 🌐 Expor para internet

### Opção 1: Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/scraper-api
server {
    listen 80;
    server_name scraper.seudominio.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/scraper-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL com Certbot (opcional)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d scraper.seudominio.com
```

### Opção 2: Expor porta diretamente

```bash
# Abrir porta no firewall
sudo ufw allow 8001/tcp
```

## 📊 Monitoramento

### Ver status

```bash
docker-compose ps
```

### Ver logs

```bash
# Últimas 100 linhas
docker-compose logs --tail=100

# Seguir logs em tempo real
docker-compose logs -f

# Logs de um serviço específico
docker-compose logs -f scraper-api
```

### Reiniciar serviço

```bash
docker-compose restart
```

## 🔧 Troubleshooting

### Container não inicia

```bash
# Ver logs de erro
docker-compose logs

# Verificar se porta está em uso
sudo netstat -tulpn | grep 8001

# Rebuild forçado
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Erro de memória

```bash
# Limpar containers antigos
docker system prune -a

# Verificar uso de recursos
docker stats
```

### YouTube não funciona

O YouTube pode bloquear IPs de VPS. Soluções:
1. Usar proxy/VPN
2. Rotacionar IPs
3. Adicionar delays entre requests

## 🔐 Segurança

### Limitar acesso por IP

```nginx
# No Nginx
location / {
    allow 192.168.1.0/24;  # Sua rede
    deny all;
    proxy_pass http://localhost:8001;
}
```

### Adicionar autenticação

```nginx
# Criar arquivo de senha
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd usuario

# No Nginx
location / {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8001;
}
```

## 📈 Performance

### Aumentar workers

Edite `app.py`:

```python
if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        workers=4  # Adicione esta linha
    )
```

### Limitar recursos do Docker

```yaml
# docker-compose.yml
services:
  scraper-api:
    # ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
```

## 🔄 Auto-restart

O Docker Compose já está configurado com `restart: unless-stopped`.

Para garantir que inicie no boot:

```bash
# Habilitar Docker no boot
sudo systemctl enable docker

# Criar serviço systemd (opcional)
sudo nano /etc/systemd/system/scraper-api.service
```

```ini
[Unit]
Description=Scraper API
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/usuario/microservico_scraper
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable scraper-api
sudo systemctl start scraper-api
```

## 📞 Uso no n8n

No seu workflow n8n, use o HTTP Request node:

```json
{
  "method": "POST",
  "url": "http://seu-vps:8001/scrape",
  "body": {
    "url": "{{ $json.article_url }}",
    "type": "auto"
  }
}
```

Resposta:
```json
{
  "success": true,
  "type": "article",
  "data": {
    "title": "...",
    "content": "...",
    "word_count": 1500
  }
}
```

## ✅ Checklist de Deploy

- [ ] Docker e Docker Compose instalados
- [ ] Código copiado para VPS
- [ ] `.env` configurado (se usar Reddit)
- [ ] `docker-compose up -d` executado
- [ ] Health check funcionando
- [ ] Teste de scraping OK
- [ ] Firewall configurado
- [ ] Nginx configurado (se usar)
- [ ] SSL configurado (se usar)
- [ ] Auto-restart habilitado

## 🎉 Pronto!

Seu microserviço está rodando em: `http://seu-vps:8001`

Documentação interativa: `http://seu-vps:8001/docs`
