import { Input, Textarea, Select, FieldGroup } from '../FormFields.jsx';

const VOIVODIAS = [
  'Dolnośląskie', 'Kujawsko-pomorskie', 'Lubelskie', 'Lubuskie',
  'Łódzkie', 'Małopolskie', 'Mazowieckie', 'Opolskie',
  'Podkarpackie', 'Podlaskie', 'Pomorskie', 'Śląskie',
  'Świętokrzyskie', 'Warmińsko-mazurskie', 'Wielkopolskie',
  'Zachodniopomorskie',
];

export function StepCabecalho({ register, errors }) {
  const reg = (f) => register(f);
  const err = (f) => errors?.[f]?.message;

  return (
    <div className="space-y-8">
      <FieldGroup
        title="Dados do pedido"
        description="Informações que aparecem no cabeçalho do requerimento oficial."
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label="Local de submissão"
            required
            help="Cidade onde o pedido é entregue"
            error={err('local_submissao')}
            {...reg('local_submissao')}
          />
          <Input
            type="date"
            label="Data de submissão"
            required
            error={err('data_submissao')}
            {...reg('data_submissao')}
          />
          <Select
            label="Voivoda destinatário"
            required
            help="Não-residentes → Mazowiecki"
            error={err('wojewoda')}
            {...reg('wojewoda')}
          >
            {VOIVODIAS.map(v => (
              <option key={v} value={v}>{v}</option>
            ))}
          </Select>
        </div>
      </FieldGroup>

      <FieldGroup
        title="Requerente (quem protocola o pedido)"
        description="Pode ser o próprio interessado, um procurador ou empresa."
      >
        <Input
          label="Nome completo / Razão social"
          required
          error={err('requerente_nome_completo')}
          {...reg('requerente_nome_completo')}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="País"
            required
            error={errors?.requerente_endereco?.pais?.message}
            {...register('requerente_endereco.pais')}
          />
          <Input
            label="Estado / Voivodia"
            {...register('requerente_endereco.estado')}
          />
          <Input
            label="Cidade"
            required
            error={errors?.requerente_endereco?.cidade?.message}
            {...register('requerente_endereco.cidade')}
          />
          <Input
            label="Rua"
            required
            error={errors?.requerente_endereco?.rua?.message}
            {...register('requerente_endereco.rua')}
          />
          <Input
            label="Número"
            required
            error={errors?.requerente_endereco?.numero_casa?.message}
            {...register('requerente_endereco.numero_casa')}
          />
          <Input
            label="Apartamento"
            {...register('requerente_endereco.numero_apartamento')}
          />
          <Input
            label="CEP"
            required
            error={errors?.requerente_endereco?.cep?.message}
            {...register('requerente_endereco.cep')}
          />
          <Input
            label="Telefone de contato"
            {...register('requerente_endereco.telefone')}
          />
        </div>
      </FieldGroup>

      <FieldGroup
        title="Tipo de decisão solicitada"
        description="Confirmação de posse ou de perda da cidadania polonesa."
      >
        <Select
          label="Tipo"
          required
          error={err('tipo_decisao')}
          {...reg('tipo_decisao')}
        >
          <option value="posiadanie">Confirmação de POSSE da cidadania</option>
          <option value="utrata">Confirmação de PERDA da cidadania</option>
        </Select>

        <Input
          label="Nome completo da pessoa beneficiada"
          required
          help="Pessoa cuja cidadania está sendo confirmada/perdida"
          error={err('nome_titular_confirmacao')}
          {...reg('nome_titular_confirmacao')}
        />

        <Textarea
          label="Informações adicionais sobre o pedido"
          required
          rows={4}
          help="Contexto do direito à cidadania — ex: via pai, via avô, com datas e lugares"
          error={err('info_adicional_pedido')}
          {...reg('info_adicional_pedido')}
        />

        <Textarea
          label="Justificativa da procuração (se aplicável)"
          rows={3}
          help="Preencha APENAS se o pedido é feito por um terceiro em nome do beneficiado"
          {...reg('justificativa_procuracao')}
        />
      </FieldGroup>
    </div>
  );
}
