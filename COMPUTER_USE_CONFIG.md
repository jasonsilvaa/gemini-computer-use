# 🖥️ Configuração do Computer Use

## ✅ Computer Use Sempre Ativo

O sistema **sempre usa o Computer Use** do Gemini. Esta é uma configuração obrigatória e não pode ser desabilitada.

## 🔧 Como Está Configurado

O Computer Use está configurado no arquivo `agent.py`:

```python
self._generate_content_config = GenerateContentConfig(
    temperature=1,
    top_p=0.95,
    top_k=40,
    max_output_tokens=8192,
    tools=[
        types.Tool(
            computer_use=types.ComputerUse(
                environment=types.Environment.ENVIRONMENT_BROWSER,
                excluded_predefined_functions=excluded_predefined_functions,
            ),
        ),
        types.Tool(function_declarations=custom_functions),
    ],
)
```

## 🎯 Funções do Computer Use Disponíveis

O sistema tem acesso a todas as funções pré-definidas do Computer Use:

1. **`open_web_browser`** - Abre o navegador web
2. **`click_at`** - Clica em uma coordenada específica
3. **`hover_at`** - Move o mouse para uma coordenada
4. **`type_text_at`** - Digita texto em uma coordenada
5. **`scroll_document`** - Rola a página inteira
6. **`scroll_at`** - Rola em uma coordenada específica
7. **`wait_5_seconds`** - Aguarda 5 segundos
8. **`go_back`** - Volta para a página anterior
9. **`go_forward`** - Avança para a próxima página
10. **`search`** - Navega para a página de busca
11. **`navigate`** - Navega para uma URL específica
12. **`key_combination`** - Pressiona combinação de teclas
13. **`drag_and_drop`** - Arrasta e solta elementos

## 🔍 Verificação

O Computer Use está **sempre ativo** porque:

1. ✅ Está configurado no `GenerateContentConfig`
2. ✅ É parte obrigatória das ferramentas (`tools`)
3. ✅ O ambiente está definido como `ENVIRONMENT_BROWSER`
4. ✅ Todas as funções pré-definidas estão disponíveis

## 📝 Como o Gemini Usa o Computer Use

Quando você envia uma query:

1. **O Gemini analisa** sua query
2. **Identifica ações necessárias** (navegar, clicar, digitar, etc.)
3. **Gera chamadas de função** usando as ferramentas do Computer Use
4. **O agente executa** essas funções no navegador
5. **Captura o estado** (screenshot, URL atual)
6. **Envia de volta** para o Gemini continuar

## 🚀 Exemplo de Uso

Quando você escreve:
```
Navegue para https://github.com
Clique no botão "Sign in"
```

O Gemini automaticamente:
1. Chama `navigate(url="https://github.com")`
2. Captura screenshot da página
3. Analisa o screenshot
4. Identifica o botão "Sign in"
5. Chama `click_at(x=coordenada_x, y=coordenada_y)`
6. Continua o processo

## ⚙️ Configurações Atuais

- **Environment**: `ENVIRONMENT_BROWSER` (navegador web)
- **Excluded Functions**: Nenhuma (todas disponíveis)
- **Custom Functions**: `multiply_numbers` (exemplo)
- **Temperature**: 1.0
- **Max Output Tokens**: 8192

## 🔒 Garantias

- ✅ Computer Use **sempre está ativo**
- ✅ Não pode ser desabilitado
- ✅ Todas as funções estão disponíveis
- ✅ Screenshots são capturados automaticamente
- ✅ Estado do ambiente é mantido

## 📚 Documentação Oficial

Para mais informações sobre Computer Use:
- [Documentação Gemini Computer Use](https://ai.google.dev/gemini-api/docs/computer-use)
- [Funções Pré-definidas](https://ai.google.dev/gemini-api/docs/computer-use#predefined-functions)

