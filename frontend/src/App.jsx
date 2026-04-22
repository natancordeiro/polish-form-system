import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ChevronLeft, ChevronRight, Download, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

import { formSchema, emptyFormValues } from './lib/schema.js';
import { generatePdf, healthCheck } from './services/api.js';
import { Stepper } from './components/Stepper.jsx';

import { StepCabecalho } from './components/steps/StepCabecalho.jsx';
import { StepSolicitante } from './components/steps/StepSolicitante.jsx';
import { StepPais } from './components/steps/StepPais.jsx';
import { StepAvos } from './components/steps/StepAvos.jsx';
import { StepBiografias } from './components/steps/StepBiografias.jsx';
import { StepInfoEAnexos } from './components/steps/StepInfoEAnexos.jsx';

// ---------------------------------------------------------------------------
// Definição das etapas
// ---------------------------------------------------------------------------
// Cada step declara quais campos participam da validação daquela etapa.
// Isso permite validar por etapa sem precisar preencher o formulário inteiro.
const STEPS = [
  {
    id: 'cabecalho',
    title: 'Cabeçalho',
    description: 'Dados do pedido e requerente',
    component: StepCabecalho,
    fields: [
      'local_submissao', 'data_submissao', 'wojewoda',
      'requerente_nome_completo', 'requerente_endereco',
      'tipo_decisao', 'nome_titular_confirmacao', 'info_adicional_pedido',
    ],
  },
  {
    id: 'solicitante',
    title: 'Beneficiado',
    description: 'Dados pessoais da pessoa cuja cidadania é confirmada',
    component: StepSolicitante,
    fields: ['solicitante', 'enderecos_vida'],
  },
  {
    id: 'pais',
    title: 'Pais',
    description: 'Dados dos pais do beneficiado',
    component: StepPais,
    fields: ['mae', 'pai'],
  },
  {
    id: 'avos',
    title: 'Avós',
    description: 'Dados dos quatro avós',
    component: StepAvos,
    fields: ['avo_materno', 'avo_materna', 'avo_paterno', 'avo_paterna'],
  },
  {
    id: 'biografias',
    title: 'Biografias',
    description: 'Relato biográfico — será traduzido para polonês',
    component: StepBiografias,
    fields: ['biografia_solicitante'],
  },
  {
    id: 'info',
    title: 'Info & Anexos',
    description: 'Informações adicionais e lista de anexos',
    component: StepInfoEAnexos,
    fields: [],
  },
];

// ---------------------------------------------------------------------------
// Persistência em localStorage
// ---------------------------------------------------------------------------
const STORAGE_KEY = 'polish-form-draft-v1';

function loadDraft() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveDraft(values) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(values));
  } catch {
    /* ignore */
  }
}

function clearDraft() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
}

