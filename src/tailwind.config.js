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
    extend: {},
  },
  plugins: [],
}
