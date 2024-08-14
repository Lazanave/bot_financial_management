from aiogram.types import Message
from database.orm import AsyncORM


async def user_in_db(message: Message, db: AsyncORM) -> bool:
    user_id = message.from_user.id
    return await db.user_in_db(user_id)
