#!/bin/bash
# Script para iniciar a interface gráfica com tratamento de erros

cd "$(dirname "$0")"

# Ativar ambiente virtual
source .venv/bin/activate

# Verificar se a API key está configurada
if [ -z "$GEMINI_API_KEY" ]; then
    echo "Aviso: GEMINI_API_KEY não está configurada no ambiente atual."
    echo "Tentando carregar do arquivo de ativação..."
    source .venv/bin/activate
fi

# Tentar iniciar a GUI
echo "Iniciando interface gráfica..."
python gui.py 2>&1

# Se houver erro, mostrar mensagem
if [ $? -ne 0 ]; then
    echo ""
    echo "Erro ao iniciar a interface gráfica."
    echo "Tente executar diretamente: python gui.py"
    echo "Ou use a linha de comando: python main.py --query 'sua query aqui'"
fi

