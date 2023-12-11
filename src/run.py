import asyncio
import logging
import sys
import contextvars

from aiogram import Dispatcher


# from app.handlers import router
# from app.handlers import user_registration
from app.handlers import user_registration, start, admin_handlers, common_handlers, request_create
from app.middlewares.media_middle_ware import MediaMiddleWare
from bot import bot

from app.database.models import async_main
from app.callbacks import admin_navigation, users_action, requests_action, director_requests, accountant_navigation


# Создаем переменную контекста для хранения экземпляра бота
# bot_context = contextvars.ContextVar('bot')

dp = Dispatcher()
# dp.include_router(router)
dp.message.middleware(MediaMiddleWare())
dp.include_routers(
    start.router,
    user_registration.router,
    admin_navigation.router,
    users_action.router,
    admin_handlers.router,
    common_handlers.router,
    request_create.router,
    requests_action.router,
    director_requests.router,
    accountant_navigation.router)
# bot_context.set(bot)


async def main():
    # bot_instance = bot_context.get()
    await async_main()
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot_instance.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('GoodBye!')
