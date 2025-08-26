from pydantic import BaseModel, field_validator, ValidationError

from errors import HttpError


class BaseAnnouncementRequest(BaseModel):
    '''Базовый класс'''
    headline: str
    description: str
    owner: str

    # Декоратор валидации на пустотое поле
    @classmethod
    @field_validator("headline", "description", "owner")
    def not_empty(cls, value: str):
        if not value or not value.strip():
            raise ValueError("Данное поле не должно быть пустым!")
        return value.strip() if value is not None else value


class CreateAnnouncementRequest(BaseAnnouncementRequest):
    '''Описание, как должен выглядеть запрос на СОЗДАНИЕ объявления'''
    pass


class UpdateAnnouncementRequest(BaseAnnouncementRequest):
    '''Описание, как должен выглядеть запрос на ОБНОВЛЕНИЕ объявления'''
    headline: str | None = None
    description:  str | None = None
    owner:  str | None = None


'''Функция ВАЛИДАЦИИ данных объекта со СХЕМОЙ'''
def validate(
        schema: type[CreateAnnouncementRequest | UpdateAnnouncementRequest],
        json_data: dict
    ) -> dict:

    try:
        schema_instance = schema(**json_data)
        return schema_instance.model_dump(exclude_unset=True)
    except ValidationError as err:
        errors = err.errors()
        for error in errors:
            error.pop("ctx", None)
        raise HttpError(status_code=400, message=errors)


