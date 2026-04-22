import { forwardRef } from 'react';

/**
 * Conjunto de componentes de formulário controlados,
 * prontos para serem usados com react-hook-form via {...register()}.
 *
 * Todos aceitam `error` (string) e renderizam a mensagem abaixo do campo.
 */

function baseClass(error) {
  return `input ${error ? 'input-error' : ''}`;
}

// ---------------------------------------------------------------------------
// Input
// ---------------------------------------------------------------------------
export const Input = forwardRef(function Input(
  { label, error, help, type = 'text', required, className = '', ...props },
  ref
) {
  return (
    <div className={className}>
      {label && (
        <label className="label">
          {label}
          {required && <span className="text-red-500 ml-0.5">*</span>}
        </label>
      )}
      <input ref={ref} type={type} className={baseClass(error)} {...props} />
      {help && !error && <p className="help-text">{help}</p>}
      {error && <p className="error-text">{error}</p>}
    </div>
  );
});

// ---------------------------------------------------------------------------
// Textarea
// ---------------------------------------------------------------------------
export const Textarea = forwardRef(function Textarea(
  { label, error, help, required, rows = 4, className = '', ...props },
  ref
) {
  return (
    <div className={className}>
      {label && (
        <label className="label">
          {label}
          {required && <span className="text-red-500 ml-0.5">*</span>}
        </label>
      )}
      <textarea
        ref={ref}
        rows={rows}
        className={`${baseClass(error)} resize-y`}
        {...props}
      />
      {help && !error && <p className="help-text">{help}</p>}
      {error && <p className="error-text">{error}</p>}
    </div>
  );
});

// ---------------------------------------------------------------------------
// Select
// ---------------------------------------------------------------------------
export const Select = forwardRef(function Select(
  { label, error, help, required, children, className = '', ...props },
  ref
) {
  return (
    <div className={className}>
      {label && (
        <label className="label">
          {label}
          {required && <span className="text-red-500 ml-0.5">*</span>}
        </label>
      )}
      <select ref={ref} className={baseClass(error)} {...props}>
        {children}
      </select>
      {help && !error && <p className="help-text">{help}</p>}
      {error && <p className="error-text">{error}</p>}
    </div>
  );
});

// ---------------------------------------------------------------------------
// Checkbox
// ---------------------------------------------------------------------------
export const Checkbox = forwardRef(function Checkbox(
  { label, error, help, className = '', ...props },
  ref
) {
  return (
    <div className={className}>
      <label className="flex items-start gap-2 cursor-pointer select-none">
        <input
          ref={ref}
          type="checkbox"
          className="mt-0.5 h-4 w-4 rounded border-stone-300 text-stone-900 focus:ring-stone-900"
          {...props}
        />
        <span className="text-sm text-stone-700">{label}</span>
      </label>
      {help && !error && <p className="help-text">{help}</p>}
      {error && <p className="error-text">{error}</p>}
    </div>
  );
});

// ---------------------------------------------------------------------------
// FieldGroup - agrupa campos relacionados com um título
// ---------------------------------------------------------------------------
export function FieldGroup({ title, description, children }) {
  return (
    <div className="space-y-4">
      {title && (
        <div>
          <h3 className="text-base font-semibold text-stone-900">{title}</h3>
          {description && (
            <p className="text-sm text-stone-500 mt-0.5">{description}</p>
          )}
        </div>
      )}
      <div className="space-y-4">{children}</div>
    </div>
  );
}
