# 🔧 Troubleshooting - Resolução de Problemas

## Erro: "Resposta sem candidatos!"

Este erro ocorre quando a API do Gemini retorna uma resposta sem candidatos. Aqui estão as causas mais comuns e soluções:

### 🔍 Diagnóstico

Execute o script de diagnóstico:

```bash
docker-compose exec gemini-computer-use python diagnose_api.py
```

Ou localmente:

```bash
python diagnose_api.py
```

### 📋 Causas Comuns e Soluções

#### 1. API Key Inválida ou Expirada

**Sintomas:**
- Erro de autenticação
- "Invalid API key"

**Solução:**
1. Verifique se a API key está correta no arquivo `.env`
2. Gere uma nova API key em: https://aistudio.google.com/app/apikey
3. Atualize o arquivo `.env`:
   ```
   GEMINI_API_KEY=sua_nova_api_key_aqui
   ```
4. Reinicie o container:
   ```bash
   docker-compose restart
   ```

#### 2. Rate Limiting / Quota Excedida

**Sintomas:**
- Erros 429 (Too Many Requests)
- Mensagens sobre quota

**Solução:**
- Aguarde alguns minutos antes de tentar novamente
- Verifique sua quota em: https://aistudio.google.com/app/apikey
- Considere usar um plano pago se necessário

#### 3. Filtros de Segurança

**Sintomas:**
- Prompt feedback indicando bloqueio
- Mensagens sobre "safety" ou "block_reason"

**Solução:**
- A query pode estar sendo bloqueada por filtros de segurança
- Tente reformular a query de forma mais clara e menos ambígua
- Evite queries que possam ser interpretadas como maliciosas

#### 4. Modelo Não Disponível

**Sintomas:**
- Erro 404 ou "model not found"
- Modelo específico não disponível

**Solução:**
- Verifique se o modelo está disponível na sua região
- Tente usar outro modelo (verifique modelos disponíveis)
- O modelo `gemini-2.5-computer-use-preview-10-2025` pode não estar disponível em todas as regiões

#### 5. Problemas com a Ferramenta Computer Use

**Sintomas:**
- Erro sobre "Computer Use tool required"
- Resposta vazia mesmo com a ferramenta configurada

**Solução:**
- Verifique se o modelo suporta Computer Use
- Certifique-se de que a ferramenta está sendo enviada corretamente
- Verifique os logs detalhados para mais informações

### 📊 Logs Detalhados

Com o sistema de logging implementado, você pode ver logs detalhados:

```bash
# Ver logs do container
docker-compose logs -f gemini-computer-use

# Ver apenas erros
docker-compose logs gemini-computer-use | grep ERROR

# Ver logs em tempo real
docker-compose logs -f gemini-computer-use | grep -E "ERROR|WARNING|INFO"
```

### 🔄 Retry Automático

O sistema já implementa retry automático (até 5 tentativas) com backoff exponencial. Se o erro persistir após todas as tentativas, verifique:

1. **Logs completos** para ver o erro específico
2. **Status da API** do Google
3. **Sua quota** de API

### 🛠️ Verificações Rápidas

```bash
# 1. Verificar variáveis de ambiente
docker-compose exec gemini-computer-use env | grep GEMINI

# 2. Testar API
docker-compose exec gemini-computer-use python diagnose_api.py

# 3. Verificar logs recentes
docker-compose logs --tail=50 gemini-computer-use

# 4. Verificar status do container
docker-compose ps
```

### 📝 Informações para Suporte

Se o problema persistir, colete estas informações:

1. **Logs completos:**
   ```bash
   docker-compose logs gemini-computer-use > logs_completos.txt
   ```

2. **Resultado do diagnóstico:**
   ```bash
   docker-compose exec gemini-computer-use python diagnose_api.py > diagnostico.txt
   ```

3. **Configuração (sem API keys):**
   - Modelo usado
   - Ambiente (playwright/browserbase)
   - Query que causou o erro

### ✅ Checklist de Verificação

- [ ] API Key está configurada e válida
- [ ] API Key tem permissões adequadas
- [ ] Quota não foi excedida
- [ ] Modelo está disponível na sua região
- [ ] Query não está sendo bloqueada por segurança
- [ ] Container está rodando corretamente
- [ ] Logs não mostram outros erros

### 🔗 Links Úteis

- [Documentação Gemini API](https://ai.google.dev/gemini-api/docs)
- [Computer Use Documentation](https://ai.google.dev/gemini-api/docs/computer-use)
- [Status da API Google](https://status.cloud.google.com/)
- [Gerenciar API Keys](https://aistudio.google.com/app/apikey)

