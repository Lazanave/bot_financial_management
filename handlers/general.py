import logging
from datetime import datetime

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter, and_f, or_f
from FSM.fsm import AddTransition, FSMHelp
from database.orm import AsyncORM
from filters.input_validation import IsDidgit
from filters.balance_category_less_zero import LessZero
from lexicon.lexicon import ADMIN, USER, GENERAL
from keyboards.keyboards import create_keyboard, create_paginated_keyboard

router = Router()

logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'btn_back', ~StateFilter(default_state))
async def process_back(callback: CallbackQuery):
    await callback.answer()


# /help - default_state
@router.message(Command(commands='help'), StateFilter(default_state))
async def process_help_command_default(message: Message, state: FSMContext):
    await message.reply(text=GENERAL['/help'])
    await state.set_state(FSMHelp.view_help)


# /help - ~default_state
@router.message(Command(commands='help'), ~StateFilter(default_state))
async def process_help_command_not_default(message: Message):
    await message.reply(text=GENERAL['~help'])


""" ___ Кнопка Расход ___ """


# Нажимает на Расход
@router.callback_query(F.data == 'btn_expenses', StateFilter(default_state))
async def process_btn_expenses(callback: CallbackQuery, state: FSMContext, db: AsyncORM):
    uid = callback.from_user.id
    categories = await db.user_categories(uid)

    await callback.message.edit_text(
        text=GENERAL['text_select_category'],
        reply_markup=create_keyboard(*categories, last_button='btn_back', width=3)
    )

    await state.set_state(AddTransition.transaction_select_category)


# Выбирал категорию, предлагаем внести данные. Сумма
@router.callback_query(StateFilter(AddTransition.transaction_select_category))
async def process_expenses_write_digit(callback: CallbackQuery, state: FSMContext, db: AsyncORM):
    uid = callback.from_user.id
    category = callback.data

    await state.update_data(category=category)

    # Категории пользователя и их остатки
    category_balances = await db.category_balances(uid)
    # Забираем баланс категории
    category_balance = [c[1] for c in category_balances if category == c[0]]

    # Если баланс в категории = 0
    if category_balance[0] == 0:
        categories = await db.user_categories(uid)
        # Пробуем изменить текст
        try:
            await callback.message.edit_text(
                text=GENERAL['text_amount_is_zero'],
                reply_markup=create_keyboard(*categories, 'btn_salary_spread', last_button='btn_back', width=3)
            )
        # Если получили ошибку, то просто отвечаем на коллбек
        except TelegramBadRequest:
            await callback.answer()
    # Если не 0, то предлагаем ввести сумму расходов
    else:
        await callback.message.edit_text(
            text=f'<b>{category}: {category_balance[0]}Р.</b>\n\n'
                 f'{GENERAL["text_expenses_digit"]}',
            reply_markup=create_keyboard(last_button='btn_back')
        )
        # Переходим в состояние ввода чисел
        await state.set_state(AddTransition.transaction_expenses_digit)


""" ___ Кнопка Доход ___ """


# Нажимает на доход
@router.callback_query(F.data == 'btn_salary', StateFilter(default_state))
async def process_btn_salary(callback: CallbackQuery, state: FSMContext):
    # Предлагаем выбрать действие: добавить доход или распределить доход
    await callback.message.edit_text(
        text=GENERAL['text_choose_action'],
        reply_markup=create_keyboard('btn_salary_add', 'btn_salary_spread', width=2, last_button='btn_back')
    )

    await state.set_state(AddTransition.choose_action)


# >>> btn_salary_add - Добавить доход
@router.callback_query(F.data == 'btn_salary_add', StateFilter(AddTransition.choose_action))
async def process_btn_salary_add(callback: CallbackQuery, state: FSMContext):
    # Внести сумму дохода
    await callback.message.edit_text(
        text=GENERAL['text_writing_digit'],
        reply_markup=create_keyboard(last_button='btn_back')
    )

    await state.set_state(AddTransition.writing_digit)


