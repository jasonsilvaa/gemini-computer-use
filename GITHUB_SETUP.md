# 📦 Configuração do Repositório GitHub

Este guia explica como criar o repositório no GitHub e fazer push do código.

## Opção 1: Via Interface Web (Recomendado)

### Passo 1: Criar o Repositório

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name**: `gemini-computer-use`
   - **Description**: `Gemini Computer Use com interface gráfica e Docker - Automação de navegador com IA`
   - **Visibility**: Public (ou Private, conforme preferir)
   - ⚠️ **NÃO marque** "Add a README file"
   - ⚠️ **NÃO adicione** .gitignore ou license
3. Clique em **"Create repository"**

### Passo 2: Conectar e Fazer Push

Execute o script:

```bash
./create-github-repo.sh
```

O script irá:
- Adicionar o remote do GitHub
- Fazer push do código
- Configurar o branch main

## Opção 2: Via API (Automático)

### Passo 1: Criar Personal Access Token

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token (classic)"**
3. Dê um nome (ex: "gemini-computer-use")
4. Marque a permissão **"repo"**
5. Clique em **"Generate token"**
6. **Copie o token** (você não verá novamente!)

### Passo 2: Executar Script

```bash
export GITHUB_TOKEN=seu_token_aqui
./create-repo-api.sh
```

## Opção 3: Manual

### 1. Criar repositório no GitHub
Acesse https://github.com/new e crie o repositório `gemini-computer-use`

### 2. Adicionar remote e fazer push

```bash
# Adicionar remote
git remote add new-origin https://github.com/jasonsilvaa/gemini-computer-use.git

# Fazer push
git push -u new-origin main
```

### 3. (Opcional) Trocar origin

Se quiser usar como remote principal:

```bash
git remote set-url origin https://github.com/jasonsilvaa/gemini-computer-use.git
git remote remove new-origin
```

## Verificar

Após o push, acesse:
- **URL**: https://github.com/jasonsilvaa/gemini-computer-use

## Estrutura do Repositório

O repositório inclui:
- ✅ Código original do Google
- ✅ Interface gráfica tkinter (`gui.py`)
- ✅ Interface web Flask (`web_gui.py`)
- ✅ Dockerfile e docker-compose.yml
- ✅ Scripts de inicialização
- ✅ Documentação completa
- ✅ `.gitignore` configurado

## Arquivos Ignorados

O `.gitignore` está configurado para ignorar:
- `.env` (arquivo com API keys)
- `.venv/` (ambiente virtual)
- Logs e arquivos temporários
- Cache do Python

## Próximos Passos

Após criar o repositório:
1. Adicione uma descrição no GitHub
2. Configure topics/tags (ex: `python`, `docker`, `gemini`, `automation`)
3. Adicione badges no README (opcional)
4. Configure GitHub Actions para CI/CD (opcional)

