#!/bin/bash
# Script para criar repositório no GitHub e fazer push

set -e

REPO_NAME="gemini-computer-use"
GITHUB_USER="jasonsilvaa"
GITHUB_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}"

echo "🚀 Criando repositório no GitHub"
echo "=================================="
echo ""
echo "Nome do repositório: ${REPO_NAME}"
echo "Usuário: ${GITHUB_USER}"
echo "URL: ${GITHUB_URL}"
echo ""

# Verificar se já existe um remote
if git remote get-url new-origin &>/dev/null; then
    echo "⚠️  Remote 'new-origin' já existe"
    read -p "Deseja remover e recriar? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        git remote remove new-origin
    else
        echo "❌ Operação cancelada"
        exit 1
    fi
fi

echo ""
echo "📝 INSTRUÇÕES:"
echo "=============="
echo ""
echo "1. Acesse: https://github.com/new"
echo "2. Preencha:"
echo "   - Repository name: ${REPO_NAME}"
echo "   - Description: Gemini Computer Use com interface gráfica e Docker"
echo "   - Visibility: Public (ou Private, conforme preferir)"
echo "   - NÃO marque 'Add a README file'"
echo "   - NÃO adicione .gitignore ou license"
echo ""
echo "3. Clique em 'Create repository'"
echo ""
read -p "Pressione Enter após criar o repositório no GitHub..."

# Adicionar novo remote
echo ""
echo "🔗 Configurando remote..."
git remote add new-origin https://github.com/${GITHUB_USER}/${REPO_NAME}.git

# Verificar se o remote foi adicionado
if git remote get-url new-origin &>/dev/null; then
    echo "✅ Remote 'new-origin' configurado"
else
    echo "❌ Erro ao configurar remote"
    exit 1
fi

# Fazer push
echo ""
echo "📤 Fazendo push para o GitHub..."
echo ""

# Tentar fazer push
if git push -u new-origin main; then
    echo ""
    echo "✅ Sucesso! Repositório criado e código enviado!"
    echo ""
    echo "🌐 Acesse em: ${GITHUB_URL}"
    echo ""
    echo "Para usar este remote como padrão:"
    echo "  git remote set-url origin ${GITHUB_URL}"
    echo "  git remote remove new-origin"
else
    echo ""
    echo "⚠️  Erro ao fazer push. Verifique:"
    echo "  1. Se o repositório foi criado no GitHub"
    echo "  2. Se você tem permissão para fazer push"
    echo "  3. Se precisa autenticar (git credential ou SSH)"
    echo ""
    echo "Tente manualmente:"
    echo "  git push -u new-origin main"
fi

