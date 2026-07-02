export class EmailValidator {
    private static readonly REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

    validate(email: string): true | string[] {
        const trimmed = email.trim();

        if (!trimmed) {
            return ["Este campo é obrigatório"];
        }

        if (!EmailValidator.REGEX.test(trimmed)) {
            return ["Insira um endereço de e-mail válido"];
        }

        return true;
    }
}
