import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

router = Router()


@router.message(CommandStart())
async def start_com(message: Message):
    await message.answer('Hi')


@router.message()
async def end_com(message: Message):
    await message.answer('Bye')
