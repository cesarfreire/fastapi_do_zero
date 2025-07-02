from http import HTTPStatus

from fastapi import HTTPException


class TodoNotFoundException(HTTPException):
    def __init__(self, detail: str = 'Todo not found'):
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail=detail,
        )
