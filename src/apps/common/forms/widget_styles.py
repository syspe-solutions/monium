"""Classes Tailwind compartilhadas pelos widgets de formulário da aplicação.

Antes duplicadas letra-por-letra em 6 arquivos de forms (account/forms/auth.py e
os 5 forms de apps/inventory/forms/) — qualquer ajuste de estilo exigia editar
todos manualmente e corria o risco de divergir entre eles.
"""

_BASE = (
    "w-full p-2 border border-zinc-300 rounded text-sm bg-white text-zinc-900 "
    "placeholder:text-zinc-400 focus:outline-none focus:ring-2 "
    "focus:ring-accent/50 focus:border-accent"
)

INPUT = _BASE
SELECT = _BASE
TEXTAREA = f"{_BASE} resize-none"
PASSWORD = f"{_BASE} pr-10"

_CHECK_BASE = "border-zinc-300 bg-white text-zinc-900 focus:ring-2 focus:ring-accent/50"
# Checkbox nativo ignora bg/border/rounded sem appearance-none, então usa o
# componente custom ".checkbox" (input.css) em vez de classes utilitárias soltas.
CHECKBOX = "checkbox"
RADIO = f"w-4 h-4 {_CHECK_BASE}"
