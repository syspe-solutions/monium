import { CpfValidator } from "@common/cpf-validator.ts";

const validator = new CpfValidator();
const ERROR_LIST_ID = "cpf-client-errors";

function showErrors(input: HTMLInputElement, errors: string[]): void {
    removeErrors(input);

    const unique = [...new Set(errors)];

    const ul = document.createElement("ul");
    ul.id = ERROR_LIST_ID;
    ul.className = "flex flex-col gap-0.5";

    unique.forEach(function (message: string): void {
        const li = document.createElement("li");
        li.className = "flex items-center gap-1 text-xs text-red-600";
        li.innerHTML = `<span class="material-symbols-outlined text-xs leading-none">error</span>${message}`;
        ul.appendChild(li);
    });

    input.classList.add("!border-red-400", "focus:!ring-red-400");
    input.insertAdjacentElement("afterend", ul);
}

function removeErrors(input: HTMLInputElement): void {
    document.getElementById(ERROR_LIST_ID)?.remove();
    input.classList.remove("!border-red-400", "focus:!ring-red-400");
}

function validate(input: HTMLInputElement): boolean {
    const result = validator.validate(input.value);
    if (result !== true) {
        showErrors(input, result);
        return false;
    }
    removeErrors(input);
    return true;
}

document.addEventListener("DOMContentLoaded", function (): void {
    const form = document.querySelector<HTMLFormElement>("form[method='post']");
    const cpfInput = document.getElementById("id_cpf") as HTMLInputElement | null;

    if (!form || !cpfInput) return;

    cpfInput.addEventListener("blur", function (): void {
        if (cpfInput.value.trim() !== "") {
            validate(cpfInput);
        }
    });

    cpfInput.addEventListener("input", function (): void {
        removeErrors(cpfInput);
    });

    form.addEventListener("submit", function (e: Event): void {
        if (!validate(cpfInput)) {
            e.preventDefault();
            cpfInput.focus();
        }
    });
});
