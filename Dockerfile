# Dockerfile para Gemini Computer Use
FROM python:3.9-slim

# Instalar dependências do sistema para Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright e navegadores
RUN playwright install-deps chromium && \
    playwright install chromium

# Copiar código do projeto
COPY . .

# Criar diretório para screenshots/logs se necessário
RUN mkdir -p /app/logs

# Variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Expor porta padrão da interface web
EXPOSE 8080

# Comando padrão - iniciar interface web
CMD ["python", "web_gui.py", "8080"]

