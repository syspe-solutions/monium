import * as esbuild from "esbuild";
import { glob } from "glob";

const isWatch = process.argv.includes("--watch");

/**
 * Descobre automaticamente os entry points TypeScript em todos os apps.
 *
 * Convenção de pastas:
 *   - Arquivos em /utils/ são bibliotecas de dados/constantes — não geram bundle próprio.
 *   - Todo arquivo .ts fora de dist/ e utils/ é um entry point.
 *
 * Para adicionar um novo script ao build, basta criar o arquivo .ts na pasta
 * static correspondente — ele será detectado automaticamente.
 */
const entryPoints = await glob("apps/**/static/**/*.ts", {
    ignore: ["**/dist/**", "**/utils/**"],
});

if (entryPoints.length === 0) {
    console.log("Nenhum entry point TypeScript encontrado.");
    process.exit(0);
}

console.log(`\nEntry points TypeScript encontrados (${entryPoints.length}):`);
entryPoints.forEach((e) => console.log(`  → ${e}`));
console.log("");

/**
 * Cada entry point é compilado para seu próprio dist/ dentro da mesma pasta.
 *
 * Exemplo:
 *   apps/common/web/static/common/js/cpf-mask.ts
 *   → apps/common/web/static/common/js/dist/cpf-mask.js
 */
const config = {
    entryPoints,
    bundle: true,
    outbase: ".",
    outdir: ".",
    entryNames: "[dir]/dist/[name]",
    format: "iife",
    target: "es2017",
    minify: !isWatch,
    tsconfig: "./tsconfig.json",
};

if (isWatch) {
    const ctx = await esbuild.context({
        ...config,
        plugins: [
            {
                name: "watch-log",
                setup(build) {
                    build.onEnd((result) => {
                        if (result.errors.length === 0) {
                            const time = new Date().toLocaleTimeString("pt-BR");
                            console.log(`[${time}] TypeScript recompilado.`);
                        }
                    });
                },
            },
        ],
    });
    await ctx.watch();
    console.log("Watching TypeScript... (Ctrl+C para encerrar)\n");
} else {
    await esbuild.build(config);
    console.log("Build TypeScript concluído.");
}
