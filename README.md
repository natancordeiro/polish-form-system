# Sistema de Requerimento de Cidadania Polonesa

Sistema web que permite o preenchimento do formulário oficial
**"Wniosek o potwierdzenie posiadania lub utraty obywatelstwa polskiego"**
em português, gerando automaticamente o PDF final em polonês
**idêntico ao modelo oficial** — com cada letra encaixada em sua caixinha.

**Stack**

- **Backend**: Python 3.10+ · FastAPI · PyMuPDF · DeepL API
- **Frontend**: React 18 · Vite · TailwindCSS · react-hook-form · Zod

---

## 1. Como funciona

```
┌─────────────┐   JSON    ┌───────────────────────────┐   PDF    ┌──────────┐
│  Frontend   │──────────▶│  FastAPI + DeepL          │─────────▶│  Wniosek │
│  (React)    │           │  + PyMuPDF                │          │  (PL)    │
│    PT-BR    │◀──────────│  escreve no template      │◀─────────│          │
└─────────────┘  download │  oficial (11 páginas)     │          └──────────┘
                          └───────────────────────────┘
```

**Pipeline de geração do PDF:**

1. O usuário preenche um formulário de 6 etapas em **português**.
2. Valores fechados (sexo, estado civil, países, voivodias) são traduzidos
   via dicionário interno — garantindo os termos oficiais poloneses
   (`MĘŻATKA`, `ŻONATY`, `BRAZYLIA`, `WOJEWODA`, etc.).
3. Textos livres (biografias, justificativas) são enviados à **DeepL API**.
4. O PDF é gerado **abrindo o template oficial** (`official_form.pdf`) e
   **escrevendo o texto por cima** usando PyMuPDF:
   - Detecta automaticamente as ~160 caixinhas de cada página
   - Distribui cada letra no seu quadradinho individual
   - Marca checkboxes com X desenhado
   - Preenche textos livres sobre as linhas pontilhadas com word-wrap
5. O download é disparado direto no navegador (sem persistência).

**Fonte:** DejaVu Sans é embarcada no PDF para suportar todos os diacríticos
poloneses (`Ł`, `Ó`, `Ś`, `Ż`, `Ę`, `Ą`, `Ć`, `Ń`).

---

## 2. Pré-requisitos

