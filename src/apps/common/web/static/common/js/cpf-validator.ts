export class CpfValidator {
  getRawDigits(cpf: string): string {
    return cpf.replace(/\D/g, "");
  }

  private isAllDigitsSame(cpf: string): boolean {
    const raw = this.getRawDigits(cpf);
    return /^(\d)\1{10}$/.test(raw);
  }

  mask(cpf: string): string {
    let raw = this.getRawDigits(cpf);
    raw = raw.replace(/^(\d{3})(\d)/, "$1.$2");
    raw = raw.replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3");
    raw = raw.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
    return raw;
  }

  isRequired(cpf: string): true | string {
    const raw = this.getRawDigits(cpf);
    if (!raw || raw.trim() === "") {
      return "Esse campo é obrigatório";
    }
    return true;
  }

  private checkLength(cpf: string): true | string {
    const raw = this.getRawDigits(cpf);
    if (raw.length !== 11) {
      return "O CPF deve possuir 11 dígitos";
    }
    return true;
  }

  private calculateCheckDigit(cpf: string, peso: number[]): number {
    let sum = 0;
    for (let i = 0; i < peso.length; i++) {
      sum += parseInt(cpf.charAt(i), 10) * peso[i];
    }

    const remainder = sum % 11;
    return remainder < 2 ? 0 : 11 - remainder;
  }

  private checkFirstDigit(cpf: string): true | string {
    const raw = this.getRawDigits(cpf);

    if (this.isAllDigitsSame(raw)) {
      return "CPF inválido (dígitos repetidos)";
    }

    const expected = this.calculateCheckDigit(raw, [
      10, 9, 8, 7, 6, 5, 4, 3, 2
    ]);

    if (parseInt(raw.charAt(9), 10) !== expected) {
      return "CPF inválido (1º dígito verificador incorreto)";
    }

    return true;
  }

  private checkSecondDigit(cpf: string): true | string {
    const raw = this.getRawDigits(cpf);

    if (this.isAllDigitsSame(raw)) {
      return "CPF inválido (dígitos repetidos)";
    }

    const expected = this.calculateCheckDigit(raw, [
      11, 10, 9, 8, 7, 6, 5, 4, 3, 2
    ]);

    if (parseInt(raw.charAt(10), 10) !== expected) {
      return "CPF inválido (2º dígito verificador incorreto)";
    }

    return true;
  }

  validate(cpf: string): true | string[] {
    const checks: Array<(cpf: string) => true | string> = [
      this.checkLength.bind(this),
      this.checkFirstDigit.bind(this),
      this.checkSecondDigit.bind(this),
    ];

    const errors = checks
      .map(check => check(cpf))
      .filter(result => result !== true) as string[];

    return errors.length === 0 ? true : errors;
  }
}
