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
      fontFamily: {
        // Aponta pra variável definida em input.css (--font-sans) em vez de
        // listar a fonte aqui de novo — trocar a fonte do projeto vira uma
        // mudança em um único arquivo.
        sans: ["var(--font-sans)"],
      },
      colors: {
        // Cor de destaque única do tema claro: usada em links, foco, estado
        // selecionado e badges informativos. Ações estruturais (botão
        // primário, item de navegação ativo) usam preto (zinc-900/950), não
        // accent — accent é reservado a "isto é interativo/clicável".
        accent: {
          DEFAULT: "#2563EB",
          hover: "#1D4ED8",
          subtle: "#EFF6FF",
        },
      },
      boxShadow: {
        // Sombra padrão de cards/modais no tema claro: bem mais sutil que a
        // versão anterior (calibrada pra fundo escuro) — no claro, a
        // separação principal já vem da borda; a sombra só dá profundidade.
        card: "0 1px 2px 0 rgb(0 0 0 / 0.04), 0 1px 3px 0 rgb(0 0 0 / 0.06)",
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
