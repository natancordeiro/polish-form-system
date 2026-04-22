import { useFieldArray } from 'react-hook-form';
import { Textarea, Input, FieldGroup } from '../FormFields.jsx';
import { Plus, Trash2 } from 'lucide-react';

export function StepInfoEAnexos({ register, errors, control }) {
  const { fields, append, remove } = useFieldArray({ control, name: 'anexos' });

  return (
    <div className="space-y-10">
      <FieldGroup
        title="Informações adicionais (Parte III.D)"
        description="Detalhes sobre irmãos, ascendentes e documentos poloneses da família."
      >
        <Textarea
          label="Decisões sobre parentes (irmãos, pais, avós)"
          rows={3}
          help="Houve decisão sobre cidadania polonesa envolvendo parentes? Processos em andamento?"
          {...register('decisao_sobre_parentes')}
        />
        <Textarea
          label="Documentos poloneses de ascendentes"
          rows={3}
          help="Ascendentes possuem/possuíam documentos poloneses? Quais, por quem e quando emitidos?"
          {...register('docs_poloneses_ancestrais')}
        />
        <Textarea
          label="Renúncia de cidadania por ascendentes"
          rows={3}
          help="Algum ascendente pediu mudança ou renúncia à cidadania polonesa?"
          {...register('renuncia_cidadania_ancestrais')}
        />
      </FieldGroup>

      <FieldGroup
        title="Parte IV — Outras informações"
        description="Qualquer outra informação que o requerente considere relevante."
      >
        <Textarea
          label="Outras informações"
          rows={4}
          {...register('outras_informacoes')}
        />
      </FieldGroup>

      <FieldGroup
        title="Anexos"
        description="Lista dos documentos que acompanham o requerimento."
      >
        <div className="space-y-3">
          {fields.map((field, idx) => (
            <div key={field.id} className="flex gap-2 items-start">
              <div className="pt-2 text-sm text-stone-500 font-medium w-6">
                {idx + 1}.
              </div>
              <Input
                placeholder="Descrição do anexo"
                className="flex-1"
                {...register(`anexos.${idx}`)}
              />
              <button
                type="button"
                onClick={() => remove(idx)}
                className="p-2 text-stone-400 hover:text-red-600 transition-colors"
                title="Remover"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
        <button
          type="button"
          onClick={() => append('')}
          className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-stone-700 hover:text-stone-900"
        >
          <Plus className="w-4 h-4" />
          Adicionar anexo
        </button>
      </FieldGroup>
    </div>
  );
}
