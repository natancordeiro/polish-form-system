/**
 * Cliente da API FastAPI.
 *
 * Converte o payload do formulário (strings vazias) para o formato
 * esperado pelo Pydantic (null em vez de string vazia nos campos opcionais).
 */

// Em dev, o Vite faz proxy /api -> :8000. Em build, definimos no build-time.
const API_BASE = import.meta.env.VITE_API_BASE || '';

/** Converte "" em null recursivamente (Pydantic espera null em Optional). */
function sanitize(value) {
  if (value === '' || value === undefined) return null;
  if (Array.isArray(value)) {
    return value.map(sanitize).filter(v => v !== null && v !== '');
  }
  if (value !== null && typeof value === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(value)) {
      out[k] = sanitize(v);
    }
    return out;
  }
  return value;
}

/** Prepara o payload, lida com campos obrigatórios que não podem virar null. */
function toPayload(formData) {
  const payload = sanitize(formData);

  // Filtra anexos vazios
  if (Array.isArray(formData.anexos)) {
    payload.anexos = formData.anexos.filter(a => a && a.trim());
  } else {
    payload.anexos = [];
  }

  return payload;
}

/** Health check — útil no boot da app. */
export async function healthCheck() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Health check falhou:', err);
    return null;
  }
}

/**
 * Envia o formulário e dispara o download do PDF gerado.
 * Lança Error em caso de falha.
 */
export async function generatePdf(formData) {
  const payload = toPayload(formData);

  const res = await fetch(`${API_BASE}/api/generate-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      detail = err.detail || detail;
    } catch {}
    throw new Error(`Falha ao gerar o PDF: ${detail}`);
  }

  const blob = await res.blob();

  // Extrai filename do Content-Disposition, se presente
  const cd = res.headers.get('Content-Disposition') || '';
  const match = cd.match(/filename="?([^"]+)"?/);
  const filename = match ? match[1] : `Wniosek_${Date.now()}.pdf`;

  // Dispara download
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);

  return { filename };
}
