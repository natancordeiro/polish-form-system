import { FieldGroup } from '../FormFields.jsx';
import { PersonFields } from '../PersonFields.jsx';

export function StepAvos({ register, errors }) {
  return (
    <div className="space-y-10">
      <p className="text-sm text-stone-600 bg-stone-100 border border-stone-200 rounded-md p-3">
        Para os avós, informe apenas os dados essenciais. Se você não souber algum dado,
        marque "desconhecido" na caixa correspondente — o PDF será preenchido com <strong>NIEZNANE</strong>.
      </p>

      <FieldGroup title="Avô materno">
        <PersonFields
          register={register}
          errors={errors}
          prefix="avo_materno"
          variant="simple"
        />
      </FieldGroup>

      <div className="border-t border-stone-200 pt-10">
        <FieldGroup title="Avó materna">
          <PersonFields
            register={register}
            errors={errors}
            prefix="avo_materna"
            variant="simple"
          />
        </FieldGroup>
      </div>

      <div className="border-t border-stone-200 pt-10">
        <FieldGroup title="Avô paterno">
          <PersonFields
            register={register}
            errors={errors}
            prefix="avo_paterno"
            variant="simple"
          />
        </FieldGroup>
      </div>

      <div className="border-t border-stone-200 pt-10">
        <FieldGroup title="Avó paterna">
          <PersonFields
            register={register}
            errors={errors}
            prefix="avo_paterna"
            variant="simple"
          />
        </FieldGroup>
      </div>
    </div>
  );
}
