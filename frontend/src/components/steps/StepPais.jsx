import { FieldGroup } from '../FormFields.jsx';
import { PersonFields } from '../PersonFields.jsx';

export function StepPais({ register, errors }) {
  return (
    <div className="space-y-10">
      <FieldGroup
        title="Dados da mãe"
        description="Dados da mãe do beneficiado, incluindo data e local do casamento."
      >
        <PersonFields
          register={register}
          errors={errors}
          prefix="mae"
          variant="progenitor"
        />
      </FieldGroup>

      <div className="border-t border-stone-200 pt-10">
        <FieldGroup
          title="Dados do pai"
          description="Dados do pai do beneficiado, incluindo data e local do casamento."
        >
          <PersonFields
            register={register}
            errors={errors}
            prefix="pai"
            variant="progenitor"
          />
        </FieldGroup>
      </div>
    </div>
  );
}
