import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message
from database.orm import AsyncORM


async def _less_zero(amount: float, balance: float) -> bool:

    return balance - amount < 0.0


class LessZero(BaseFilter):
    async def __call__(self, message: Message, db: AsyncORM) -> bool:
        uid = message.from_user.id
        balance, _ = await db.check_balance_username(uid)
        return await _less_zero(float(message.text), balance)  # Используем функцию для проверки
