from pydantic import field_validator

from domain.entities import ValueObject


class Title(ValueObject):
    value: str

    @field_validator("value", mode="before")
    @classmethod
    def _strip(cls, raw: str) -> str:
        if not isinstance(raw, str):
            raise TypeError("title must be a string")
        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("title must not be empty")
        if len(cleaned) > 500:
            raise ValueError("title must be at most 500 characters")
        return cleaned

    def __str__(self) -> str:
        return self.value


class Body(ValueObject):
    value: str

    @field_validator("value", mode="before")
    @classmethod
    def _strip(cls, raw: str) -> str:
        if not isinstance(raw, str):
            raise TypeError("body must be a string")
        if not raw.strip():
            raise ValueError("body must not be empty")
        return raw

    def __str__(self) -> str:
        return self.value


class Tags(ValueObject):
    values: tuple[str, ...]

    @field_validator("values", mode="before")
    @classmethod
    def _normalise(cls, raw: object) -> tuple[str, ...]:
        if not isinstance(raw, (list, tuple)):
            raise TypeError("tags must be a list or tuple")
        seen: list[str] = []
        for tag in raw:
            if not isinstance(tag, str):
                raise TypeError("each tag must be a string")
            cleaned = tag.strip().lower()
            if cleaned and cleaned not in seen:
                seen.append(cleaned)
        return tuple(seen)

    def as_list(self) -> list[str]:
        return list(self.values)
