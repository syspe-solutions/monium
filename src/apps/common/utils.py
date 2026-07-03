class CommonUtils:
    def disable_welcome_signal(self):
        """No-op: mantido por compatibilidade com testes legados que esperam
        poder desligar um sinal de boas-vindas no cadastro de usuário — esse
        sinal não existe no projeto atual."""
        return None
