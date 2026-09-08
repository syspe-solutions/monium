import csv
import io
from dataclasses import dataclass, field

from django.utils.translation import gettext as _

from apps.inventory.models import (
    AssetSpec,
    AssetStatus,
    Brand,
    Category,
    Item,
    ItemCondition,
    MovableAsset,
    Sector,
)

IMPORT_COLUMNS = [
    "Código", "Nome", "Categoria", "Setor", "Localização",
    "Marca", "Responsável", "Status", "Condição",
]
REQUIRED_COLUMNS = ["Código", "Nome", "Categoria", "Setor"]

_STATUS_BY_LABEL = {label.lower(): value for value, label in AssetStatus.choices}
_STATUS_BY_VALUE = {value.lower(): value for value, _ in AssetStatus.choices}
_CONDITION_BY_LABEL = {label.lower(): value for value, label in ItemCondition.choices}
_CONDITION_BY_VALUE = {value.lower(): value for value, _ in ItemCondition.choices}


@dataclass
class ImportResult:
    created_count: int = 0
    errors: list = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)


def _resolve_choice(raw_value: str, by_label: dict, by_value: dict):
    key = raw_value.strip().lower()
    return by_value.get(key) or by_label.get(key)


def import_items_from_csv(organization, csv_file, user) -> ImportResult:
    result = ImportResult()

    try:
        text = csv_file.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        result.errors.append(_("The file is not a valid UTF-8 text file."))
        return result

    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in (reader.fieldnames or [])]
    if missing_columns:
        result.errors.append(
            _("Missing required columns: %(columns)s") % {"columns": ", ".join(missing_columns)}
        )
        return result

    existing_codes = set(Item.objects.filter(organization=organization).values_list("code", flat=True))

    for row_number, row in enumerate(reader, start=2):  # header is row 1
        code = (row.get("Código") or "").strip()
        name = (row.get("Nome") or "").strip()
        category_name = (row.get("Categoria") or "").strip()
        sector_name = (row.get("Setor") or "").strip()
        location_name = (row.get("Localização") or "").strip()
        brand_name = (row.get("Marca") or "").strip()
        responsible = (row.get("Responsável") or "").strip()
        status_raw = (row.get("Status") or "").strip()
        condition_raw = (row.get("Condição") or "").strip()

        if not code or not name:
            result.errors.append(_("Row %(row)s: code and name are required.") % {"row": row_number})
            continue

        if code in existing_codes:
            result.errors.append(
                _('Row %(row)s: an item with code "%(code)s" already exists.')
                % {"row": row_number, "code": code}
            )
            continue

        category = Category.objects.filter(name__iexact=category_name).first() if category_name else None
        if not category:
            result.errors.append(
                _('Row %(row)s: category "%(name)s" not found.')
                % {"row": row_number, "name": category_name}
            )
            continue

        sector = Sector.objects.filter(name__iexact=sector_name).first() if sector_name else None
        if not sector:
            result.errors.append(
                _('Row %(row)s: sector "%(name)s" not found.')
                % {"row": row_number, "name": sector_name}
            )
            continue

        location = None
        if location_name:
            location = sector.locations.filter(name__iexact=location_name).first()
            if not location:
                result.errors.append(
                    _('Row %(row)s: location "%(name)s" not found in sector "%(sector)s".')
                    % {"row": row_number, "name": location_name, "sector": sector.name}
                )
                continue

        status = _resolve_choice(status_raw, _STATUS_BY_LABEL, _STATUS_BY_VALUE) if status_raw else AssetStatus.IN_USE
        if status_raw and not status:
            result.errors.append(
                _('Row %(row)s: unknown status "%(value)s".') % {"row": row_number, "value": status_raw}
            )
            continue

        condition = (
            _resolve_choice(condition_raw, _CONDITION_BY_LABEL, _CONDITION_BY_VALUE)
            if condition_raw else ItemCondition.GOOD
        )
        if condition_raw and not condition:
            result.errors.append(
                _('Row %(row)s: unknown condition "%(value)s".') % {"row": row_number, "value": condition_raw}
            )
            continue

        item = MovableAsset.objects.create(
            organization=organization,
            code=code,
            name=name,
            category=category,
            sector=sector,
            location=location,
            responsible=responsible,
            status=status,
            condition=condition,
            created_by=user,
            updated_by=user,
        )
        existing_codes.add(code)

        if brand_name:
            brand, _created = Brand.objects.get_or_create(
                name__iexact=brand_name,
                defaults={"name": brand_name, "created_by": user, "updated_by": user},
            )
            AssetSpec.objects.create(asset=item, brand=brand, created_by=user, updated_by=user)

        result.created_count += 1

    return result
