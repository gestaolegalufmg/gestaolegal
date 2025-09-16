from typing import Any, Protocol


class HasDataAttribute(Protocol):
    data: dict[str, Any]

    def _postprocess_data(self) -> dict[str, Any]: ...


class BaseFormMixin:
    def to_dict(self: HasDataAttribute) -> dict[str, Any]:
        raw: dict[str, Any] = self.data
        processed_data: dict[str, Any] = {}
        for name, value in raw.items():
            if name in {"csrf_token", "submit"}:
                continue
            if value is None:
                continue
            processed_data[name] = value

        return self._postprocess_data()

    def _postprocess_data(self: HasDataAttribute) -> dict[str, Any]:
        return self.data
