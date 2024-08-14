import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from filters.check_user_role import RoleFilter
from database.orm import AsyncORM
from keyboards.keyboards import create_keyboard
from lexicon.lexicon import ADMIN, GENERAL

router = Router()
# Проверка на простого пользователя
router.message.filter(RoleFilter(role='admin'))
router.callback_query.filter(RoleFilter(role='admin'))


# start, refresh
@router.message(CommandStart())
async def start_com(message: Message, db: AsyncORM):
    # Получаем баланс пользователя из базы данных
    balance, username = await db.check_balance_username(message.from_user.id)

    await message.answer(f'Привет, admin!\n\n'
                         f'<b>{GENERAL["text_balance"]}:</b> {format(balance, ".2f")}Р.',
                         reply_markup=create_keyboard('btn_expenses', 'btn_salary',
                                                      'btn_statistic', 'btn_view_users',
                                                      width=2, lexicon=ADMIN))
