# 🚀 Guia: Corrigindo Página em Branco - Bolt.new → EasyPanel

## 📋 Problema
Frontend React/Vite criado no Bolt.new exibe **página em branco** quando deployado no EasyPanel, mesmo com build aparentemente bem-sucedido.

## 🔍 Diagnóstico Rápido

### Sintomas:
- ✅ Build Docker passa sem erros
- ✅ Arquivos estáticos são servidos (CSS, JS)
- ❌ Página fica em branco ou trava no loading
- ❌ Console do navegador pode mostrar erros de variáveis de ambiente

### Causas Principais:
1. **Variáveis de ambiente não injetadas no build Vite**
2. **Configuração Vite inadequada para produção**
3. **Arquivos `src/lib/` bloqueados pelo gitignore**
4. **Ordem incorreta no Dockerfile**

## 🛠️ Solução Passo-a-Passo

### 1. **Corrigir vite.config.ts**
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/',                    // ← CRÍTICO: Base path explícito
  build: {
    outDir: 'dist',            // ← CRÍTICO: Output explícito
    assetsDir: 'assets',       // ← CRÍTICO: Assets explícito
    sourcemap: false,          // ← Otimização para produção
    rollupOptions: {
      output: {
        manualChunks: undefined, // ← Evita problemas de chunks
      },
    },
  },
  server: {
    host: true,
    port: 5173,
  },
  preview: {
    host: true,
    port: 4173,
  },
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
});
```

### 2. **Atualizar package.json**
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "build:check": "vite build && ls -la dist/",  // ← Debug script
    "lint": "eslint .",
    "preview": "vite preview --host"              // ← Host para preview
  }
}
```

### 3. **Corrigir .gitignore**
```gitignore
# Python lib directory (not src/lib)
lib/
!src/lib/          # ← CRÍTICO: Permitir src/lib/
!frontend/src/lib/ # ← Backup para estruturas antigas
```

### 4. **Dockerfile Otimizado**

#### ❌ Versão Problemática:
```dockerfile
# Variáveis depois da cópia
COPY package*.json ./
RUN npm ci
COPY src/ ./src/
# ENV depois da cópia - ERRO!
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
```

#### ✅ Versão Corrigida:
```dockerfile
FROM node:18-alpine AS frontend-builder
WORKDIR /app

# CRÍTICO: Variáveis ANTES da cópia
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ARG VITE_WEBHOOK_URL
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY
ENV VITE_WEBHOOK_URL=$VITE_WEBHOOK_URL

# Package files primeiro
COPY package*.json ./
RUN npm ci

# Copiar tudo de uma vez
COPY . .

# Debug: Verificar env vars
RUN echo "Building with VITE_SUPABASE_URL: $VITE_SUPABASE_URL"
RUN echo "Building with VITE_WEBHOOK_URL: $VITE_WEBHOOK_URL"

# Build
RUN npm run build

# Debug: Verificar arquivos gerados
RUN ls -la /app/dist/
```

### 5. **Arquivo .env Local**
```env
# Backend (Python/FastAPI)
WORKANA_EMAIL=seu_email
WORKANA_PASSWORD=sua_senha
PORT=8000
HOST=0.0.0.0
DEBUG=true

# Frontend (Vite - apenas para desenvolvimento local)
VITE_SUPABASE_URL=https://seu-projeto.supabase.co
VITE_SUPABASE_ANON_KEY=sua_anon_key
VITE_WEBHOOK_URL=https://seu-webhook.url
```

## 🔧 Comandos de Verificação

### Build Local:
```bash
npm run build:check
# Deve mostrar: dist/index.html, dist/assets/, dist/vite.svg
```

### Verificar Git:
```bash
git ls-files src/lib/
# Deve listar: src/lib/supabase.ts (ou similar)
```

### Debug Ambiente:
```bash
# No código JavaScript, adicione temporariamente:
console.log('Environment Debug:', {
  url: import.meta.env.VITE_SUPABASE_URL,
  webhook: import.meta.env.VITE_WEBHOOK_URL
});
```

## 📊 Comparação: Funcionando vs Problemático

| Aspecto | ❌ Problemático | ✅ Funcionando |
|---------|----------------|----------------|
| **ENV no Dockerfile** | Depois do COPY | Antes do COPY |
| **vite.config.ts** | Mínimo | Completo com base/build |
| **Build output** | Genérico | Com debug logs |
| **src/lib/** | Bloqueado no git | Incluído no git |
| **package.json** | Scripts básicos | Com build:check |

## 🚨 Checklist de Emergência

Quando enfrentar página em branco:

1. [ ] **ENV vars estão sendo passadas no build?**
   - Verificar ordem no Dockerfile
   - Adicionar debug logs

2. [ ] **src/lib/ está no Git?**
   - `git ls-files src/lib/`
   - Corrigir .gitignore se necessário

3. [ ] **vite.config.ts está completo?**
   - base: '/', outDir: 'dist', assetsDir: 'assets'
   - manualChunks: undefined

4. [ ] **Console do navegador mostra erros?**
   - F12 → Console
   - Procurar por erros de import/environment

5. [ ] **Build local funciona?**
   - `npm run build:check`
   - Verificar se gera dist/ corretamente

## 🎯 Solução Expressa (5 minutos)

```bash
# 1. Copiar vite.config.ts de projeto funcionando
cp /caminho/para/dash-workana/vite.config.ts ./

# 2. Atualizar package.json scripts
# (adicionar build:check e preview --host)

# 3. Corrigir gitignore
echo "!src/lib/" >> .gitignore

# 4. Adicionar src/lib/ ao git
git add src/lib/

# 5. Verificar Dockerfile
# (ENV vars antes de COPY, debug logs)

# 6. Commit e push
git add -A
git commit -m "Fix: Apply frontend corrections for EasyPanel"
git push
```

## 📈 Commits de Referência

- **04ff07c**: Fix gitignore e adicionar src/lib/
- **1877f5c**: Apply dash-workana corrections (vite.config + Dockerfile)
- **3405a2e**: Restructure frontend (mover para root)

## 💡 Dica Final

**Sempre compare com um projeto Vite funcionando no EasyPanel** antes de debugar por horas. A diferença geralmente está em detalhes de configuração que não são óbvios.

---
*Guia criado após resolver problema de página em branco no workanaFreela*