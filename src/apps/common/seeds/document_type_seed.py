from apps.business.models.document_type import DocumentType
from apps.common.seeds.base_seed import BaseSeed


class DocumentTypeSeed(BaseSeed):
    DATA = [
        {"type": "RG"},
        {"type": "CPF"},
        {"type": "CNH"},
        {"type": "Comprovante de Residência"},
        {"type": "Comprovante de Renda"},
        {"type": "Passaporte"},
        {"type": "Título de Eleitor"},
        {"type": "Certidão de Nascimento"},
        {"type": "Certidão de Casamento"},
    ]

    def run(self) -> str:
        return self.populate_if_needed(
            model=DocumentType,
            data=self.DATA,
            unique_field="type",
        )
