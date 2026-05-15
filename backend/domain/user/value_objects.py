from pydantic import EmailStr, field_validator

from domain.entities import ValueObject


class Email(ValueObject):
    value: EmailStr

    @field_validator("value", mode="before")
    @classmethod
    def _normalise(cls, raw: str) -> str:
        if not isinstance(raw, str):
            raise TypeError("email must be a string")
        return raw.strip().lower()

    def __str__(self) -> str:
        return self.value


class FullName(ValueObject):
    first: str
    last: str

    @field_validator("first", "last", mode="before")
    @classmethod
    def _strip(cls, raw: str) -> str:
        if not isinstance(raw, str):
            raise TypeError("name parts must be strings")
        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("name parts must not be empty")
        return cleaned

    @property
    def display(self) -> str:
        return f"{self.first} {self.last}"


class Username(ValueObject):
    value: str

    @field_validator("value", mode="before")
    @classmethod
    def _strip(cls, raw: str) -> str:
        if not isinstance(raw, str):
            raise TypeError("username must be a string")
        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("username must not be empty")
        if len(cleaned) > 100:
            raise ValueError("username must be at most 100 characters")
        return cleaned

    def __str__(self) -> str:
        return self.value
