from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from domain.user.model import NewUserData, UserModel
from domain.user.value_objects import Email, FullName, Username


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    external_id: int | None
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, user: UserModel) -> "UserResponse":
        return cls(
            id=int(user.id),
            external_id=int(user.external_id) if user.external_id is not None else None,
            first_name=user.name.first,
            last_name=user.name.last,
            email=user.email.value,
            username=user.username.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class CreateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str = Field(min_length=1, max_length=200)
    last_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    username: str = Field(min_length=1, max_length=100)

    def to_domain(self) -> NewUserData:
        return NewUserData(
            name=FullName(first=self.first_name, last=self.last_name),
            email=Email(value=self.email),
            username=Username(value=self.username),
        )


class UpdateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(default=None, min_length=1, max_length=200)
    last_name: str | None = Field(default=None, min_length=1, max_length=200)
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=1, max_length=100)

    def name_or_none(self) -> FullName | None:
        if self.first_name is None and self.last_name is None:
            return None
        if self.first_name is None or self.last_name is None:
            raise ValueError("first_name and last_name must be provided together")
        return FullName(first=self.first_name, last=self.last_name)

    def email_or_none(self) -> Email | None:
        return Email(value=self.email) if self.email is not None else None

    def username_or_none(self) -> Username | None:
        return Username(value=self.username) if self.username is not None else None
