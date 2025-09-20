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

Copie o arquivo `.env.example` para `.env` e configure:

```env
# Backend - Workana scraping (obrigatório)
WORKANA_EMAIL=seu_email@exemplo.com
WORKANA_PASSWORD=sua_senha

# Frontend - Supabase database (obrigatório)
VITE_SUPABASE_URL=https://seu-projeto.supabase.co
VITE_SUPABASE_ANON_KEY=sua_chave_anonima

# Webhook integration (obrigatório para botão "Atualizar Dados")
VITE_WEBHOOK_URL=https://seu-n8n-webhook.com/webhook/update_freela

# Servidor (opcional)
PORT=8000
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

2. **Configure estas variáveis no EasyPanel**:

   **Obrigatórias:**
   - `WORKANA_EMAIL=seu_email@workana.com`
   - `WORKANA_PASSWORD=sua_senha`
   - `VITE_SUPABASE_URL=https://seu-projeto.supabase.co`
   - `VITE_SUPABASE_ANON_KEY=sua_chave_anonima`
   - `VITE_WEBHOOK_URL=https://seu-n8n-webhook.com/webhook/update_freela`

   **Opcionais:**
   - `PORT=8000` (padrão é 8000)

3. **Configure os domínios**:
   - **Dashboard**: `sua-aplicacao.exemplo.com` (porta 8000)
   - **API Scraping**: `sua-aplicacao.exemplo.com/api/scrape`

## Endpoints da API

- `GET /` - Dashboard principal
- `GET /api/health` - Health check
- `GET /api/scrape` - Executar scraping da Workana

## Arquitetura

A aplicação usa uma arquitetura simples e eficiente:

1. **Backend FastAPI**: Realiza scraping da Workana e salva no Supabase
2. **Frontend React**: Dashboard para visualização dos dados do Supabase
3. **Webhook/n8n**: Dispara o scraping via chamada para /api/scrape
4. **Fluxo**: Webhook → Backend scrapes → Salva no Supabase → Frontend lê

### Fluxo de Dados
```
n8n/Webhook → /api/scrape → Backend scraping → Salva no Supabase
                                ↓
                           Resposta JSON
                                ↓
Frontend Dashboard ← Lê do Supabase ← Dados atualizados
```

## Monitoramento

- Health check disponível em `/api/health`
- Logs da aplicação via Docker/EasyPanel
- Frontend inclui tratamento de erros e loading states