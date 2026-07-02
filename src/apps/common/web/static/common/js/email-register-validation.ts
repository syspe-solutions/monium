import { EmailValidator } from "@common/email-validator.ts";

const validator = new EmailValidator();
const ERROR_LIST_ID = "email-client-errors";

function showErrors(input: HTMLInputElement, errors: string[]): void {
    removeErrors(input);

    
    const ul = document.createElement("ul");
    ul.id = ERROR_LIST_ID;
    ul.className = "flex flex-col gap-0.5";
    
    errors.forEach(function (message: string): void {
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
    const emailInput = document.getElementById("id_email") as HTMLInputElement | null;

    if (!form || !emailInput) return;

    emailInput.addEventListener("blur", function (): void {
        if (emailInput.value.trim() !== "") {
            validate(emailInput);
        }
    });

    emailInput.addEventListener("input", function (): void {
        removeErrors(emailInput);
    });

    form.addEventListener("submit", function (e: Event): void {
        if (!validate(emailInput)) {
            e.preventDefault();
            emailInput.focus();
        }
    });
});