// ---------------------------------------------------------------------------
// Componente principal
// ---------------------------------------------------------------------------
export default function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [status, setStatus] = useState({ kind: 'idle' });
  const [apiHealth, setApiHealth] = useState(null);

  const { register, control, handleSubmit, formState, trigger, getValues, reset, watch } = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: loadDraft() || emptyFormValues,
    mode: 'onBlur',
  });

  const { errors } = formState;

  // Auto-save no localStorage a cada mudança (debounced pelo React)
  useEffect(() => {
    const subscription = watch((value) => saveDraft(value));
    return () => subscription.unsubscribe();
  }, [watch]);

  // Healthcheck na inicialização
  useEffect(() => {
    healthCheck().then(setApiHealth);
  }, []);

  const step = STEPS[currentStep];
  const StepComponent = step.component;
  const isLast = currentStep === STEPS.length - 1;
  const isFirst = currentStep === 0;

  // ---- Navegação entre steps ----
  async function goNext() {
    // Valida apenas os campos da etapa atual
    const ok = step.fields.length === 0 ? true : await trigger(step.fields);
    if (!ok) {
      // Scroll ao primeiro erro
      const firstError = document.querySelector('.input-error');
      firstError?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }
    setCurrentStep((i) => Math.min(i + 1, STEPS.length - 1));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function goPrev() {
    setCurrentStep((i) => Math.max(i - 1, 0));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function jumpTo(idx) {
    if (idx < currentStep) {
      // Permite voltar sem revalidar
      setCurrentStep(idx);
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    // Para avançar, valida tudo até o step de destino
    const fieldsToValidate = STEPS.slice(currentStep, idx)
      .flatMap((s) => s.fields);
    const ok = fieldsToValidate.length === 0 ? true : await trigger(fieldsToValidate);
    if (ok) {
      setCurrentStep(idx);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  // ---- Submissão ----
  async function onSubmit(values) {
    setStatus({ kind: 'loading' });
    try {
      const result = await generatePdf(values);
      setStatus({ kind: 'success', filename: result.filename });
    } catch (err) {
      setStatus({ kind: 'error', message: err.message });
    }
  }

  function startOver() {
    if (!confirm('Tem certeza que deseja limpar todos os dados e começar do zero?')) return;
    clearDraft();
    reset(emptyFormValues);
    setCurrentStep(0);
    setStatus({ kind: 'idle' });
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    <div className="min-h-screen bg-stone-50">
      {/* ---------- Header ---------- */}
      <header className="bg-white border-b border-stone-200 sticky top-0 z-20">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-stone-900">
              Requerimento de Cidadania Polonesa
            </h1>
            <p className="text-xs text-stone-500">
              Preencha em português — a saída é gerada automaticamente em polonês
            </p>
          </div>
          <div className="flex items-center gap-3">
            {apiHealth && (
              <span className={`flex items-center gap-1.5 text-xs ${
                apiHealth.deepl_configured ? 'text-emerald-600' : 'text-amber-600'
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${
                  apiHealth.deepl_configured ? 'bg-emerald-500' : 'bg-amber-500'
                }`} />
                {apiHealth.deepl_configured ? 'API online' : 'DeepL não configurado'}
              </span>
            )}
            <button
              type="button"
              onClick={startOver}
              className="text-xs text-stone-500 hover:text-stone-900"
            >
              Limpar rascunho
            </button>
          </div>
        </div>

        <div className="max-w-5xl mx-auto px-4 pb-4">
          <Stepper
            steps={STEPS}
            currentIndex={currentStep}
            onStepClick={jumpTo}
          />
        </div>
      </header>

      {/* ---------- Form ---------- */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="section-card">
            <div className="mb-6 pb-4 border-b border-stone-100">
              <h2 className="text-xl font-bold text-stone-900">{step.title}</h2>
              <p className="text-sm text-stone-500 mt-1">{step.description}</p>
            </div>

            <StepComponent
              register={register}
              errors={errors}
              control={control}
              getValues={getValues}
            />
          </div>

          {/* ---------- Status banner ---------- */}
          {status.kind === 'success' && (
            <div className="rounded-md bg-emerald-50 border border-emerald-200 p-4 flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-emerald-900">
                  PDF gerado com sucesso!
                </p>
                <p className="text-xs text-emerald-700 mt-0.5">
                  O download do arquivo <code>{status.filename}</code> foi iniciado.
                </p>
              </div>
            </div>
          )}

          {status.kind === 'error' && (
            <div className="rounded-md bg-red-50 border border-red-200 p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-red-900">Erro ao gerar PDF</p>
                <p className="text-xs text-red-700 mt-0.5">{status.message}</p>
              </div>
            </div>
          )}

          {/* ---------- Navegação ---------- */}
          <div className="flex items-center justify-between gap-3">
            <button
              type="button"
              onClick={goPrev}
              disabled={isFirst}
              className="btn-secondary"
            >
              <ChevronLeft className="w-4 h-4" />
              Anterior
            </button>

            <div className="text-xs text-stone-500">
              Etapa {currentStep + 1} de {STEPS.length}
            </div>

            {isLast ? (
              <button
                type="submit"
                disabled={status.kind === 'loading'}
                className="btn-primary"
              >
                {status.kind === 'loading' ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Gerando PDF…
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    Gerar PDF em Polonês
                  </>
                )}
              </button>
            ) : (
              <button type="button" onClick={goNext} className="btn-primary">
                Próximo
                <ChevronRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </form>
      </main>

      <footer className="max-w-5xl mx-auto px-4 py-6 text-xs text-stone-400 text-center">
        Sistema desenvolvido por TGN Technologies
      </footer>
    </div>
  );
}
