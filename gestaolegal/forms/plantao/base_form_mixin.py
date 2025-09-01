from typing import Any


class BaseFormMixin:
    def populate_from_entity(
        self, entity: Any, field_mapping: dict[str, str] | None = None
    ) -> None:
        mapped_fields = set(field_mapping.keys()) if field_mapping else set()

        for field_name in self._fields:
            if field_name in mapped_fields:
                entity_attr = field_mapping[field_name]
                if hasattr(entity, entity_attr):
                    field = getattr(self, field_name)
                    entity_value = getattr(entity, entity_attr)
                    if entity_value is not None:
                        field.data = entity_value
            elif hasattr(entity, field_name):
                field = getattr(self, field_name)
                entity_value = getattr(entity, field_name)
                if entity_value is not None:
                    field.data = entity_value
