# Interface Gráfica - Gemini Computer Use

Esta interface gráfica permite usar o Gemini Computer Use de forma visual e interativa.

## Como Usar

### 1. Iniciar a Interface Gráfica

```bash
python gui.py
```

Certifique-se de que o ambiente virtual está ativado e que a variável `GEMINI_API_KEY` está configurada.

### 2. Configurar a Query

1. **Query**: Digite a tarefa que deseja que o agente execute (ex: "Go to Google and type 'Hello World' into the search bar")
2. **Ambiente**: Escolha entre `playwright` (local) ou `browserbase` (remoto)
3. **URL Inicial**: Defina a URL inicial para o navegador (padrão: https://www.google.com)
4. **Modelo**: Escolha o modelo do Gemini a ser usado
5. **Destacar posição do mouse**: Marque esta opção se quiser ver a posição do mouse destacada nas screenshots

### 3. Executar

1. Clique no botão **▶ Iniciar** para começar a execução
2. Acompanhe os logs em tempo real na área de logs
3. Veja as screenshots atualizadas automaticamente durante a execução
4. Use o botão **⏹ Parar** para interromper a execução (se necessário)

## Recursos

- **Logs em Tempo Real**: Veja todas as ações e raciocínios do agente
- **Screenshots Automáticas**: Visualize o estado atual do navegador
- **Interface Intuitiva**: Configuração fácil e visualização clara
- **Controle de Execução**: Inicie, pare e limpe logs facilmente

## Requisitos

- Python 3.9+
- Todas as dependências do `requirements.txt` (incluindo Pillow)
- Variável de ambiente `GEMINI_API_KEY` configurada

## Notas

- A interface executa o agente em uma thread separada para não travar a interface
- Screenshots são atualizadas automaticamente a cada ação do agente
- Em caso de confirmação de segurança, um diálogo será exibido
- Os logs podem ser limpos a qualquer momento usando o botão "Limpar Logs"

