"""
Serviço de tradução PT→PL via DeepL API.

Características:
- Cache em memória (evita traduzir a mesma string duas vezes)
- Tradução em lote (mais eficiente para múltiplos textos)
- Fallback silencioso: se a API falhar, retorna o texto original em MAIÚSCULAS
  (melhor que quebrar o fluxo e deixar o usuário sem PDF)
- Só traduz textos "longos" — nomes próprios, datas e códigos passam direto
"""
from __future__ import annotations

import logging
import re
from typing import Optional

import deepl

from app.config import settings

logger = logging.getLogger(__name__)

# Cache simples em memória. Em produção, trocar por Redis.
_CACHE: dict[str, str] = {}


# Regex que detecta se a string contém letras latinas (i.e. palavras para traduzir)
# Se a string for apenas números, pontuação ou códigos, não traduzimos.
_HAS_WORDS_RE = re.compile(r"[A-Za-zÀ-ÿ]{3,}")


class Translator:
    """Wrapper fino em cima do SDK oficial do DeepL."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.deepl_api_key
        self._client: Optional[deepl.Translator] = None

        if self.api_key:
            try:
                self._client = deepl.Translator(self.api_key)
                logger.info("DeepL client inicializado com sucesso.")
            except Exception as e:
                logger.warning("Falha ao inicializar DeepL: %s", e)
                self._client = None
        else:
            logger.warning("DEEPL_API_KEY não configurada — tradução desativada.")

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def translate(self, text: Optional[str]) -> str:
        """Traduz um único texto de PT para PL."""
        if not text or not text.strip():
            return ""

        text = text.strip()

        # Se não tem palavras reais (só números/datas/códigos) -> retorna como está
        if not _HAS_WORDS_RE.search(text):
            return text

        # Cache
        if settings.enable_translation_cache and text in _CACHE:
            return _CACHE[text]

        if not self._client:
            # Sem API — retorna o texto original em MAIÚSCULAS (padrão do formulário)
            return text.upper()

        try:
            result = self._client.translate_text(
                text, source_lang="PT", target_lang="PL"
            )
            translated = result.text.upper()  # formulário polonês é em CAIXA ALTA
            if settings.enable_translation_cache:
                _CACHE[text] = translated
            return translated
        except deepl.DeepLException as e:
            logger.error("Erro DeepL ao traduzir '%s...': %s", text[:50], e)
            return text.upper()
        except Exception as e:
            logger.exception("Erro inesperado na tradução: %s", e)
            return text.upper()

    def translate_batch(self, texts: list[str]) -> list[str]:
        """Traduz vários textos numa única chamada (mais eficiente)."""
        if not texts:
            return []

        results: list[Optional[str]] = [None] * len(texts)
        to_translate: list[tuple[int, str]] = []

        # Separa o que já está em cache do que precisa ir para a API
        for i, t in enumerate(texts):
            if not t or not t.strip():
                results[i] = ""
                continue
            stripped = t.strip()
            if not _HAS_WORDS_RE.search(stripped):
                results[i] = stripped
                continue
            if settings.enable_translation_cache and stripped in _CACHE:
                results[i] = _CACHE[stripped]
                continue
            to_translate.append((i, stripped))

        if not self._client or not to_translate:
            # Completa o que falta com UPPERCASE
            for i, t in to_translate:
                results[i] = t.upper()
            return [r or "" for r in results]

        try:
            batch = [t for _, t in to_translate]
            translations = self._client.translate_text(
                batch, source_lang="PT", target_lang="PL"
            )
            for (i, original), tr in zip(to_translate, translations):
                translated = tr.text.upper()
                results[i] = translated
                if settings.enable_translation_cache:
                    _CACHE[original] = translated
        except Exception as e:
            logger.exception("Erro na tradução em lote: %s", e)
            for i, t in to_translate:
                results[i] = t.upper()

        return [r or "" for r in results]


# Singleton
translator = Translator()
