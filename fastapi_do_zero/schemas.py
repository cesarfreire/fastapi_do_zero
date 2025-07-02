from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fastapi_do_zero.models import TodoState


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublicSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserListSchema(BaseModel):
    users: list[UserPublicSchema]


class JWTToken(BaseModel):
    access_token: str  # O token JWT
    token_type: str  # O tipo do token, geralmente "bearer"


class FilterParams(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=0, default=100)


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoPublicSchema(TodoSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class TodoListSchema(BaseModel):
    todos: list[TodoPublicSchema]


class TodoUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None


class FilterTodoParams(FilterParams):
    title: str | None = Field(None, min_length=3, max_length=20)
    description: str | None = Field(None, min_length=3, max_length=20)
    state: TodoState | None = None
