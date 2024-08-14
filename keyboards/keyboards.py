import logging

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import GENERAL


# Функция для добавления кнопок в билдер клавиатуры с заданной шириной
def add_buttons_to_builder(kb_builder: InlineKeyboardBuilder, buttons: list, width: int, lexicon: dict) -> None:
    # Проходим по кнопкам и добавляем их в строки по ширине
    for i in range(0, len(buttons), width):
        row_buttons = buttons[i:i + width]
        kb_builder.row(*[
            InlineKeyboardButton(
                text=lexicon.get(button, button),
                callback_data=button
            ) for button in row_buttons
        ])


# Функция для создания обычной клавиатуры
def create_keyboard(*buttons: str, last_button: str = None, width: int = 1, lexicon: dict = GENERAL) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()  # Инициализируем билдер клавиатуры
    add_buttons_to_builder(kb_builder, buttons, width, lexicon=lexicon)  # Добавляем кнопки

    # Добавляем последнюю кнопку, если она есть
    if last_button:
        kb_builder.row(InlineKeyboardButton(
            text=lexicon.get(last_button, last_button),
            callback_data=last_button
        ))

    return kb_builder.as_markup()  # Возвращаем готовую клавиатуру


# Функция для создания пагинированной клавиатуры
def create_paginated_keyboard(buttons: list, current_page: int, total_pages: int, width: int = 2) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()  # Инициализируем билдер клавиатуры

    # Определяем кнопки для текущей страницы
    start = (current_page - 1) * 8
    end = start + 8
    page_buttons = buttons[start:end]

    add_buttons_to_builder(kb_builder, page_buttons, width)  # Добавляем кнопки для текущей страницы

    navigation_buttons = []
    # Добавляем кнопку "Назад" если это не первая страница
    if current_page > 1:
        navigation_buttons.append(InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data=f'page_{current_page - 1}'
        ))

    # Добавляем кнопку с номером текущей страницы
    navigation_buttons.append(InlineKeyboardButton(
        text=f'{current_page}/{total_pages}',
        callback_data='current_page'
    ))

    # Добавляем кнопку "Вперед" если это не последняя страница
    if current_page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(
            text='Вперед ➡️',
            callback_data=f'page_{current_page + 1}'
        ))

    kb_builder.row(*navigation_buttons)  # Добавляем кнопки навигации в строку

    kb_builder.row(InlineKeyboardButton(
        text='Назад',
        callback_data='back'
    ))  # Добавляем кнопку "Назад" для возврата

    return kb_builder.as_markup()  # Возвращаем готовую клавиатуру
