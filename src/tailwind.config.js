/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./apps/**/templates/**/*.html",
    "./apps/**/static/**/*.js",
    "./apps/**/static/**/*.ts",
  ],
  // Classes que o Django gera em runtime (ex.: "errorlist" nos formulários)
  // nunca aparecem escritas nos templates, então o scanner de content não as
  // vê e o Tailwind faz purge da regra em @layer components — precisam ser
  // listadas aqui manualmente.
  safelist: ["errorlist"],
  theme: {
    extend: {
      boxShadow: {
        // Sombra padrão de cards/modais em toda a aplicação (antes espalhada
        // como "shadow-xl shadow-black/20" em ~30 templates).
        card: "0 20px 25px -5px rgb(0 0 0 / 0.20), 0 8px 10px -6px rgb(0 0 0 / 0.20)",
      },
      transitionTimingFunction: {
        // Curva padrão de easing (macOS/iOS) para motion de UI: sidebar,
        // dropdowns, modais.
        apple: "cubic-bezier(0.4, 0, 0.2, 1)",
      },
    },
  },
  plugins: [],
}
