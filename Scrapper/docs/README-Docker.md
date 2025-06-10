# Executando o Scrapper em Docker 🐳

Este guia explica como executar o sistema de coleta de dados do SofaScore em um ambiente Docker.

## 📋 Pré-requisitos

- Docker instalado (versão 20.10 ou superior)
- Docker Compose instalado (versão 2.0 ou superior)
- 4GB de RAM disponível (recomendado)

## 🚀 Instalação e Execução

### 1. Executar com Docker Compose (Recomendado)

```bash
# Clonar e navegar para o diretório
cd Scrapper

# Construir e executar
docker-compose up --build

# Ou em background
docker-compose up -d --build
```

### 2. Executar com Docker direto

```bash
# Construir a imagem
docker build -t scrapper-api .

# Executar o container
docker run -p 8000:8000 \
  --shm-size=2g \
  --security-opt seccomp:unconfined \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env:ro \
  scrapper-api
```

## 🔧 Configurações Importantes

### Playwright no Docker

O Dockerfile inclui configurações específicas para o Playwright funcionar em containers:

- **Imagem base**: `mcr.microsoft.com/playwright/python:v1.40.0-jammy`
- **Argumentos do Chrome**: Otimizados para ambiente headless
- **Shared memory**: 2GB para evitar crashes do navegador
- **Security options**: `seccomp:unconfined` para permitir subprocessos

### Variáveis de Ambiente

Crie um arquivo `.env` com:

```env
OPENAI_API_KEY=sua_chave_openai_aqui
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
PYTHONUNBUFFERED=1
```

## 📚 Endpoints da API

Uma vez executando, a API estará disponível em `http://localhost:8000`:

### 🏥 Health Check
```bash
curl http://localhost:8000/health
```

### ⚽ Coleta de Dados de Partida
```bash
# Dados completos
curl -X POST "http://localhost:8000/match/11161648/full-data"

# Dados simplificados
curl -X POST "http://localhost:8000/match/11161648/simplified-data"

# Análise completa (requer OpenAI API Key)
curl -X POST "http://localhost:8000/match/11161648/analysis"
```

## 📊 Monitoramento

### Verificar logs
```bash
# Com docker-compose
docker-compose logs -f scrapper-api

# Com docker direto
docker logs -f <container_id>
```

### Verificar status do container
```bash
docker-compose ps
# ou
docker ps
```

## 🐛 Troubleshooting

### Erro "NotImplementedError" no Playwright

Se você encontrar o erro `NotImplementedError`, verifique:

1. **Shared memory suficiente**:
   ```bash
   docker run --shm-size=2g ...
   ```

2. **Security options**:
   ```bash
   docker run --security-opt seccomp:unconfined ...
   ```

3. **Argumentos do Chrome**: O código inclui argumentos otimizados para Docker

### Container não inicia

1. **Verificar recursos**: Garanta pelo menos 4GB RAM disponível
2. **Verificar porta**: Porta 8000 não deve estar em uso
3. **Verificar logs**: `docker-compose logs scrapper-api`

### Playwright não encontra navegador

O Dockerfile instala automaticamente o Chromium:
```dockerfile
RUN playwright install --with-deps chromium
```

Se houver problemas, reconstrua a imagem:
```bash
docker-compose build --no-cache
```

## 🔒 Segurança

### Produção

Para ambiente de produção, considere:

1. **Secrets**: Use Docker secrets para API keys
2. **User non-root**: Adicione usuário não-root no Dockerfile
3. **Resource limits**: Defina limites de CPU/memória
4. **Network**: Use redes Docker personalizadas

### Exemplo de configuração de produção

```yaml
# docker-compose.prod.yml
services:
  scrapper-api:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    environment:
      - ENVIRONMENT=production
    secrets:
      - openai_api_key
```

## 📈 Performance

### Otimizações incluídas

- **Single process**: `--single-process` para ambientes com poucos recursos
- **Disable features**: Features desnecessárias desabilitadas
- **Fast loading**: `domcontentloaded` em vez de `networkidle`
- **Retry logic**: Tentativas automáticas em caso de falha

### Monitoramento de recursos

```bash
# Ver uso de recursos
docker stats

# Ver logs de performance
docker-compose logs | grep "✅\|❌\|⚠️"
```

## 🚀 Implantação

### Docker Hub (opcional)

```bash
# Build e tag
docker build -t seu-usuario/scrapper-api:latest .

# Push
docker push seu-usuario/scrapper-api:latest
```

### Deploy em servidor

```bash
# No servidor
docker pull seu-usuario/scrapper-api:latest
docker-compose up -d
```

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs: `docker-compose logs`
2. Teste os scripts originais fora do Docker
3. Verifique recursos do sistema (RAM, CPU)
4. Reconstrua sem cache: `docker-compose build --no-cache` 