from aiogram.filters import BaseFilter
from aiogram.types import Message


def _is_number(text: str) -> bool:
    try:
        float(text)  # Пробуем преобразовать текст в число с плавающей запятой
        return True
    except ValueError:
        return False  # Если возникает ошибка, значит текст не является числом


class IsDidgit(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return _is_number(message.text)  # Используем функцию для проверки
