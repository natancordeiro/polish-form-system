import { z } from 'zod';

/**
 * Schema de validação que espelha o Pydantic do backend.
 * Os campos opcionais são representados como strings vazias na UI
 * e convertidos para `null` no envio (ver toPayload em api.js).
 */

// Regex simples para data ISO (YYYY-MM-DD)
const isoDate = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Data inválida').or(z.literal(''));

export const enderecoSchema = z.object({
  pais: z.string().min(1, 'Obrigatório'),
  estado: z.string().optional().default(''),
  cidade: z.string().min(1, 'Obrigatório'),
  rua: z.string().min(1, 'Obrigatório'),
  numero_casa: z.string().min(1, 'Obrigatório'),
  numero_apartamento: z.string().optional().default(''),
  cep: z.string().min(1, 'Obrigatório'),
  telefone: z.string().optional().default(''),
});

export const dadosPessoaisSchema = z.object({
  sobrenome: z.string().min(1, 'Obrigatório'),
  sobrenome_solteiro: z.string().optional().default(''),
  nome: z.string().min(1, 'Obrigatório'),
  nome_pai: z.string().optional().default(''),
  sobrenome_pai: z.string().optional().default(''),
  nome_mae: z.string().optional().default(''),
  sobrenome_solteiro_mae: z.string().optional().default(''),
  nomes_usados: z.string().optional().default(''),
  data_mudanca_nome: isoDate.optional().default(''),
  data_nascimento: isoDate.optional().default(''),
  data_nascimento_desconhecida: z.boolean().optional().default(false),
  sexo: z.enum(['M', 'F']).optional().or(z.literal('')),
  pais_nascimento: z.string().optional().default(''),
  cidade_nascimento: z.string().optional().default(''),
  cidade_nascimento_desconhecida: z.boolean().optional().default(false),
  cidadania: z.string().optional().default(''),
  data_aquisicao_cidadania: z.string().optional().default(''),
  estado_civil: z.enum([
    'solteiro', 'casado', 'casada',
    'divorciado', 'divorciada',
    'viuvo', 'viuva', 'uniao_estavel',
  ]).optional().or(z.literal('')),
  pesel: z.string().optional().default(''),
});

export const progenitorSchema = dadosPessoaisSchema.extend({
  data_casamento: isoDate.optional().default(''),
  pais_casamento: z.string().optional().default(''),
  cidade_casamento: z.string().optional().default(''),
});

export const formSchema = z.object({
  // Cabeçalho
  local_submissao: z.string().min(1, 'Obrigatório'),
  data_submissao: isoDate.refine(v => v.length > 0, 'Obrigatório'),
  wojewoda: z.string().min(1, 'Obrigatório'),

  // Requerente
  requerente_nome_completo: z.string().min(1, 'Obrigatório'),
  requerente_endereco: enderecoSchema,

  // Tipo
  tipo_decisao: z.enum(['posiadanie', 'utrata']),
  nome_titular_confirmacao: z.string().min(1, 'Obrigatório'),
  info_adicional_pedido: z.string().min(1, 'Obrigatório'),
  justificativa_procuracao: z.string().optional().default(''),

  // Solicitante
  solicitante: dadosPessoaisSchema,

  // B, C, D
  houve_decisao_anterior: z.boolean().default(false),
  detalhes_decisao_anterior: z.string().optional().default(''),
  houve_mudanca_cidadania: z.boolean().default(false),
  detalhes_mudanca_cidadania: z.string().optional().default(''),
  enderecos_vida: z.string().min(1, 'Obrigatório'),

  // Pais
  mae: progenitorSchema,
  pai: progenitorSchema,

  // Avós
  avo_materno: dadosPessoaisSchema,
  avo_materna: dadosPessoaisSchema,
  avo_paterno: dadosPessoaisSchema,
  avo_paterna: dadosPessoaisSchema,

  // Biografias
  biografia_solicitante: z.string().min(1, 'Obrigatório'),
  escolheu_cidadania_estrangeira: z.enum(['TAK', 'NIE', 'NIE_WIEM', 'NIE_DOTYCZY']).default('NIE'),
  orgao_escolha_cidadania: z.string().optional().default(''),

  biografia_mae: z.string().optional().default(''),
  biografia_pai: z.string().optional().default(''),
  biografia_avo_materno: z.string().optional().default(''),
  biografia_avo_materna: z.string().optional().default(''),
  biografia_avo_paterno: z.string().optional().default(''),
  biografia_avo_paterna: z.string().optional().default(''),
  biografia_ancestral_polones: z.string().optional().default(''),

  // Info adicional
  decisao_sobre_parentes: z.string().optional().default(''),
  docs_poloneses_ancestrais: z.string().optional().default(''),
  renuncia_cidadania_ancestrais: z.string().optional().default(''),
  outras_informacoes: z.string().optional().default(''),

  // Anexos
  anexos: z.array(z.string()).default([]),
});

/** Valores iniciais vazios para popular o useForm. */
export const emptyFormValues = {
  local_submissao: 'Warszawa',
  data_submissao: new Date().toISOString().slice(0, 10),
  wojewoda: 'Mazowiecki',

  requerente_nome_completo: '',
  requerente_endereco: {
    pais: '', estado: '', cidade: '', rua: '',
    numero_casa: '', numero_apartamento: '', cep: '', telefone: '',
  },

  tipo_decisao: 'posiadanie',
  nome_titular_confirmacao: '',
  info_adicional_pedido: '',
  justificativa_procuracao: '',

  solicitante: emptyPessoa(),

  houve_decisao_anterior: false,
  detalhes_decisao_anterior: '',
  houve_mudanca_cidadania: false,
  detalhes_mudanca_cidadania: '',
  enderecos_vida: '',

  mae: emptyProgenitor(),
  pai: emptyProgenitor(),
  avo_materno: emptyPessoa(),
  avo_materna: emptyPessoa(),
  avo_paterno: emptyPessoa(),
  avo_paterna: emptyPessoa(),

  biografia_solicitante: '',
  escolheu_cidadania_estrangeira: 'NIE',
  orgao_escolha_cidadania: '',

  biografia_mae: '',
  biografia_pai: '',
  biografia_avo_materno: '',
  biografia_avo_materna: '',
  biografia_avo_paterno: '',
  biografia_avo_paterna: '',
  biografia_ancestral_polones: '',

  decisao_sobre_parentes: '',
  docs_poloneses_ancestrais: '',
  renuncia_cidadania_ancestrais: '',
  outras_informacoes: '',

  anexos: [''],
};

function emptyPessoa() {
  return {
    sobrenome: '', sobrenome_solteiro: '', nome: '',
    nome_pai: '', sobrenome_pai: '', nome_mae: '', sobrenome_solteiro_mae: '',
    nomes_usados: '', data_mudanca_nome: '',
    data_nascimento: '', data_nascimento_desconhecida: false,
    sexo: '', pais_nascimento: '', cidade_nascimento: '',
    cidade_nascimento_desconhecida: false,
    cidadania: '', data_aquisicao_cidadania: '',
    estado_civil: '', pesel: '',
  };
}

function emptyProgenitor() {
  return {
    ...emptyPessoa(),
    data_casamento: '', pais_casamento: '', cidade_casamento: '',
  };
}