# writing_digit - вводит число
@router.message(F.text, IsDidgit(), StateFilter(AddTransition.writing_digit))
async def process_salary_writing_digit(message: Message, state: FSMContext):
    # uid пользователя
    uid = message.from_user.id
    # сумма
    amount = float(message.text)

    await state.update_data(uid=uid, amount=amount)

    await message.reply(
        text=GENERAL['text_salary_writing_comment'],
        reply_markup=create_keyboard(last_button='btn_back')
    )

    await state.set_state(AddTransition.writing_comment)


# writing_digit - вводит НЕ число\НЕ текст
@router.message(StateFilter(AddTransition.writing_digit))
async def process_salary_writing_not_digit(message: Message, state: FSMContext):
    await message.reply(
        text=GENERAL['text_writing_digit'],
        reply_markup=create_keyboard(last_button='btn_back')
    )


# writing_comment - ввод комментария
@router.message(F.text, StateFilter(AddTransition.writing_comment))
async def process_salary_writing_comment(message: Message, state: FSMContext, db: AsyncORM):
    # Получаем записанные значения
    user_data = await state.get_data()
    uid = user_data['uid']          # uid
    amount = user_data['amount']    # сумма
    description = message.text      # описание

    try:
        await db.update_balance_salary(uid=uid, amount=amount, description=description)
        await message.answer(text=GENERAL['text_refresh'])
    except Exception as e:
        logging.error('Error', exc_info=e)
        return

    await state.clear()


# >>> Распределить доход - btn_salary_spread
@router.callback_query(F.data == 'btn_salary_spread', StateFilter(AddTransition.choose_action))
async def process_btn_salary_spread(callback: CallbackQuery, state: FSMContext, db: AsyncORM):
    uid = callback.from_user.id
    categories = await db.user_categories(uid)

    await callback.message.edit_text(
        text=GENERAL['text_select_category'],
        reply_markup=create_keyboard(*categories, last_button='btn_back', width=3)
    )

    await state.set_state(AddTransition.select_category)


# Пользователь выбрал категорию
@router.callback_query(StateFilter(AddTransition.select_category))
async def process_btn_salary_select_category(callback: CallbackQuery, state: FSMContext, db: AsyncORM):
    uid = callback.from_user.id
    category = callback.data

    await state.update_data(category=category)

    category_balances = await db.category_balances(uid)
    category_balance = [c[1] for c in category_balances if category == c[0]]
    balance, _ = await db.check_balance_username(uid)

    await callback.message.edit_text(
        text=f'<b>{GENERAL["text_balance"]}:</b> {format(balance, ".2f")}Р.\n'
             f'<b>Баланс в категории {category}:</b> {format(category_balance[0], ".2f")}Р.\n\n'
             f'{GENERAL["text_spread_digit"]}',
        reply_markup=create_keyboard(last_button='btn_back')
    )

    await state.set_state(AddTransition.income_digit)


# Пользователь вводит число
@router.message(and_f(F.text, IsDidgit(), ~LessZero()), StateFilter(AddTransition.income_digit))
async def process_text_spread_is_digit(message: Message, state: FSMContext, db: AsyncORM):
    user_data = await state.get_data()
    category = user_data['category']
    uid = message.from_user.id
    amount = float(message.text)

    try:
        await db.update_category_balance(uid, amount, category)

        await message.answer(
            text=f'Баланс категории <b>{category}</b> изменён.\n'
                 f'Обновите данные - /refresh'
        )
    except Exception:
        logging.error('Error')

    await state.clear()


# Пользователь вводит НЕ число, НЕ текст
@router.message(StateFilter(AddTransition.income_digit))
async def process_text_spread_is_digit(message: Message, state: FSMContext, db: AsyncORM):
    await message.reply(
        text=GENERAL['text_spread_digit'],
        reply_markup=create_keyboard(last_button='btn_back')
    )


""" ___ Кнопка Статистика ___ """

""" ___ Кнопка Пользователи ___ """
