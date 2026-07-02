import re


class CPFService:
    def is_required(self, cpf: str):
        if not cpf or not str(cpf).strip():
            return "O CPF é obrigatório"
        return True
    
    def _raw_digits(self, cpf: str) -> str:
        return re.sub(r"\D", "", cpf)
    
    def _is_all_digits_same(self, cpf: str) -> bool:
        raw = self._raw_digits(cpf)
        return re.fullmatch(r"(\d)\1{10}", raw) is not None

    def mask(self, cpf: str) -> str:
        raw = self._raw_digits(cpf)
        if len(raw) != 11:
            return raw
        return f"{raw[:3]}.{raw[3:6]}.{raw[6:9]}-{raw[9:]}"

    def check_length(self, cpf: str):
        raw = self._raw_digits(cpf)
        if len(raw) != 11:
            return "O CPF deve possuir 11 dígitos"
        return True

    def _calculate_check_digit(self, cpf: str, pesos: list[int]) -> int:
        soma = sum(int(cpf[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    def check_first_digit(self, cpf: str):
        raw = self._raw_digits(cpf)
        if self._is_all_digits_same(raw):
            return "CPF inválido (dígitos repetidos)"
        esperado = self._calculate_check_digit(raw, [10, 9, 8, 7, 6, 5, 4, 3, 2])
        if int(raw[9]) != esperado:
            return "CPF inválido (1º dígito verificador incorreto)"
        return True

    def check_second_digit(self, cpf: str):
        raw = self._raw_digits(cpf)
        if self._is_all_digits_same(raw):
            return "CPF inválido (dígitos repetidos)"
        esperado = self._calculate_check_digit(raw, [11, 10, 9, 8, 7, 6, 5, 4, 3, 2])
        if int(raw[10]) != esperado:
            return "CPF inválido (2º dígito verificador incorreto)"
        return True

    @property
    def validators(self):
        return [
            self.is_required,
            self.check_length,
            self.check_first_digit,
            self.check_second_digit
        ]