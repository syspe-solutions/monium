export class CnpjValidator {
  getRaw(cnpj: string): string {
    return cnpj.replace(/[^A-Z0-9]/gi, "").toUpperCase();
  }

  mask(cnpj: string): string {
    let raw = this.getRaw(cnpj);

    raw = raw.replace(/^([A-Z0-9]{2})([A-Z0-9])/, "$1.$2");
    raw = raw.replace(/^([A-Z0-9]{2})\.([A-Z0-9]{3})([A-Z0-9])/, "$1.$2.$3");
    raw = raw.replace(/\.([A-Z0-9]{3})([A-Z0-9])/, ".$1/$2");
    raw = raw.replace(/([A-Z0-9]{4})([A-Z0-9])/, "$1-$2");

    return raw;
  }

  isRequired(cnpj: string): true | string {
    const raw = this.getRaw(cnpj);

    if (!raw) {
      return "Esse campo é obrigatório";
    }

    return true;
  }

  private checkPattern(cnpj: string): true | string {
    const raw = this.getRaw(cnpj);

    if (raw.length !== 14) {
      return "O CNPJ deve possuir 14 caracteres";
    }

    const regex = /^[A-Z0-9]{14}$/;

    if (!regex.test(raw)) {
      return "Formato inválido (somente letras e números)";
    }

    return true;
  }

  validate(cnpj: string): true | string[] {
    const checks: Array<(cnpj: string) => true | string> = [
      this.checkPattern.bind(this),
    ];

    const errors = checks
      .map(check => check(cnpj))
      .filter(result => result !== true) as string[];

    return errors.length === 0 ? true : errors;
  }
}