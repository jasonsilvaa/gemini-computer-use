# 🔐 Sistema de Credenciais

Este sistema permite armazenar credenciais (email e senha) em um arquivo seguro e usá-las automaticamente nas queries do Gemini.

## 📁 Arquivos

- `credentials.json` - Arquivo com suas credenciais reais (NÃO commitar no Git!)
- `credentials.example.json` - Exemplo de estrutura do arquivo
- `credentials_loader.py` - Módulo para carregar e usar credenciais

## 🚀 Como Usar

### 1. Criar o arquivo de credenciais

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp credentials.example.json credentials.json
```

### 2. Editar credentials.json

```json
{
  "github": {
    "email": "seu_email@example.com",
    "password": "sua_senha_aqui"
  }
}
```

### 3. Usar na Query

Você pode usar credenciais de duas formas:

#### Opção 1: Placeholders
```
Navegue para github.com
Clique em "Sign in"
Digite {email} no campo de email
Digite {password} no campo de senha
Clique em "Sign in"
```

#### Opção 2: Referências genéricas
```
Navegue para github.com
Clique em "Sign in"
Digite o email fornecido no campo de email
Digite a senha fornecida no campo de senha
Clique em "Sign in"
```

## 🔒 Segurança

### ⚠️ IMPORTANTE

- ✅ `credentials.json` está no `.gitignore` - NÃO será commitado
- ✅ Use `credentials.example.json` como template
- ❌ NUNCA commite `credentials.json` no Git
- ❌ NUNCA compartilhe suas credenciais

### Verificar se está no .gitignore

```bash
git check-ignore credentials.json
```

Se retornar o caminho, está protegido! ✅

## 📝 Exemplo Completo

### Query Original:
```
acesse o github
faça o login com o email de jasonsilvadev@gmail.com
coloque a senha J@lves94
```

### Query Melhorada (usando credenciais):
```
Navegue para github.com
Clique no botão "Sign in" no canto superior direito
Na página de login, digite o email fornecido no campo de email
Digite a senha fornecida no campo de senha
Clique no botão "Sign in" para fazer login
```

### credentials.json:
```json
{
  "github": {
    "email": "jasonsilvadev@gmail.com",
    "password": "J@lves94"
  }
}
```

## 🎯 Múltiplos Serviços

Você pode armazenar credenciais para vários serviços:

```json
{
  "github": {
    "email": "user@example.com",
    "password": "senha123"
  },
  "google": {
    "email": "user@gmail.com",
    "password": "senha456"
  },
  "other": {
    "email": "user@other.com",
    "password": "senha789"
  }
}
```

Na interface web, selecione o serviço no dropdown "Serviço (para credenciais)".

## 🔧 Como Funciona

1. Você escreve a query usando placeholders ou referências genéricas
2. O sistema carrega `credentials.json`
3. Substitui os placeholders/referências pelas credenciais reais
4. Envia a query formatada para o Gemini

## 🐛 Troubleshooting

### Credenciais não estão sendo aplicadas

1. Verifique se `credentials.json` existe no diretório raiz
2. Verifique se o JSON está válido
3. Verifique se o serviço selecionado existe no arquivo
4. Veja os logs para mensagens de erro

### Arquivo não encontrado

```
Arquivo de credenciais não encontrado: credentials.json
Crie um arquivo credentials.json baseado em credentials.example.json
```

**Solução:** Crie o arquivo `credentials.json` baseado no exemplo.

### JSON inválido

```
Erro ao decodificar JSON do arquivo de credenciais
```

**Solução:** Verifique a sintaxe do JSON (vírgulas, chaves, etc.)

## 📚 API do Módulo

### Uso básico:

```python
from credentials_loader import load_credentials, format_query

# Carregar credenciais
creds = load_credentials('github')
email = creds['email']
password = creds['password']

# Formatar query
query = "Digite {email} e {password}"
formatted = format_query(query, 'github')
```

### Uso avançado:

```python
from credentials_loader import CredentialsLoader

loader = CredentialsLoader('credentials.json')
creds = loader.load()
email = loader.get_email('github')
password = loader.get_password('github')
```

## ✅ Checklist

- [ ] Arquivo `credentials.json` criado
- [ ] Credenciais preenchidas corretamente
- [ ] Arquivo está no `.gitignore`
- [ ] Query usa placeholders ou referências genéricas
- [ ] Serviço correto selecionado na interface web

## 🔗 Links Relacionados

- [QUERY_MELHORADA.md](./QUERY_MELHORADA.md) - Como melhorar queries
- [SAFETY_BLOCKS.md](./SAFETY_BLOCKS.md) - Sobre bloqueios de segurança

