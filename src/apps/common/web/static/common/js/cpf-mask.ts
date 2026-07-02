(function (): void {
    function getRawDigits(value: string): string {
        return value.replace(/\D/g, "").slice(0, 11);
    }

    function mask(value: string): string {
        let raw = getRawDigits(value);
        raw = raw.replace(/^(\d{3})(\d)/, "$1.$2");
        raw = raw.replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3");
        raw = raw.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
        return raw;
    }

    function applyMask(input: HTMLInputElement): void {
        input.setAttribute("maxlength", "14");
        input.addEventListener("input", function (e: Event): void {
            const target = e.target as HTMLInputElement;
            target.value = mask(target.value);
        });
    }

    document.addEventListener("DOMContentLoaded", function (): void {
        document.querySelectorAll<HTMLInputElement>('[data-mask="cpf"]').forEach(applyMask);
    });
})();
