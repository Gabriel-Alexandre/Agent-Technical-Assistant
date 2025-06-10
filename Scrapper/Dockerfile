# Use a imagem oficial do Python com Node.js incluído
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright e navegadores
RUN playwright install --with-deps chromium

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p data live_data live_data_simplify analysis

# Configurar variáveis de ambiente para Playwright no Docker
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV DISPLAY=:99

# Expor porta da API
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 