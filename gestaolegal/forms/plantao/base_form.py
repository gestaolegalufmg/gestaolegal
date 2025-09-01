from typing import Any


class BaseFormMixin:
    def populate_from_entity(
        self, entity: Any, field_mapping: dict[str, str] | None = None
    ) -> None:
        if field_mapping is None:
            for field_name in self._fields:
                if hasattr(entity, field_name):
                    field = getattr(self, field_name)
                    entity_value = getattr(entity, field_name)
                    if entity_value is not None:
                        field.data = entity_value
        else:
            for form_field, entity_attr in field_mapping.items():
                if hasattr(self, form_field) and hasattr(entity, entity_attr):
                    field = getattr(self, form_field)
                    entity_value = getattr(entity, entity_attr)
                    if entity_value is not None:
                        field.data = entity_value

    def populate_from_dict(
        self, data: dict[str, Any], field_mapping: dict[str, str] | None = None
    ) -> None:
        if field_mapping is None:
            for field_name in self._fields:
                if field_name in data:
                    field = getattr(self, field_name)
                    if data[field_name] is not None:
                        field.data = data[field_name]
        else:
            for form_field, dict_key in field_mapping.items():
                if hasattr(self, form_field) and dict_key in data:
                    field = getattr(self, form_field)
                    if data[dict_key] is not None:
                        field.data = data[dict_key]
