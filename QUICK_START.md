# 🚀 Início Rápido - Docker

## Passo 1: Iniciar Docker

**No macOS:**
1. Abra o Docker Desktop
2. Aguarde até que o ícone do Docker na barra de menu mostre "Docker Desktop is running"

**Verificar se está rodando:**
```bash
docker ps
```
Se não mostrar erro, o Docker está funcionando!

## Passo 2: Iniciar o Projeto

Execute o script de inicialização:

```bash
./docker-start.sh
```

Ou manualmente:

```bash
# Construir e iniciar
docker-compose up --build -d

# Ver logs
docker-compose logs -f
```

## Passo 3: Acessar a Interface

Abra seu navegador em:
```
http://localhost:8080
```

## Comandos Úteis

```bash
# Ver logs em tempo real
docker-compose logs -f

# Parar o container
docker-compose down

# Reiniciar
docker-compose restart

# Ver status
docker-compose ps
```

## Troubleshooting

### Docker não inicia:
- Verifique se o Docker Desktop está instalado
- Reinicie o Docker Desktop
- Verifique se há atualizações pendentes

### Porta 8080 em uso:
Edite `docker-compose.yml` e altere:
```yaml
ports:
  - "3000:8080"  # Usa porta 3000
```

### Reconstruir do zero:
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

