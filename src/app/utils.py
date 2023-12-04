from aiogram.types import CallbackQuery, Message

from app.database.service import get_users, get_user_role, get_all_requests, is_admin
import app.keyboards as kb

import logging
import sys

import pdb

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


async def update_user_list(chat):
    """ Function for updating user list and displaying it with inline buttons """

    users = await get_users()
    for user in users:
        menu = await kb.user_inline_keyboard(user=user)
        user_info = f"1. Имя: {user.name}\n 2. Отчество: {user.middle_name}\n3. Фамилия: {user.last_name}\n4. Роль: {user.role.name}"
        if isinstance(chat, CallbackQuery):
            await chat.message.answer(user_info, reply_markup=menu)
        elif isinstance(chat, Message):
            await chat.answer(user_info, reply_markup=menu)


async def update_requests_all_list(chat):
    """ Function for updating all requests with inline buttons """
    requests = await get_all_requests()
    for request in requests:
        # pdb.set_trace()
        media_files = [media.file_id for media in request.media]
        media_files_str = "\n".join(media_files)
        menu = await kb.request_inline_keyboard(request=request)
        date_str = request.date.strftime("%Y-%m-%d")
        request_info = f"Дата заявки: {request.date}\n" \
                       f"Адрес ПВЗ: {request.address.name}\nИмя инициатора: {request.user.name}\n" \
                       f"Отчество инициатора: {request.user.middle_name}\nФамилия инициатора: {request.user.last_name}\n" \
                       f"Сумма затрат: {request.summ}\nОписание затрат: {request.description}\n" \
                       f"Основание: {request.purpose}"
        if isinstance(chat, CallbackQuery):
            await chat.message.answer(request_info, reply_markup=menu)
        elif isinstance(chat, Message):
            await chat.answer(request_info, reply_markup=menu)


async def is_user_admin(chat, text, menu):
    """ Function for detecting admin right to some menu or action """

    if isinstance(chat, CallbackQuery):
        if await is_admin(chat.from_user.id):
            await chat.message.answer(text=text, reply_markup=menu)

    elif isinstance(chat, Message):
        if await is_admin(chat.from_user.id):
            await chat.answer(text=text, reply_markup=menu)


