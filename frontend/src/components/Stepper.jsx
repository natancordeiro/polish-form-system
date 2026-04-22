import { Check } from 'lucide-react';

/**
 * Indicador visual de progresso no formulário multi-step.
 * Mostra os passos concluídos, o atual e os pendentes.
 */
export function Stepper({ steps, currentIndex, onStepClick }) {
  return (
    <nav aria-label="Progresso">
      <ol className="flex items-center gap-0 overflow-x-auto">
        {steps.map((step, idx) => {
          const isComplete = idx < currentIndex;
          const isCurrent = idx === currentIndex;

          return (
            <li key={step.id} className="flex items-center flex-shrink-0">
              <button
                type="button"
                onClick={() => onStepClick(idx)}
                className={`group flex items-center gap-2 transition-colors ${
                  isCurrent ? 'text-stone-900' : isComplete ? 'text-stone-600 hover:text-stone-900' : 'text-stone-400'
                }`}
              >
                <span
                  className={`
                    flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold
                    transition-colors shrink-0
                    ${isCurrent ? 'bg-stone-900 text-white' : ''}
                    ${isComplete ? 'bg-stone-900 text-white' : ''}
                    ${!isComplete && !isCurrent ? 'bg-stone-200 text-stone-500' : ''}
                  `}
                >
                  {isComplete ? <Check className="w-4 h-4" /> : idx + 1}
                </span>
                <span className="text-sm font-medium hidden md:inline whitespace-nowrap">
                  {step.title}
                </span>
              </button>
              {idx < steps.length - 1 && (
                <span
                  className={`mx-3 h-px w-8 md:w-12 ${
                    isComplete ? 'bg-stone-900' : 'bg-stone-200'
                  }`}
                />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
