import { Input, Select, Checkbox, FieldGroup } from './FormFields.jsx';

/**
 * Renderiza o bloco de campos de uma pessoa.
 * `prefix` define o path no objeto (ex: "solicitante", "mae", "avo_materno").
 * `variant` controla quais campos aparecem:
 *   - 'full'        -> todos os campos (solicitante)
 *   - 'progenitor'  -> todos + casamento (pais)
 *   - 'simple'      -> apenas dados essenciais (avós)
 */
export function PersonFields({ register, errors, prefix, variant = 'full' }) {
  const err = (field) => errors?.[prefix]?.[field]?.message;
  const reg = (field) => register(`${prefix}.${field}`);

  return (
    <div className="space-y-6">
      <FieldGroup title="Nome">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input label="Nome (próprio)" required error={err('nome')} {...reg('nome')} />
          <Input label="Sobrenome" required error={err('sobrenome')} {...reg('sobrenome')} />
          <Input label="Sobrenome de solteiro(a)" help="Se não houve mudança, repita o sobrenome" error={err('sobrenome_solteiro')} {...reg('sobrenome_solteiro')} />
          {variant === 'full' && (
            <Input label="Nomes anteriormente usados" help="Deixe vazio se não se aplica" {...reg('nomes_usados')} />
          )}
        </div>
      </FieldGroup>

      <FieldGroup title="Filiação">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input label="Nome do pai" {...reg('nome_pai')} />
          <Input label="Sobrenome do pai" {...reg('sobrenome_pai')} />
          <Input label="Nome da mãe" {...reg('nome_mae')} />
          <Input label="Sobrenome de solteira da mãe" {...reg('sobrenome_solteiro_mae')} />
        </div>
      </FieldGroup>

      <FieldGroup title="Nascimento">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Input
              type="date"
              label="Data de nascimento"
              {...reg('data_nascimento')}
            />
            <Checkbox
              label="Data desconhecida"
              className="mt-2"
              {...reg('data_nascimento_desconhecida')}
            />
          </div>
          <Select label="Sexo" {...reg('sexo')}>
            <option value="">Selecione…</option>
            <option value="M">Masculino</option>
            <option value="F">Feminino</option>
          </Select>
          <Input label="País de nascimento" {...reg('pais_nascimento')} />
          <div>
            <Input
              label="Cidade de nascimento"
              {...reg('cidade_nascimento')}
            />
            <Checkbox
              label="Cidade desconhecida"
              className="mt-2"
              {...reg('cidade_nascimento_desconhecida')}
            />
          </div>
        </div>
      </FieldGroup>

      {variant !== 'simple' && (
        <>
          <FieldGroup title="Cidadania">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Cidadania(s)"
                help="Ex: Brasileira, Polonesa"
                {...reg('cidadania')}
              />
              <Input
                label="Data de aquisição"
                help='Ex: "desde o nascimento" ou "12/05/1985"'
                {...reg('data_aquisicao_cidadania')}
              />
            </div>
          </FieldGroup>

          <FieldGroup title="Estado civil e PESEL">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Select label="Estado civil" {...reg('estado_civil')}>
                <option value="">Selecione…</option>
                <option value="solteiro">Solteiro(a)</option>
                <option value="casado">Casado(a)</option>
                <option value="divorciado">Divorciado(a)</option>
                <option value="viuvo">Viúvo(a)</option>
                <option value="uniao_estavel">União estável</option>
              </Select>
              <Input
                label="Nº PESEL"
                help="Deixe vazio se não possui"
                {...reg('pesel')}
              />
            </div>
          </FieldGroup>
        </>
      )}

      {variant === 'progenitor' && (
        <FieldGroup title="Casamento">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              type="date"
              label="Data do casamento"
              {...reg('data_casamento')}
            />
            <Input label="País do casamento" {...reg('pais_casamento')} />
            <Input label="Cidade do casamento" {...reg('cidade_casamento')} />
          </div>
        </FieldGroup>
      )}
    </div>
  );
}
