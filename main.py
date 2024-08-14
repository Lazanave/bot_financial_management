import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import user
from aiogram.fsm.storage.redis import RedisStorage, Redis


# Функция конфигурирования и запуска бота
async def main() -> None:

    logging.getLogger('aiogram').setLevel(logging.ERROR)

    # Форматируем логгер
    logging.basicConfig(
        level=logging.INFO,
        format='[{asctime}] #{levelname:8} {filename}:'
               '{lineno} - {name} - {message}',
        style='{'
    )

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем Redis
    r = Redis(host="localhost")
    storage = RedisStorage(redis=r)

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(storage=storage)

    # Регистриуем роутеры в диспетчере
    dp.include_router(user.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    logger.info('Starting bot...')
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info('Bot started')
    await dp.start_polling(bot)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped gracefully.")
