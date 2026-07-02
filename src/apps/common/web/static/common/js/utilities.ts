function copyToClipboard(source: string | HTMLElement, icon: string | HTMLElement | null = null): void {
    const textElement = typeof source === "string"
        ? document.getElementById(source)
        : source;

    if (!textElement) {
        console.error("Elemento de texto não encontrado:", source);
        return;
    }

    const text = textElement.textContent?.trim() ?? "";

    navigator.clipboard.writeText(text).then((): void => {
        if (!icon) return;

        const iconElement = typeof icon === "string"
            ? document.getElementById(icon)
            : icon;

        if (iconElement) {
            iconElement.textContent = "check";
            setTimeout((): void => {
                iconElement.textContent = "content_copy";
            }, 1500);
        }
    }).catch((err: unknown): void => {
        console.error("Erro ao copiar:", err);
    });
}

function isValidUrl(string: string): boolean {
    try {
        const url = new URL(string);
        return url.protocol === "http:" || url.protocol === "https:";
    } catch {
        return false;
    }
}
