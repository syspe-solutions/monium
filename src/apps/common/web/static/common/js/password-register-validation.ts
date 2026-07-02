const PASSWORD_ERROR_ID = "password-client-errors";
const CONFIRM_ERROR_ID = "confirm-password-client-errors";

const SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?/";

function validatePasswordRules(value: string): string[] {
    const errors: string[] = [];
    if (value.length < 8) {
        errors.push("A senha deve ter pelo menos 8 caracteres.");
    }
    if (!errors.length || value.length >= 8) {
        if (!/[a-zA-Z]/.test(value) || !/[0-9]/.test(value)) {
            errors.push("A senha deve conter letras e números.");
        }
        if (![...value].some((c) => SPECIAL_CHARS.includes(c))) {
            errors.push("A senha deve conter pelo menos um caractere especial.");
        }
    }
    return errors;
}

function showErrors(input: HTMLInputElement, errors: string[], errorId: string): void {
    removeErrors(input, errorId);

    const ul = document.createElement("ul");
    ul.id = errorId;
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

function removeErrors(input: HTMLInputElement, errorId: string): void {
    document.getElementById(errorId)?.remove();
    input.classList.remove("!border-red-400", "focus:!ring-red-400");
}

function validatePassword(input: HTMLInputElement): boolean {
    if (input.value.trim() === "") return true;
    const errors = validatePasswordRules(input.value);
    if (errors.length) {
        showErrors(input, errors, PASSWORD_ERROR_ID);
        return false;
    }
    removeErrors(input, PASSWORD_ERROR_ID);
    return true;
}

function validateConfirm(passwordInput: HTMLInputElement, confirmInput: HTMLInputElement): boolean {
    if (confirmInput.value.trim() === "") return true;
    if (passwordInput.value !== confirmInput.value) {
        showErrors(confirmInput, ["As senhas não coincidem."], CONFIRM_ERROR_ID);
        return false;
    }
    removeErrors(confirmInput, CONFIRM_ERROR_ID);
    return true;
}

document.addEventListener("DOMContentLoaded", function (): void {
    const form = document.querySelector<HTMLFormElement>("form[method='post']");
    const passwordInput = document.getElementById("id_password") as HTMLInputElement | null;
    const confirmInput = document.getElementById("id_confirm_password") as HTMLInputElement | null;

    if (!form || !passwordInput || !confirmInput) return;

    passwordInput.addEventListener("blur", function (): void {
        validatePassword(passwordInput);
        if (confirmInput.value.trim() !== "") {
            validateConfirm(passwordInput, confirmInput);
        }
    });

    passwordInput.addEventListener("input", function (): void {
        removeErrors(passwordInput, PASSWORD_ERROR_ID);
        if (confirmInput.value.trim() !== "") {
            validateConfirm(passwordInput, confirmInput);
        }
    });

    confirmInput.addEventListener("blur", function (): void {
        validateConfirm(passwordInput, confirmInput);
    });

    confirmInput.addEventListener("input", function (): void {
        removeErrors(confirmInput, CONFIRM_ERROR_ID);
    });

    form.addEventListener("submit", function (e: Event): void {
        const passwordOk = validatePassword(passwordInput);
        const confirmOk = validateConfirm(passwordInput, confirmInput);

        if (!passwordOk) {
            e.preventDefault();
            passwordInput.focus();
        } else if (!confirmOk) {
            e.preventDefault();
            confirmInput.focus();
        }
    });
});
