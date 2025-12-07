#!/bin/bash
# Script para iniciar o projeto usando Docker

set -e

echo "🐳 Gemini Computer Use - Docker Setup"
echo "======================================"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Verificar se arquivo .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado."
    echo "📝 Criando arquivo .env a partir do exemplo..."
    
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ Arquivo .env criado. Por favor, edite o arquivo .env e adicione sua GEMINI_API_KEY"
        echo ""
        echo "Abra o arquivo .env e configure:"
        echo "  GEMINI_API_KEY=your_api_key_here"
        echo ""
        read -p "Pressione Enter após configurar o .env para continuar..."
    else
        echo "❌ Arquivo env.example não encontrado."
        exit 1
    fi
fi

# Verificar se GEMINI_API_KEY está configurada
if ! grep -q "GEMINI_API_KEY=.*[^your_api_key_here]" .env 2>/dev/null; then
    echo "⚠️  GEMINI_API_KEY não está configurada no arquivo .env"
    echo "Por favor, edite o arquivo .env e adicione sua chave da API."
    exit 1
fi

echo "✅ Configuração verificada"
echo ""

# Construir e iniciar
echo "🔨 Construindo imagem Docker..."
docker-compose build

echo ""
echo "🚀 Iniciando container..."
docker-compose up -d

echo ""
echo "✅ Container iniciado!"
echo ""
echo "📊 Para ver os logs:"
echo "   docker-compose logs -f"
echo ""
echo "🌐 Acesse a interface web em:"
echo "   http://localhost:8080"
echo ""
echo "⏹️  Para parar o container:"
echo "   docker-compose down"
echo ""