| Requisito          | Versão mínima   | Notas                                            |
| ------------------ | --------------- | ------------------------------------------------ |
| Python             | 3.10            | 3.11+ recomendado                                |
| Node.js            | 18              | Apenas para buildar o frontend                   |
| Chave DeepL API    | Free ou Pro     | [deepl.com/pro-api](https://www.deepl.com/pro-api) |

> **Sem dependências de sistema** — PyMuPDF já inclui tudo que precisa
> (diferente do WeasyPrint, que exige Pango e libs de renderização).

---

## 3. Tutorial passo a passo

### Passo 1 — Clone/extraia o projeto

```bash
cd polish-form-system
```

Estrutura:

```
polish-form-system/
├── backend/         # API FastAPI + gerador de PDF
├── frontend/        # SPA React
└── README.md
```

### Passo 2 — Obtenha uma chave DeepL

1. Cadastre-se em https://www.deepl.com/pro-api no plano **Free**
   (500.000 caracteres/mês de graça — suficiente para o uso real).
2. Copie a **Authentication Key** (formato `xxxxx:fx` para free, sem `:fx` para pro).

### Passo 3 — Configure o backend

```bash
cd backend
cp .env.example .env
```

Edite `.env`:

```env
DEEPL_API_KEY=sua_chave_aqui:fx
```

> **Sem a chave, o sistema ainda gera o PDF** — mas os textos livres
> sairão em português (maiúsculas). Útil para validar layout sem gastar
> cota DeepL.

### Passo 4 — Rode o backend

**Atalho** (Linux/macOS):

```bash
./run.sh
```

**Manualmente:**

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend estará em `http://localhost:8000`.

Teste:

```bash
curl http://localhost:8000/api/health
# {"status":"ok","deepl_configured":true,...}
```

### Passo 5 — Rode o frontend

Em **outro terminal**:

```bash
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`.

O Vite faz proxy automático das chamadas `/api/*` para `localhost:8000`.

### Passo 6 — Preencha o formulário

Um stepper visual guia por 6 etapas:

1. **Cabeçalho** — local, data, voivoda, requerente
2. **Beneficiado** — dados pessoais de quem tem direito à cidadania
3. **Pais** — dados completos da mãe e do pai
4. **Avós** — quatro avós (dados essenciais)
5. **Biografias** — textos livres que serão traduzidos pelo DeepL
6. **Info & Anexos** — informações adicionais + lista de documentos

Clique em **"Gerar PDF em Polonês"** — o download é disparado automaticamente.

> **Auto-save**: o formulário é salvo no `localStorage` do navegador.
> Feche e reabra a aba que seus dados continuam. Botão **"Limpar rascunho"**
> no topo para resetar.

---

## 4. Teste rápido (só backend)

Para validar a geração sem subir frontend:

```bash
cd backend
python smoke_test.py
```

Gera `sample_output.pdf` usando os dados do Luiz Ricardo como exemplo —
útil para validar layout antes de configurar DeepL.

---

## 5. Arquitetura do código

### Backend

```
backend/
├── app/
│   ├── main.py                # FastAPI: /api/health, /api/generate-pdf
│   ├── config.py              # Settings via Pydantic (.env)
│   ├── schemas.py             # Modelos Pydantic do formulário
│   ├── fonts/
│   │   ├── DejaVuSans.ttf     # Fonte embarcada (cobre diacríticos PL)
│   │   └── DejaVuSans-Bold.ttf
│   ├── templates/
│   │   └── official_form.pdf  # Template oficial polonês (11 páginas)
│   └── services/
│       ├── box_detector.py    # Detecta caixinhas automaticamente
│       ├── template_filler.py # Handlers: char_boxes, date_boxes, text_block
│       ├── field_mapper.py    # Dicionários PT→PL (enums)
│       ├── translator.py      # DeepL + cache em memória
│       └── pdf_generator.py   # Pipeline: FormData → PDF (11 fillers)
├── smoke_test.py              # Teste E2E com dados do Luiz Ricardo
├── requirements.txt
├── run.sh                     # Script de conveniência
└── .env.example
```

**Arquitetura do gerador de PDF:**

- `box_detector.detect_all_rows()` varre o template e extrai, por página,
  as fileiras horizontais de caixinhas (~17.2pt × 8pt) detectadas como
  desenhos de linhas verticais consecutivas. Cacheado (roda uma vez).
- `template_filler` oferece handlers de baixo nível:
  - `write_char_boxes(page, text, row)` — uma letra por caixinha, centralizada
  - `write_date_boxes(page, iso_date, row)` — data no padrão YYYY/MM/DD
    respeitando os separadores `/` desenhados
  - `write_two_field_row(page, row, left, right)` — duas sub-fileiras separadas
    por gap (ex: Numer domu + Numer mieszkania)
  - `write_text_block(page, text, x, y, max_width, max_lines)` — texto livre
    sobre linhas pontilhadas, com word-wrap
  - `draw_checkbox_cross(page, x, y)` — marca X em checkbox
- `pdf_generator` tem uma função `_fill_page_N(page, rows, data)` para
  cada uma das 11 páginas, que combina os handlers para montar o conteúdo.
- `ensure_fonts(page)` registra DejaVu Sans em cada página antes de escrever
  (necessário para os diacríticos poloneses).

### Frontend

```
frontend/
├── src/
│   ├── App.jsx                # Orquestra os 6 steps + submissão
│   ├── main.jsx
│   ├── index.css              # Tailwind + classes customizadas
│   ├── lib/
│   │   └── schema.js          # Zod (espelha Pydantic) + valores iniciais
│   ├── services/
│   │   └── api.js             # Cliente HTTP + download do PDF
│   └── components/
│       ├── FormFields.jsx     # Input, Textarea, Select, Checkbox
│       ├── PersonFields.jsx   # Bloco reutilizado em solicitante/pais/avós
│       ├── Stepper.jsx        # Barra de progresso
│       └── steps/             # Uma JSX por etapa
└── vite.config.js
```

**Decisões importantes:**

- **Multi-step com validação por etapa** — `trigger(fields)` do
  react-hook-form valida só os campos da etapa antes de avançar.
- **Persistência em localStorage** — auto-save a cada mudança.
- **Um único schema Zod** espelhando o Pydantic do servidor.

---

## 6. Customização

### Adicionar um novo país à tradução

Edite `backend/app/services/field_mapper.py`:

```python
PAIS_MAP = {
    ...
    "seu_pais": "SEU_PAIS_EM_POLONES",
}
```

### Ajustar posição de um campo no PDF

As coordenadas de **texto livre** (wojewoda, checkboxes, biografias) ficam
em `backend/app/services/pdf_generator.py`, nas funções `_fill_page_N`.

As coordenadas de **caixinhas** são detectadas automaticamente — não é
necessário calibrar.

### Atualizar o template oficial

Se o governo polonês atualizar o formulário:

1. Substitua `backend/app/templates/official_form.pdf`.
2. Rode `python smoke_test.py` e inspecione o PDF gerado.
3. Ajuste os mapeamentos `rows[i]` nas funções `_fill_page_N` se necessário.

---

## 7. Deploy em produção

### Build estático do frontend

```bash
cd frontend
npm run build      # gera frontend/dist/
```

### Docker (sugestão)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Nenhuma dependência de sistema extra — PyMuPDF já traz tudo.

---

## 8. Troubleshooting

| Sintoma                                                | Solução                                                   |
| ------------------------------------------------------ | --------------------------------------------------------- |
| Banner "DeepL não configurado" no frontend             | Edite `.env` e reinicie o backend                         |
| PDF sai com textos em português maiúsculo              | Idem — chave DeepL ausente ou inválida                    |
| Caracteres Ł/Ó/Ź aparecem vazios                       | Fontes DejaVu estão em `app/fonts/`? Re-instale deps      |
| Erro 422 ao submeter                                   | Campo obrigatório vazio — veja log do backend             |
| Frontend não alcança o backend                         | Confirme backend em `:8000` (proxy Vite configurado)      |
| Caixinha não preenche                                  | Verifique mapeamento em `_fill_page_N` no `pdf_generator` |

---

## 9. Créditos

Projeto desenvolvido por **TGN Technologies** (Natan Targino).

Formulário base: documento oficial do governo polonês
(_Wojewoda Mazowiecki_ — 11 páginas + instruções).
