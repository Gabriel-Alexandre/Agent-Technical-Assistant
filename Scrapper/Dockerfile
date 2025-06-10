# Use a imagem oficial do Python com Playwright incluído
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    DISPLAY=:99

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    gnupg \
    ca-certificates \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Instalar Playwright e navegadores
RUN playwright install --with-deps chromium

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p data live_data live_data_simplify analysis logs

# Criar usuário não-root para segurança
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app/data && \
    chmod -R 755 /app/live_data && \
    chmod -R 755 /app/live_data_simplify && \
    chmod -R 755 /app/analysis && \
    chmod -R 755 /app/logs

USER appuser

# Expor porta
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Comando para iniciar a aplicação
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 