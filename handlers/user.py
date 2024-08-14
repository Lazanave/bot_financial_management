import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter, and_f, or_f
from filters.check_user_db import user_in_db
from filters.check_user_role import RoleFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State
from database.orm import AsyncORM
from keyboards.keyboards import create_keyboard
from FSM.fsm import FSMUsername
from lexicon.lexicon import USER, GENERAL

router = Router()
# Проверка на простого пользователя
router.message.filter(RoleFilter(role='user'))
router.callback_query.filter(RoleFilter(role='user'))


# start / refresh
@router.message(user_in_db,
                or_f(CommandStart(), Command('refresh')),
                or_f(~StateFilter(default_state), StateFilter(default_state)))
async def start_user_in_db(message: Message, state: FSMContext, db: AsyncORM):
    await state.clear()
    uid = message.from_user.id

    # Получаем баланс пользователя из базы данных
    balance, username = await db.check_balance_username(uid)
    # Категории пользователя и их остатки
    category_balances = await db.category_balances(uid)
    # Создаём текст с категорией и её остатком
    category_text = '\n'.join([f'<b>{category}:</b> {balance}Р.' for category, balance in category_balances])

    await message.answer(f'<b>{GENERAL["text_balance"]}:</b> {format(balance, ".2f")}Р.\n\n'
                         f'{category_text}',
                         reply_markup=create_keyboard('btn_expenses', 'btn_salary',
                                                      'btn_statistic', 'btn_view_users',
                                                      last_button='btn_settings', width=2))


# Первый запуск
@router.message(CommandStart(), StateFilter(default_state))
async def start_user_not_in_db_not_username(message: Message, state: FSMContext, db: AsyncORM):
    await message.answer(text=GENERAL['text_writing_username'])
    await state.set_state(FSMUsername.username_write)


# Пользователь вводит username
@router.message(F.text, StateFilter(FSMUsername.username_write))
async def user_writing_username(message: Message, state: FSMContext, db: AsyncORM):
    uid = message.from_user.id
    username = message.text

    # Добавляем в базу данных
    await db.insert_user(uid, username)
    await db.add_category(uid, ['Еда', 'ЖКХ', 'Прочее'])

    await message.answer(text=GENERAL['/help'])

    await state.clear()


# Пользователь отправляет не текст
@router.message(~F.text, StateFilter(FSMUsername.username_write))
async def user_writing_not_username(message: Message):
    await message.reply(text=GENERAL['text_writing_username'])





