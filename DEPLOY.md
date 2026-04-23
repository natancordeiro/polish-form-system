# 🚀 Deploy no Easypanel — Polish Form System

## Estrutura do projeto após adicionar os arquivos

```
polish-form-system/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile          ← NOVO
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── nginx.conf          ← NOVO
│   └── Dockerfile          ← NOVO
└── docker-compose.yml      ← NOVO (para testes locais)
```

---

## Passo 1 — Adicione os arquivos ao seu projeto

Copie os arquivos fornecidos para as pastas correspondentes do seu projeto:

- `Dockerfile` → dentro de `backend/`
- `Dockerfile` + `nginx.conf` → dentro de `frontend/`
- `docker-compose.yml` → na raiz do projeto

---

## Passo 2 — Suba o código para um repositório Git

O Easypanel puxa o código via Git. Se ainda não tiver:

```bash
git init
git add .
git commit -m "Add Dockerfiles for Easypanel deploy"
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
git push -u origin main
```

> **Importante:** Adicione `backend/.env` no `.gitignore` para não expor suas chaves.

---

## Passo 3 — Configure o Backend no Easypanel

1. No Easypanel, clique em **"Create Service"** → **"App"**
2. Dê o nome: `polish-backend`
3. Em **Source**, escolha **Git** e conecte seu repositório
4. Em **Build**, defina:
   - **Root Directory:** `backend`
   - **Dockerfile:** `Dockerfile` (já detectado automaticamente)
5. Em **Ports**, adicione: `8000`
6. Em **Environment Variables**, adicione:
   ```
   DEEPL_API_KEY=sua_chave_deepl_aqui
   API_HOST=0.0.0.0
   API_PORT=8000
   ENABLE_TRANSLATION_CACHE=true
   ```
7. Clique em **Deploy**
8. Após subir, copie o **domínio gerado** (ex: `polish-backend.seuservidor.com`)

---

## Passo 4 — Configure o Frontend no Easypanel

1. Clique em **"Create Service"** → **"App"**
2. Dê o nome: `polish-frontend`
3. Em **Source**, escolha o mesmo repositório Git
4. Em **Build**, defina:
   - **Root Directory:** `frontend`
   - **Dockerfile:** `Dockerfile`
   - **Build Arguments:**
     ```
     VITE_API_URL=https://polish-backend.seuservidor.com
     ```
     ⚠️ Substitua pela URL real do backend criado no passo anterior
5. Em **Ports**, adicione: `80`
6. Em **Environment Variables**, adicione o CORS no backend:
   ```
   CORS_ORIGINS=https://polish-frontend.seuservidor.com
   ```
   (ajuste também essa variável no serviço do backend)
7. Clique em **Deploy**

---

## Passo 5 — Ajuste o CORS no backend

Volte ao serviço `polish-backend` e atualize a variável:

```
CORS_ORIGINS=https://polish-frontend.seuservidor.com
```

Isso permite que o frontend acesse o backend sem bloqueio de CORS.

---

## Teste rápido

Após o deploy, acesse:

```
https://polish-backend.seuservidor.com/api/health
```

Deve retornar:
```json
{"status": "ok", "deepl_configured": true, "timestamp": "..."}
```

---

## Dicas

- **`deepl_configured: false`** → a `DEEPL_API_KEY` não foi configurada no Easypanel
- **Erro de CORS no browser** → revise o valor de `CORS_ORIGINS` no backend
- **Frontend não encontra o backend** → confira se `VITE_API_URL` aponta para o domínio correto (com `https://`)
- Para **testar localmente** antes do deploy:
  ```bash
  cp backend/.env.example backend/.env
  # edite backend/.env e adicione sua DEEPL_API_KEY
  docker compose up --build
  ```
