# Sistema de Logging Detalhado

Este documento descreve o sistema de logging implementado no projeto.

## Visão Geral

O projeto agora possui um sistema de logging detalhado e estruturado que registra todas as operações importantes do agente, navegador e interface web.

## Módulo de Logging

O módulo `logger_config.py` fornece:

- **Formatação detalhada**: Timestamp, nível, módulo, função e linha
- **Cores no terminal**: Logs coloridos para melhor visualização
- **Log em arquivo**: Opcionalmente salva logs em arquivo
- **Níveis configuráveis**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## O que é Logado

### BrowserAgent (`agent.py`)

- ✅ Inicialização do agente (modelo, query, configuração)
- ✅ Configuração do cliente Gemini (API key ou Vertex AI)
- ✅ Cada ação executada (nome, argumentos, tempo de execução)
- ✅ Respostas do modelo (tempo de resposta, número de candidatos)
- ✅ Chamadas de função (nome, argumentos detalhados)
- ✅ Raciocínio do modelo
- ✅ Estados do ambiente (URL, tamanho de screenshot)
- ✅ Erros com stack traces completos
- ✅ Loop do agente (iterações, conclusão)

### PlaywrightComputer (`playwright.py`)

- ✅ Inicialização do Playwright
- ✅ Lançamento do navegador (headless/headed)
- ✅ Criação de contexto e páginas
- ✅ Navegação para URLs (tempo de carregamento)
- ✅ Ações do mouse (cliques, hover, coordenadas)
- ✅ Digitação de texto
- ✅ Captura de screenshots (tamanho, tempo)
- ✅ Encerramento da sessão

### Interface Web (`web_gui.py`)

- ✅ Requisições HTTP (início, parada, status)
- ✅ Inicialização de threads do agente
- ✅ Configurações recebidas
- ✅ Erros e exceções
- ✅ Estado do agente

## Configuração

### Variáveis de Ambiente

```bash
# Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export LOG_LEVEL=INFO

# Arquivo de log (opcional)
export LOG_FILE=logs/app.log
```

### Uso no Código

```python
from logger_config import get_logger

logger = get_logger(__name__)

logger.info("Mensagem informativa")
logger.debug("Mensagem de debug")
logger.warning("Aviso")
logger.error("Erro")
```

## Localização dos Logs

### Console
Todos os logs são exibidos no console/terminal em tempo real.

### Arquivo
Os logs são salvos em `logs/app.log` (se configurado).

### Interface Web
Os logs também aparecem na interface web em tempo real.

## Níveis de Log

- **DEBUG**: Informações detalhadas para debugging
- **INFO**: Informações gerais sobre o funcionamento
- **WARNING**: Avisos que não impedem a execução
- **ERROR**: Erros que impedem operações específicas
- **CRITICAL**: Erros críticos que podem parar o sistema

## Exemplos de Logs

```
[2025-12-07 01:05:23] [INFO    ] [agent:__init__:71] Inicializando BrowserAgent com modelo: gemini-2.5-computer-use-preview-10-2025
[2025-12-07 01:05:23] [DEBUG   ] [agent:__init__:72] Query: Go to Google and type 'Hello World'
[2025-12-07 01:05:23] [INFO    ] [agent:__init__:76] Configurando cliente Gemini - VertexAI: False
[2025-12-07 01:05:24] [INFO    ] [agent:handle_action:146] Executando ação: click_at
[2025-12-07 01:05:24] [DEBUG   ] [agent:handle_action:147] Argumentos da ação click_at: {'x': 500, 'y': 300}
[2025-12-07 01:05:24] [INFO    ] [agent:handle_action:249] Ação click_at concluída em 0.45s
```

## Benefícios

1. **Debugging facilitado**: Logs detalhados ajudam a identificar problemas
2. **Monitoramento**: Acompanhe o progresso do agente em tempo real
3. **Análise de performance**: Tempos de execução registrados
4. **Rastreamento**: Stack traces completos para erros
5. **Auditoria**: Histórico completo de todas as operações

