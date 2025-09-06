# Deploy no Railway - Crypto Arbitrage Monitor

## Pré-requisitos

1. Conta no Railway (https://railway.app)
2. Git configurado
3. Projeto no GitHub/GitLab

## Passos para Deploy

### 1. Preparar o Repositório

```bash
# Fazer commit de todos os arquivos
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Conectar ao Railway

1. Acesse https://railway.app
2. Faça login com sua conta
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha o repositório do projeto

### 3. Configurar Variáveis de Ambiente

No dashboard do Railway, vá para "Variables" e adicione:

```env
# Configurações básicas
DEBUG=false
LOG_LEVEL=info
HOST=0.0.0.0

# CORS (ajuste com seus domínios)
ALLOWED_ORIGINS=https://your-frontend.railway.app

# Configurações de arbitragem
MIN_PROFIT_PERCENTAGE=0.5
MAX_PRICE_DIFFERENCE=10.0
UPDATE_INTERVAL=30
```

### 4. Deploy

O Railway irá automaticamente:
- Detectar que é um projeto Python
- Instalar dependências do `requirements.txt`
- Executar o comando definido no `railway.json`

### 5. Verificar Deploy

Após o deploy, você receberá uma URL como:
`https://your-app-name.railway.app`

Teste os endpoints:
- Health check: `https://your-app-name.railway.app/health`
- API docs: `https://your-app-name.railway.app/docs`
- Preços BTC: `https://your-app-name.railway.app/api/v1/prices/BTC`

## Estrutura de Arquivos para Railway

```
crypto-arbitrage/
├── railway.json          # Configuração do Railway
├── Procfile             # Comando de start alternativo
├── requirements.txt     # Dependências Python
├── runtime.txt          # Versão do Python
├── env.example          # Exemplo de variáveis
├── railway.env          # Configurações específicas
└── app/
    ├── main.py          # Aplicação FastAPI
    ├── config.py        # Configurações
    └── ...
```

## Comandos de Deploy

### Usando railway.json (recomendado)
```json
{
  "deploy": {
    "startCommand": "cd app && python -m uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health"
  }
}
```

### Usando Procfile (alternativo)
```
web: cd app && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Troubleshooting

### Erro de Porta
- Certifique-se de usar `$PORT` (variável do Railway)
- Host deve ser `0.0.0.0`

### Erro de Dependências
- Verifique se `requirements.txt` está na raiz
- Todas as dependências devem estar listadas

### Erro de CORS
- Configure `ALLOWED_ORIGINS` com seus domínios
- Use vírgulas para separar múltiplos domínios

### Logs
- Use o dashboard do Railway para ver logs
- Configure `LOG_LEVEL=debug` para mais detalhes

## Monitoramento

O Railway fornece:
- Health check automático em `/health`
- Logs em tempo real
- Métricas de uso
- Deploy automático a cada push

## Próximos Passos

1. Configurar domínio customizado
2. Adicionar banco de dados PostgreSQL
3. Configurar notificações
4. Implementar cache Redis
5. Adicionar monitoramento avançado