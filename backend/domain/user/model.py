from datetime import datetime

from domain.entities import AggregateRoot, ValueObject
from domain.ids import ExternalUserID, UserID
from domain.user.value_objects import Email, FullName, Username


class UserModel(AggregateRoot):
    id: UserID
    external_id: ExternalUserID | None = None
    name: FullName
    email: Email
    username: Username
    created_at: datetime
    updated_at: datetime

    def rename(self, *, name: FullName, now: datetime) -> "UserModel":
        if name == self.name:
            return self
        return self.model_copy(update={"name": name, "updated_at": now})

    def change_email(self, *, email: Email, now: datetime) -> "UserModel":
        if email == self.email:
            return self
        return self.model_copy(update={"email": email, "updated_at": now})

    def change_username(self, *, username: Username, now: datetime) -> "UserModel":
        if username == self.username:
            return self
        return self.model_copy(update={"username": username, "updated_at": now})


class NewUserData(ValueObject):
    external_id: ExternalUserID | None = None
    name: FullName
    email: Email
    username: Username
