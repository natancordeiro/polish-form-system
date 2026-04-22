"""
Mapeamento PT→PL de valores FECHADOS (enums, opções de dropdown).

Esses valores NUNCA devem ir para o DeepL — tradução manual garante
que os termos oficiais poloneses sejam usados corretamente.
"""

# ---------------------------------------------------------------------------
# Estado civil — depende do sexo para alguns casos
# ---------------------------------------------------------------------------
# No formulário polonês:
#   - MĘŻATKA  (mulher casada)
#   - ŻONATY   (homem casado)
#   - KAWALER  (homem solteiro)
#   - PANNA    (mulher solteira)
#   - ROZWIEDZIONY / ROZWIEDZIONA
#   - WDOWIEC / WDOWA

ESTADO_CIVIL_MAP = {
    ("solteiro", "M"): "KAWALER",
    ("solteiro", "F"): "PANNA",
    ("casado",   "M"): "ŻONATY",
    ("casado",   "F"): "MĘŻATKA",
    ("casada",   "F"): "MĘŻATKA",
    ("casada",   "M"): "ŻONATY",
    ("divorciado", "M"): "ROZWIEDZIONY",
    ("divorciado", "F"): "ROZWIEDZIONA",
    ("divorciada", "F"): "ROZWIEDZIONA",
    ("divorciada", "M"): "ROZWIEDZIONY",
    ("viuvo", "M"): "WDOWIEC",
    ("viuvo", "F"): "WDOWA",
    ("viuva", "F"): "WDOWA",
    ("viuva", "M"): "WDOWIEC",
    # União estável não tem equivalente exato em formulário oficial
    ("uniao_estavel", "M"): "KAWALER",
    ("uniao_estavel", "F"): "PANNA",
}


def traduzir_estado_civil(estado_civil: str | None, sexo: str | None) -> str:
    if not estado_civil:
        return ""
    if not sexo:
        sexo = "M"  # fallback
    return ESTADO_CIVIL_MAP.get((estado_civil.lower(), sexo.upper()), estado_civil.upper())


# ---------------------------------------------------------------------------
# Sexo
# ---------------------------------------------------------------------------
SEXO_MAP = {"M": "M", "F": "K"}  # K = kobieta em polonês


def traduzir_sexo(sexo: str | None) -> str:
    if not sexo:
        return ""
    return SEXO_MAP.get(sexo.upper(), sexo.upper())


# ---------------------------------------------------------------------------
# Países (mais comuns) — expandir conforme necessário
# ---------------------------------------------------------------------------
PAIS_MAP = {
    "brasil":       "BRAZYLIA",
    "brazil":       "BRAZYLIA",
    "polônia":      "POLSKA",
    "polonia":      "POLSKA",
    "poland":       "POLSKA",
    "argentina":    "ARGENTYNA",
    "portugal":     "PORTUGALIA",
    "italia":       "WŁOCHY",
    "itália":       "WŁOCHY",
    "italy":        "WŁOCHY",
    "espanha":      "HISZPANIA",
    "spain":        "HISZPANIA",
    "alemanha":     "NIEMCY",
    "germany":      "NIEMCY",
    "estados unidos": "STANY ZJEDNOCZONE",
    "eua":          "STANY ZJEDNOCZONE",
    "usa":          "STANY ZJEDNOCZONE",
    "frança":       "FRANCJA",
    "franca":       "FRANCJA",
    "france":       "FRANCJA",
    "reino unido":  "WIELKA BRYTANIA",
    "inglaterra":   "WIELKA BRYTANIA",
    "uk":           "WIELKA BRYTANIA",
    "ucrânia":      "UKRAINA",
    "ucrania":      "UKRAINA",
    "rússia":       "ROSJA",
    "russia":       "ROSJA",
    "israel":       "IZRAEL",
    "canadá":       "KANADA",
    "canada":       "KANADA",
    "austrália":    "AUSTRALIA",
    "australia":    "AUSTRALIA",
    "uruguai":      "URUGWAJ",
    "paraguai":     "PARAGWAJ",
    "chile":        "CHILE",
    "méxico":       "MEKSYK",
    "mexico":       "MEKSYK",
}


def traduzir_pais(pais: str | None) -> str:
    if not pais:
        return ""
    key = pais.strip().lower()
    return PAIS_MAP.get(key, pais.upper())


# ---------------------------------------------------------------------------
# Voivodias polonesas (województwa) — para o campo "estado" quando em Polônia
# ---------------------------------------------------------------------------
WOJEWODZTWA = [
    "DOLNOŚLĄSKIE", "KUJAWSKO-POMORSKIE", "LUBELSKIE", "LUBUSKIE",
    "ŁÓDZKIE", "MAŁOPOLSKIE", "MAZOWIECKIE", "OPOLSKIE",
    "PODKARPACKIE", "PODLASKIE", "POMORSKIE", "ŚLĄSKIE",
    "ŚWIĘTOKRZYSKIE", "WARMIŃSKO-MAZURSKIE", "WIELKOPOLSKIE",
    "ZACHODNIOPOMORSKIE",
]


# ---------------------------------------------------------------------------
# Respostas de checkbox TAK/NIE/NIE WIEM/NIE DOTYCZY
# ---------------------------------------------------------------------------
RESPOSTA_MAP = {
    "TAK":         "TAK",
    "NIE":         "NIE",
    "NIE_WIEM":    "NIE WIEM",
    "NIE_DOTYCZY": "NIE DOTYCZY",
}


def traduzir_resposta(r: str | None) -> str:
    if not r:
        return "NIE"
    return RESPOSTA_MAP.get(r.upper(), r.upper())


# ---------------------------------------------------------------------------
# Valores padrão quando o usuário não informa
# ---------------------------------------------------------------------------
NIE_DOTYCZY = "NIE DOTYCZY"      # Não se aplica
NIEZNANE = "NIEZNANE"             # Desconhecido
BRAK_DANYCH = "BRAK DANYCH"       # Sem dados


# ---------------------------------------------------------------------------
# Formatação de data para o padrão polonês (rok/miesiąc/dzień = YYYY/MM/DD)
# ---------------------------------------------------------------------------
def formatar_data_pl(d) -> str:
    """Formata uma date Python como 'YYYY/MM/DD' (padrão do formulário)."""
    if d is None:
        return ""
    return d.strftime("%Y/%m/%d")


def formatar_data_boletim_pl(d) -> str:
    """Formata uma date como '08.12.1949 R.' — usado nas biografias."""
    if d is None:
        return ""
    return d.strftime("%d.%m.%Y R.")
