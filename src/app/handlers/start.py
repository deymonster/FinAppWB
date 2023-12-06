import logging
import os

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import config
from app.database.service import get_user_role, get_user_by_tg_id
from app.keyboards.builders import inline_builder
from app.states import UserRoleState

import app.keyboards as kb
import pdb

router = Router()


@router.message(CommandStart())
@router.callback_query(F.data == "main_page")
async def start(message: Message | CallbackQuery, state: FSMContext):
    """ Handler for /start command

    """

    tg_id = message.from_user.id
    current_user = await get_user_by_tg_id(tg_id=tg_id)
    await state.update_data(current_user=current_user)

    # pdb.set_trace()
    if current_user:
        if current_user.role_id == config.ADMIN_ROLE_ID:

            pattern = dict(
                text='Главное меню',
                reply_markup=inline_builder(
                    ["👤 Пользователи", " 💰Заявки", "➕ Добавить заявку"],
                    ["users", "requests", "add_request"]
                )
            )
            if isinstance(message, CallbackQuery):
                await message.message.edit_text(**pattern)
                await message.answer()
            else:
                await message.answer(**pattern)
        if current_user.role_id == config.MANAGER_ROLE_ID:
            pattern = dict(
                text='Главное меню',
                reply_markup=inline_builder(
                    [" 💰Заявки", "➕ Добавить заявку"],
                    ["requests",  "add_request"]
                )
            )
            if isinstance(message, CallbackQuery):
                await message.message.edit_text(**pattern)
                await message.answer()
            else:
                await message.answer(**pattern)
        if current_user.role_id == config.DIRECTOR_ROLE_ID:
            pattern = dict(
                text='Главное меню',
                reply_markup=inline_builder(
                    [" 🆕 💰Новые заявки", "👌 💰Одобренные заявки", "⛔️ 💰 Отклоненные заявки"],
                    ["new_requests",  "confirmed_requests", "rejected_requests"]
                )
            )
            if isinstance(message, CallbackQuery):
                await message.message.edit_text(**pattern)
                await message.answer()
            else:
                await message.answer(**pattern)

        if current_user.role_id == config.ACCOUNTANT_ROLE_ID:
            pattern = dict(
                text='Главное меню',
                reply_markup=inline_builder(
                    ["👌 💰Одобренные заявки"],
                    ["confirmed_requests"]
                )
            )
            if isinstance(message, CallbackQuery):
                await message.message.edit_text(**pattern)
                await message.answer()
            else:
                await message.answer(**pattern)
        if current_user.role_id == config.DEFAULT_ROLE_ID:
            await message.answer('Ваша учетная запись еще не подтверждена!')

    else:
        await message.answer('Вы не зарегистрованы в системе. Вы можете пройти регистрацию. '
                             'После подтверждения регистрации вы получите уведомление', reply_markup=inline_builder(
                                    ["Зарегистрироваться", "Отмена"],
                                    ["confirm_register_user", "main_page"]
                                )
                             )
