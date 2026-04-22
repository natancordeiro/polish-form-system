"""
Pydantic schemas que modelam o formulário oficial polonês
'Wniosek o potwierdzenie posiadania lub utraty obywatelstwa polskiego'.

Os nomes dos campos estão em português (conforme preenchimento do usuário),
e o mapeamento PT→PL é feito no momento da geração do PDF.
"""
from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums como Literal
# ---------------------------------------------------------------------------

Sexo = Literal["M", "F"]

EstadoCivil = Literal[
    "solteiro",
    "casado",
    "casada",
    "divorciado",
    "divorciada",
    "viuvo",
    "viuva",
    "uniao_estavel",
]

TipoDecisao = Literal["posiadanie", "utrata"]  # confirma posse ou perda

RespostaSimNao = Literal["TAK", "NIE", "NIE_WIEM", "NIE_DOTYCZY"]


# ---------------------------------------------------------------------------
# Blocos reutilizáveis
# ---------------------------------------------------------------------------

class Endereco(BaseModel):
    """Endereço atual do requerente ou do solicitante."""
    pais: str = Field(..., description="País")
    estado: Optional[str] = Field(None, description="Estado/Voivodia")
    cidade: str
    rua: str
    numero_casa: str
    numero_apartamento: Optional[str] = None
    cep: str
    telefone: Optional[str] = None


class DadosPessoais(BaseModel):
    """Dados pessoais básicos (usado em várias seções)."""
    sobrenome: str
    sobrenome_solteiro: Optional[str] = None
    nome: str  # pode ser composto
    nome_pai: Optional[str] = None
    sobrenome_pai: Optional[str] = None
    nome_mae: Optional[str] = None
    sobrenome_solteiro_mae: Optional[str] = None
    nomes_usados: Optional[str] = Field(
        None, description="Nomes anteriormente usados (com data de mudança). Deixe vazio se não se aplica."
    )
    data_mudanca_nome: Optional[date] = None
    data_nascimento: Optional[date] = None
    data_nascimento_desconhecida: bool = False
    sexo: Optional[Sexo] = None
    pais_nascimento: Optional[str] = None
    cidade_nascimento: Optional[str] = None
    cidade_nascimento_desconhecida: bool = False
    cidadania: Optional[str] = Field(None, description="Cidadania(s) que possui")
    data_aquisicao_cidadania: Optional[str] = Field(
        None,
        description="Data de aquisição da cidadania ou 'DESDE O NASCIMENTO'",
    )
    estado_civil: Optional[EstadoCivil] = None
    pesel: Optional[str] = None


class DadosProgenitor(DadosPessoais):
    """Dados dos pais — inclui dados de casamento."""
    data_casamento: Optional[date] = None
    pais_casamento: Optional[str] = None
    cidade_casamento: Optional[str] = None


# ---------------------------------------------------------------------------
# Formulário completo
# ---------------------------------------------------------------------------

class FormData(BaseModel):
    """Modelo raiz que representa todo o formulário."""

    # ---- Cabeçalho ----
    local_submissao: str = Field(..., description="Ex: WARSZAWA")
    data_submissao: date
    wojewoda: str = Field(..., description="Voivoda destinatário. Ex: MAZOWIECKI")

    # ---- Requerente (procurador / advogado / empresa) ----
    requerente_nome_completo: str
    requerente_endereco: Endereco

    # ---- Tipo de pedido ----
    tipo_decisao: TipoDecisao
    nome_titular_confirmacao: str = Field(
        ...,
        description="Nome da pessoa cuja cidadania está sendo confirmada/perdida",
    )
    info_adicional_pedido: str = Field(
        ...,
        description="Contexto sobre o direito à cidadania (ex: via pai/avô)",
    )
    justificativa_procuracao: Optional[str] = Field(
        None,
        description="Se o pedido é para terceiro, descrever a relação de procuração",
    )

    # ---- CZĘŚĆ I — A. Dados do solicitante ----
    solicitante: DadosPessoais

    # ---- CZĘŚĆ I — B. Decisões anteriores sobre cidadania ----
    houve_decisao_anterior: bool = False
    detalhes_decisao_anterior: Optional[str] = None

    # ---- CZĘŚĆ I — C. Mudança/perda de cidadania polonesa ----
    houve_mudanca_cidadania: bool = False
    detalhes_mudanca_cidadania: Optional[str] = None

    # ---- CZĘŚĆ I — D. Locais de residência na vida ----
    enderecos_vida: str = Field(
        ...,
        description="Texto livre listando locais onde a pessoa viveu",
    )

    # ---- CZĘŚĆ I — E. Dados dos pais ----
    mae: DadosProgenitor
    pai: DadosProgenitor

    # ---- CZĘŚĆ I — F. Dados dos avós ----
    avo_materno: DadosPessoais
    avo_materna: DadosPessoais
    avo_paterno: DadosPessoais
    avo_paterna: DadosPessoais

    # ---- CZĘŚĆ II — A. Biografia do solicitante ----
    biografia_solicitante: str

    # ---- CZĘŚĆ II — B. Escolha de cidadania estrangeira para filho ----
    escolheu_cidadania_estrangeira: RespostaSimNao = "NIE"
    orgao_escolha_cidadania: Optional[str] = None

    # ---- CZĘŚĆ III — A. Biografias dos pais ----
    biografia_mae: Optional[str] = None
    biografia_pai: Optional[str] = None

    # ---- CZĘŚĆ III — B. Biografias dos avós ----
    biografia_avo_materno: Optional[str] = None
    biografia_avo_materna: Optional[str] = None
    biografia_avo_paterno: Optional[str] = None
    biografia_avo_paterna: Optional[str] = None

    # ---- CZĘŚĆ III — C. Informações sobre ascendentes mais distantes (bisavós) ----
    biografia_ancestral_polones: Optional[str] = Field(
        None,
        description="Biografia do ancestral polonês que gera o direito (ex: bisavô imigrante)",
    )

    # ---- CZĘŚĆ III — D. Informações adicionais ----
    decisao_sobre_parentes: Optional[str] = Field(
        None,
        description="Houve decisão sobre cidadania polonesa a irmãos ou ascendentes?",
    )
    docs_poloneses_ancestrais: Optional[str] = Field(
        None,
        description="Algum ascendente possui/possuía documento polonês?",
    )
    renuncia_cidadania_ancestrais: Optional[str] = Field(
        None,
        description="Algum ascendente pediu mudança/renúncia à cidadania polonesa?",
    )

    # ---- CZĘŚĆ IV — Outras informações ----
    outras_informacoes: Optional[str] = None

    # ---- Anexos ----
    anexos: list[str] = Field(
        default_factory=list,
        description="Lista de anexos que acompanham o requerimento",
    )


# ---------------------------------------------------------------------------
# Resposta da API
# ---------------------------------------------------------------------------

class GenerateResponse(BaseModel):
    """Resposta do endpoint de geração do PDF."""
    success: bool
    message: str
    filename: str
