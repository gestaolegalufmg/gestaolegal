from dataclasses import asdict, fields, is_dataclass
from typing import Any, TypeVar

T = TypeVar("T")


def from_dict(cls: type[T], data: dict[str, Any]) -> T:
    if not is_dataclass(cls):
        raise TypeError(f"{cls} is not a dataclass")

    field_names = {f.name for f in fields(cls)}
    filtered_data = {k: v for k, v in data.items() if k in field_names}

    return cls(**filtered_data)


def to_dict(obj: Any, exclude: set[str] | None = None) -> dict[str, Any]:
    if not is_dataclass(obj):
        raise TypeError(f"{obj} is not a dataclass instance")

    result = asdict(obj)

    if exclude:
        for key in exclude:
            result.pop(key, None)

    return result
