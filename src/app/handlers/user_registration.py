import logging
import sys
import pdb

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
import app.keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType

from app.database.service import add_user, get_admins
from app.keyboards.builders import inline_builder
from app.notify.notify_utils import notify_user_test
from app.states import UserRegister


from bot import bot
from config import USERS

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

router = Router()


@router.callback_query(F.data.startswith("confirm_register_user"))
async def start_user_register(callback: CallbackQuery, state: FSMContext):
    """ Handler for begin user registration BEGIN"""

    await callback.message.edit_text(text="Укажите свое имя")
    await state.set_state(UserRegister.set_name)
    await callback.answer()


@router.message(UserRegister.set_name)
async def set_name(message: Message, state: FSMContext):
    """ Handler for setting username """
    # pdb.set_trace()
    await state.update_data(name=message.text)
    await message.answer(text="Теперь укажите ваше отчество")
    await state.set_state(UserRegister.set_middle_name)


@router.message(UserRegister.set_middle_name)
async def set_middle_name(message: Message, state: FSMContext):
    """ Handler for setting middle_name """

    await state.update_data(middle_name=message.text)

    await message.answer(text="Теперь укажите вашу фамилию")
    await state.set_state(UserRegister.set_last_name)


@router.message(UserRegister.set_last_name)
async def set_last_name(message: Message, state: FSMContext):
    """ Handler for setting last name """

    await state.update_data(last_name=message.text)
    user_info = await state.get_data()
    tg_id = message.from_user.id
    await state.update_data(tg_id=tg_id)
    await message.answer(text="Подтвердите введенные данные")
    await message.answer(f"Имя - {user_info['name']}\nОтчество - {user_info['middle_name']}"
                         f"\nФамилия - {user_info['last_name']} ", reply_markup=inline_builder(
                            ["Все верно", "Отмена"],
                            ["confirm_user_data", "main_page"]
                            ))


@router.callback_query(F.data == "confirm_user_data")
async def save_user(callback: CallbackQuery, state: FSMContext):
    user_info = await state.get_data()
    # pdb.set_trace()
    await add_user(tg_id=user_info['tg_id'], name=user_info['name'], middle_name=user_info['middle_name'],
                   last_name=user_info['last_name'], role_id=5)
    all_admins = await get_admins()
    for user in all_admins:
        await notify_user_test(user_id=user.tg_id, text=f"Зарегистрирован новый пользователь - {user_info['name']}")

    await callback.message.edit_text(text="Данные сохранены", reply_markup=inline_builder(
        ["Главное меню"],
        ["main_page"]
    ))
    await state.clear()
    await callback.answer()





























