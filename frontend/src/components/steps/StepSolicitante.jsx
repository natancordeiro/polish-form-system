import { useWatch } from 'react-hook-form';
import { Textarea, Checkbox, FieldGroup } from '../FormFields.jsx';
import { PersonFields } from '../PersonFields.jsx';

export function StepSolicitante({ register, errors, control }) {
  const houveDecisao = useWatch({ control, name: 'houve_decisao_anterior' });
  const houveMudanca = useWatch({ control, name: 'houve_mudanca_cidadania' });

  return (
    <div className="space-y-10">
      <FieldGroup
        title="Dados pessoais do beneficiado"
        description="Pessoa cuja cidadania polonesa está sendo confirmada."
      >
        <PersonFields
          register={register}
          errors={errors}
          prefix="solicitante"
          variant="full"
        />
      </FieldGroup>

      <FieldGroup
        title="Decisões anteriores sobre cidadania (Seção B)"
      >
        <Checkbox
          label="Já existiu decisão sobre a cidadania polonesa desta pessoa?"
          {...register('houve_decisao_anterior')}
        />
        {houveDecisao && (
          <Textarea
            label="Detalhes da decisão anterior"
            rows={3}
            help="Qual órgão, quando foi emitida e qual o teor da decisão"
            {...register('detalhes_decisao_anterior')}
          />
        )}
      </FieldGroup>

      <FieldGroup
        title="Mudança ou perda de cidadania (Seção C)"
      >
        <Checkbox
          label="A pessoa já pediu autorização para mudar ou renunciar à cidadania polonesa?"
          {...register('houve_mudanca_cidadania')}
        />
        {houveMudanca && (
          <Textarea
            label="Detalhes"
            rows={3}
            {...register('detalhes_mudanca_cidadania')}
          />
        )}
      </FieldGroup>

      <FieldGroup
        title="Locais de residência ao longo da vida (Seção D)"
        description="Endereços em que a pessoa morou, na Polônia ou no exterior."
      >
        <Textarea
          label="Endereços"
          required
          rows={4}
          error={errors?.enderecos_vida?.message}
          help="Você pode listar múltiplos endereços, um por linha"
          {...register('enderecos_vida')}
        />
      </FieldGroup>
    </div>
  );
}
