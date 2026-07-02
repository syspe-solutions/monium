import subprocess
import sys
from pathlib import Path

from django.core.management.base import BaseCommand

BASE_DIR = Path(__file__).resolve().parents[4]


class Command(BaseCommand):
    help = "Compila assets TypeScript e Tailwind CSS."

    def add_arguments(self, parser):
        parser.add_argument(
            "--watch",
            action="store_true",
            help="Modo watch: recompila ao detectar mudanças (dois processos paralelos).",
        )

    def handle(self, *args, **options):
        watch = options["watch"]
        mode = "watch" if watch else "build"

        self.stdout.write(
            self.style.MIGRATE_HEADING(f"\n=== Build de Assets ({mode}) ===\n")
        )

        if not (BASE_DIR / "node_modules").exists():
            self.stdout.write("Instalando dependências Node.js...")
            result = subprocess.run(["npm", "install"], cwd=BASE_DIR)
            if result.returncode != 0:
                self.stdout.write(self.style.ERROR("Falha ao instalar dependências."))
                sys.exit(1)
            self.stdout.write(self.style.SUCCESS("Dependências instaladas.\n"))

        if watch:
            self._watch()
        else:
            self._build()

    def _build(self):
        result = subprocess.run(["npm", "run", "build"], cwd=BASE_DIR)
        if result.returncode != 0:
            self.stdout.write(self.style.ERROR("Build falhou."))
            sys.exit(1)
        self.stdout.write(self.style.SUCCESS("\nBuild concluído com sucesso!"))

    def _watch(self):
        self.stdout.write("Iniciando watchers (Ctrl+C para encerrar)...\n")
        ts_proc = subprocess.Popen(["npm", "run", "watch:ts"], cwd=BASE_DIR)
        css_proc = subprocess.Popen(["npm", "run", "watch:css"], cwd=BASE_DIR)
        try:
            ts_proc.wait()
            css_proc.wait()
        except KeyboardInterrupt:
            ts_proc.terminate()
            css_proc.terminate()
            self.stdout.write("\nWatchers encerrados.")
