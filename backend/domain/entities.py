from pydantic import BaseModel, ConfigDict


class ValueObject(BaseModel):
    model_config = ConfigDict(frozen=True, validate_assignment=True)


class Entity(BaseModel):
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)


class AggregateRoot(Entity):
    pass
