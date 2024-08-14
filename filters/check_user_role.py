from aiogram.filters import BaseFilter
from aiogram.types import Message
from database.orm import AsyncORM


class RoleFilter(BaseFilter):
    role: str

    def __init__(self, role: str):
        self.role = role

    async def __call__(self, message: Message, db: AsyncORM) -> bool:
        is_admin = await db.is_admin(message.from_user.id)
        return (self.role == 'admin' and is_admin) or (self.role == 'user' and not is_admin)
