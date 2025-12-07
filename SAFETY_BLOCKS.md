# 🛡️ Tratamento de Bloqueios de Segurança

## O que são Bloqueios de Segurança?

Os bloqueios de segurança ocorrem quando a API do Gemini detecta que uma query pode violar suas políticas de segurança ou ser interpretada como maliciosa.

## Como o Sistema Trata Bloqueios

### Detecção Automática

O sistema detecta automaticamente quando uma resposta é bloqueada:

```
🚫 BLOQUEIO DE SEGURANÇA DETECTADO
Razão: BlockedReason.OTHER
```

### Retry Automático

Quando um bloqueio é detectado:

1. **Primeira vez**: O sistema tenta continuar automaticamente
2. **Segunda vez**: Ainda tenta continuar, mas com aviso
3. **Terceira vez**: Para o agente para evitar loop infinito

### Mensagens de Ajuda

Quando um bloqueio ocorre, você verá:

- Razão do bloqueio
- Mensagem explicativa (se disponível)
- Safety ratings detalhados
- Sugestões de como resolver

## Como Resolver Bloqueios

### 1. Reformular a Query

**❌ Evite:**
```
"Delete all files"
"Hack into website"
"Bypass security"
```

**✅ Use:**
```
"Navigate to settings page"
"Open the configuration menu"
"Access the admin panel"
```

### 2. Ser Mais Específico

**❌ Vago:**
```
"Do something dangerous"
```

**✅ Específico:**
```
"Click on the settings icon in the top right corner"
```

### 3. Dividir em Etapas

**❌ Complexo:**
```
"Go to the website, login, change password, and delete account"
```

**✅ Dividido:**
```
"Go to the website"
"Login with credentials"
"Navigate to account settings"
```

### 4. Evitar Termos Ambíguos

Evite palavras que possam ser interpretadas como:
- Maliciosas
- Destrutivas
- Enganosas
- Violentas

## Exemplos de Queries que Funcionam

✅ **Navegação:**
```
"Go to Google and search for 'Python tutorials'"
```

✅ **Interação:**
```
"Click on the login button and enter username"
```

✅ **Formulários:**
```
"Fill out the contact form with name and email"
```

✅ **Navegação em Sites:**
```
"Navigate to the products page and view item details"
```

## Monitoramento

O sistema registra:
- Número de bloqueios consecutivos
- Razão de cada bloqueio
- Tentativas de retry
- Quando o agente para devido a bloqueios

## Logs

Verifique os logs para detalhes:

```bash
docker-compose logs -f gemini-computer-use | grep -E "BLOQUEIO|safety|block"
```

## Limites

- **Máximo de 3 bloqueios consecutivos**: Após isso, o agente para
- **Máximo de 50 iterações**: Limite geral do loop do agente

## Dicas

1. **Seja claro e específico** na sua query
2. **Evite comandos que soem destrutivos**
3. **Use linguagem natural e descritiva**
4. **Divida tarefas complexas em etapas**
5. **Teste queries diferentes** se uma for bloqueada

## Suporte

Se bloqueios persistirem mesmo após reformular:
1. Verifique os logs detalhados
2. Tente uma abordagem completamente diferente
3. Consulte a documentação do Gemini sobre políticas de segurança

