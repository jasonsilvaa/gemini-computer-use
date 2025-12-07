# Docker Setup - Gemini Computer Use

Este guia explica como executar o projeto usando Docker.

## Pré-requisitos

- Docker instalado
- Docker Compose instalado (geralmente vem com Docker Desktop)

## Configuração Rápida

### 1. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua `GEMINI_API_KEY`:

```
GEMINI_API_KEY=AIzaSyD04vY3czMlU-82ogENSWQZIaeSWR65EgQ
```

### 2. Construir e Iniciar o Container

```bash
docker-compose up --build
```

Ou para rodar em background:

```bash
docker-compose up -d --build
```

### 3. Acessar a Interface Web

Abra seu navegador e acesse:

```
http://localhost:8080
```

## Comandos Úteis

### Parar o container:
```bash
docker-compose down
```

### Ver logs:
```bash
docker-compose logs -f
```

### Reconstruir após mudanças:
```bash
docker-compose up --build
```

### Executar comandos dentro do container:
```bash
docker-compose exec gemini-computer-use bash
```

### Executar script Python diretamente:
```bash
docker-compose exec gemini-computer-use python main.py --query "sua query aqui"
```

## Usando Dockerfile Diretamente

Se preferir usar apenas o Dockerfile:

### 1. Construir a imagem:
```bash
docker build -t gemini-computer-use .
```

### 2. Executar o container:
```bash
docker run -d \
  -p 8080:8080 \
  -e GEMINI_API_KEY=your_api_key_here \
  --name gemini-computer-use \
  gemini-computer-use
```

### 3. Ver logs:
```bash
docker logs -f gemini-computer-use
```

### 4. Parar o container:
```bash
docker stop gemini-computer-use
docker rm gemini-computer-use
```

## Variáveis de Ambiente

Você pode configurar as seguintes variáveis de ambiente:

- `GEMINI_API_KEY`: Sua chave da API do Gemini (obrigatório)
- `USE_VERTEXAI`: `true` ou `false` (padrão: `false`)
- `VERTEXAI_PROJECT`: ID do projeto Vertex AI (se usar Vertex AI)
- `VERTEXAI_LOCATION`: Localização do Vertex AI (se usar Vertex AI)
- `BROWSERBASE_API_KEY`: Chave da API Browserbase (opcional)
- `BROWSERBASE_PROJECT_ID`: ID do projeto Browserbase (opcional)

## Troubleshooting

### Porta já em uso:
Se a porta 8080 estiver em uso, altere no `docker-compose.yml`:
```yaml
ports:
  - "3000:8080"  # Usa porta 3000 no host
```

### Problemas com Playwright:
O container já instala todas as dependências do Playwright. Se houver problemas, verifique os logs:
```bash
docker-compose logs gemini-computer-use
```

### Reconstruir do zero:
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## Desenvolvimento

Para desenvolvimento com hot-reload, você pode montar o código como volume (já configurado no docker-compose.yml):

```yaml
volumes:
  - .:/app
```

Isso permite que mudanças no código sejam refletidas sem reconstruir a imagem.

