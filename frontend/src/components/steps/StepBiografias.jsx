import { useWatch } from 'react-hook-form';
import { Textarea, Select, Input, FieldGroup } from '../FormFields.jsx';

export function StepBiografias({ register, errors, control }) {
  const escolha = useWatch({ control, name: 'escolheu_cidadania_estrangeira' });

  return (
    <div className="space-y-10">
      <div className="rounded-md bg-amber-50 border border-amber-200 p-4 text-sm text-amber-900">
        <strong>Importante:</strong> as biografias serão traduzidas automaticamente do português para o polonês
        via DeepL. Escreva em PT-BR de forma clara, usando parágrafos curtos e dados objetivos
        (datas, lugares, profissões).
      </div>

      <FieldGroup
        title="Biografia do beneficiado (Parte II.A)"
        description="Obrigatório. Cobrir nascimento, educação, trabalho, serviço militar, casamentos, mudanças de nome, cidadanias e documentos."
      >
        <Textarea
          label="Biografia completa"
          required
          rows={10}
          error={errors?.biografia_solicitante?.message}
          {...register('biografia_solicitante')}
        />
      </FieldGroup>

      <FieldGroup
        title="Escolha de cidadania estrangeira (Parte II.B)"
        description="Pais escolheram cidadania estrangeira para o filho nascido entre 22/08/1962 e 15/08/2012?"
      >
        <Select label="Resposta" {...register('escolheu_cidadania_estrangeira')}>
          <option value="NIE">Não</option>
          <option value="TAK">Sim</option>
          <option value="NIE_WIEM">Não sei</option>
          <option value="NIE_DOTYCZY">Não se aplica</option>
        </Select>
        {escolha === 'TAK' && (
          <Input
            label="Órgão perante o qual foi feita a escolha"
            {...register('orgao_escolha_cidadania')}
          />
        )}
      </FieldGroup>

      <FieldGroup
        title="Biografias dos pais (Parte III.A)"
        description="Opcional se você anexar passaporte/documento polonês dos pais."
      >
        <Textarea
          label="Biografia da mãe"
          rows={6}
          {...register('biografia_mae')}
        />
        <Textarea
          label="Biografia do pai"
          rows={6}
          {...register('biografia_pai')}
        />
      </FieldGroup>

      <FieldGroup
        title="Biografias dos avós (Parte III.B)"
      >
        <Textarea label="Biografia do avô materno" rows={5} {...register('biografia_avo_materno')} />
        <Textarea label="Biografia da avó materna" rows={5} {...register('biografia_avo_materna')} />
        <Textarea label="Biografia do avô paterno" rows={5} {...register('biografia_avo_paterno')} />
        <Textarea label="Biografia da avó paterna" rows={5} {...register('biografia_avo_paterna')} />
      </FieldGroup>

      <FieldGroup
        title="Ancestral polonês (Parte III.C)"
        description="Biografia do ancestral que gera o direito à cidadania — obrigatório se você estiver reivindicando via bisavô, avô, etc."
      >
        <Textarea
          label="Biografia do ancestral polonês"
          rows={10}
          help="Nascimento, pais, saída da Polônia, jornada, trabalho, casamento, falecimento"
          {...register('biografia_ancestral_polones')}
        />
      </FieldGroup>
    </div>
  );
}
