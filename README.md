# Workana Freela

Aplicação unificada que combina o scraper Workana com o dashboard React para análise de projetos freelancer.

## Estrutura do Projeto

```
workanaFreela/
├── main.py                 # Servidor FastAPI principal
├── requirements.txt        # Dependências Python
├── .env                   # Variáveis de ambiente
├── Dockerfile             # Configuração Docker
├── docker-compose.yml     # Orquestração Docker
├── frontend/              # Frontend React
│   ├── src/               # Código fonte React
│   ├── package.json       # Dependências Node.js
│   └── .env               # Variáveis de ambiente do frontend
└── backend/               # Código original do worker (backup)
```

## Funcionalidades

### Backend (FastAPI)
- **Endpoint de Scraping**: `/api/scrape` - Executa scraping da Workana
- **Health Check**: `/api/health` - Verifica status da aplicação
- **Servidor de Frontend**: Serve os arquivos estáticos do React

### Frontend (React + Vite)
- Dashboard com análise de projetos por:
  - 🔥 Temperatura (projetos mais quentes)
  - 🎯 Competição (menor número de propostas)
  - ⏰ Recência (mais recentes)
- Filtros por status de contato
- Atualização automática via API

## Configuração

### Variáveis de Ambiente

Copie o arquivo `.env` e configure:

```env
# Credenciais Workana
WORKANA_EMAIL=seu_email@exemplo.com
WORKANA_PASSWORD=sua_senha

# Configuração Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_chave_anonima

# Webhook (opcional)
WEBHOOK_URL=https://seu-webhook.com/endpoint
```

## Desenvolvimento Local

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- Docker (opcional)

### Instalação

1. **Clone o repositório**:
```bash
git clone https://github.com/FresHHerB/workanaFreela.git
cd workanaFreela
```

2. **Configure as variáveis de ambiente**:
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

3. **Instalar dependências do backend**:
```bash
pip install -r requirements.txt
playwright install chromium
```

4. **Instalar dependências do frontend**:
```bash
cd frontend
npm install
```

5. **Build do frontend**:
```bash
npm run build
cd ..
```

6. **Executar a aplicação**:
```bash
python main.py
```

A aplicação estará disponível em `http://localhost:8000`

## Deploy com Docker

### Build e execução local
```bash
docker-compose up --build
```

### Deploy no EasyPanel

1. **Configure o repositório Git**:
   - URL: `https://github.com/FresHHerB/workanaFreela`
   - Branch: `main`

2. **Configure as variáveis de ambiente no EasyPanel**:
   - `WORKANA_EMAIL`
   - `WORKANA_PASSWORD`
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `PORT=8000`

3. **Configure os domínios**:
   - **Dashboard**: `sua-aplicacao.exemplo.com` (porta 8000)
   - **API Scraping**: `sua-aplicacao.exemplo.com/api/scrape`

## Endpoints da API

- `GET /` - Dashboard principal
- `GET /api/health` - Health check
- `GET /api/scrape` - Executar scraping da Workana

## Arquitetura

A aplicação usa uma arquitetura híbrida:

1. **Backend FastAPI**: Gerencia o scraping e serve a API
2. **Frontend React**: Interface do usuário para visualização
3. **Roteamento**: FastAPI serve tanto a API quanto os arquivos estáticos
4. **Integração**: Frontend faz chamadas para `/api/scrape` internamente

## Monitoramento

- Health check disponível em `/api/health`
- Logs da aplicação via Docker/EasyPanel
- Frontend inclui tratamento de erros e loading states