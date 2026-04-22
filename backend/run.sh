#!/usr/bin/env bash
# Script de conveniência para subir o backend em desenvolvimento.
# Uso:  ./run.sh
set -e

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "→ Criando virtualenv…"
  python3 -m venv venv
fi

source venv/bin/activate

echo "→ Instalando dependências…"
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  echo "⚠  Arquivo .env não encontrado. Copiando de .env.example…"
  cp .env.example .env
  echo "   Edite o .env e adicione sua DEEPL_API_KEY antes de continuar."
fi

echo "→ Iniciando servidor em http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
