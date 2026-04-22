/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Paleta minimalista inspirada no formulário oficial
        primary: {
          50:  '#f5f5f4',
          100: '#e7e5e4',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          900: '#1c1917',
        },
        accent: {
          // Vermelho bandeira polonesa (sutil, só para detalhes)
          500: '#dc2626',
          600: '#b91c1c',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
