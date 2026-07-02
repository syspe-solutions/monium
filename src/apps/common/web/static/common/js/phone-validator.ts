import { brazilDDDs } from "@common/utils/brazil-ddds.ts";

export class PhoneValidator {
    mask(phone: string): string {
        phone = phone.replace(/\D/g, "").slice(0, 11);

        if (phone.length <= 2) {
            phone = phone.replace(/^(\d{1,2})/, "($1");
        } else if (phone.length <= 7) {
            phone = phone.replace(/^(\d{2})(\d+)/, "($1) $2");
        } else {
            phone = phone.replace(/^(\d{2})(\d{5})(\d{0,4})/, "($1) $2-$3");
        }

        return phone;
    }

    getRawDigits(phone: string): string {
        return phone.replace(/\D/g, "");
    }

    private checkLength(phone: string): true | string {
        return this.getRawDigits(phone).length === 11
            ? true
            : "O número deve conter exatamente 11 dígitos.";
    }

    private checkDDD(phone: string): true | string {
        const ddd = this.getRawDigits(phone).slice(0, 2);
        return brazilDDDs.includes(ddd) ? true : "O DDD é inválido.";
    }

    private checkFirstDigit(phone: string): true | string {
        return this.getRawDigits(phone)[2] === "9"
            ? true
            : "O número deve começar com 9 após o DDD.";
    }

    validate(phone: string): true | string[] {
        const checks: Array<(p: string) => true | string> = [
            this.checkLength.bind(this),
            this.checkDDD.bind(this),
            this.checkFirstDigit.bind(this),
        ];

        const errors = checks
            .map((check) => check(phone))
            .filter((result): result is string => result !== true);

        return errors.length === 0 ? true : errors;
    }
}
