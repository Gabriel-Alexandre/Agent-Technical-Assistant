# Use a imagem oficial do Python com Playwright incluído
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0 \
    DISPLAY=:99

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias para Playwright
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    gnupg \
    ca-certificates \
    procps \
    curl \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libcups2 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Verificar se o Playwright foi instalado corretamente
RUN python -c "import playwright; print('Playwright importado com sucesso')"

# Instalar navegadores do Playwright com dependências do sistema
# Forçar reinstalação para garantir que funcione
RUN playwright install chromium && \
    playwright install-deps chromium

# Verificar se o Chromium foi instalado corretamente
RUN python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print('Chromium path:', p.chromium.executable_path); p.stop()"

# Copiar código da aplicação
COPY . .

# Copiar e configurar script de entrada
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Criar diretórios necessários
RUN mkdir -p data live_data live_data_simplify analysis logs

# Criar usuário não-root para segurança
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /ms-playwright && \
    chmod -R 755 /app/data && \
    chmod -R 755 /app/live_data && \
    chmod -R 755 /app/live_data_simplify && \
    chmod -R 755 /app/analysis && \
    chmod -R 755 /app/logs

USER appuser

# Verificar novamente após mudar de usuário
RUN python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print('Final check - Chromium path:', p.chromium.executable_path); p.stop()"

# Expor porta
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Definir entrypoint e comando
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 