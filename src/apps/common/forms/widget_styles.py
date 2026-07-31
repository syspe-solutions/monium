"""Classes Tailwind compartilhadas pelos widgets de formulário da aplicação.

Antes duplicadas letra-por-letra em 6 arquivos de forms (account/forms/auth.py e
os 5 forms de apps/inventory/forms/) — qualquer ajuste de estilo exigia editar
todos manualmente e corria o risco de divergir entre eles.
"""

_BASE = (
    "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white "
    "placeholder:text-zinc-600 focus:outline-none focus:ring-2 "
    "focus:ring-white/60 focus:border-zinc-500"
)

INPUT = _BASE
SELECT = _BASE
TEXTAREA = f"{_BASE} resize-none"
PASSWORD = f"{_BASE} pr-10"

_CHECK_BASE = "border-zinc-700 bg-zinc-900 text-white focus:ring-2 focus:ring-white/60"
# Checkbox nativo ignora bg/border/rounded sem appearance-none, então usa o
# componente custom ".checkbox" (input.css) em vez de classes utilitárias soltas.
CHECKBOX = "checkbox"
RADIO = f"w-4 h-4 {_CHECK_BASE}"
