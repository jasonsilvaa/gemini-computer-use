#!/bin/bash
# Script para criar repositório no GitHub via API

set -e

REPO_NAME="gemini-computer-use"
GITHUB_USER="jasonsilvaa"
GITHUB_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}"

echo "🚀 Criando repositório no GitHub via API"
echo "========================================"
echo ""

# Verificar se há token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN não encontrado"
    echo ""
    echo "Para usar a API, você precisa:"
    echo "1. Criar um Personal Access Token em: https://github.com/settings/tokens"
    echo "2. Dar permissão 'repo'"
    echo "3. Executar: export GITHUB_TOKEN=seu_token_aqui"
    echo ""
    echo "Ou use o método manual:"
    echo "  ./create-github-repo.sh"
    echo ""
    exit 1
fi

echo "📦 Criando repositório '${REPO_NAME}'..."
echo ""

# Criar repositório via API
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{
    \"name\": \"${REPO_NAME}\",
    \"description\": \"Gemini Computer Use com interface gráfica e Docker - Automação de navegador com IA\",
    \"private\": false,
    \"auto_init\": false
  }")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "201" ]; then
    echo "✅ Repositório criado com sucesso!"
    echo ""
    
    # Adicionar remote se não existir
    if ! git remote get-url new-origin &>/dev/null 2>&1; then
        git remote add new-origin https://github.com/${GITHUB_USER}/${REPO_NAME}.git
        echo "✅ Remote 'new-origin' adicionado"
    fi
    
    # Fazer push
    echo ""
    echo "📤 Fazendo push..."
    git push -u new-origin main
    
    echo ""
    echo "🎉 Sucesso! Repositório disponível em:"
    echo "   ${GITHUB_URL}"
    
else
    echo "❌ Erro ao criar repositório"
    echo "HTTP Code: $HTTP_CODE"
    echo "Response: $BODY"
    echo ""
    echo "Verifique:"
    echo "1. Se o token está correto"
    echo "2. Se o token tem permissão 'repo'"
    echo "3. Se o repositório já existe"
    exit 1
fi

