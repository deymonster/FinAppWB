import logging
import pdb

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from app.database.service import get_user_role, get_users, get_user_by_id, delete_user_by_id, get_roles
from aiogram.fsm.context import FSMContext

from app.utils import update_user_list, update_requests_all_list, is_user_admin

router = Router()


@router.message(F.text.lower() == 'пользователи')
async def show_users(message: Message):
    """ Handler for button  Users"""
    await is_user_admin(chat=message, text='Список пользователей', menu=kb.back_menu)
    await update_user_list(message)


@router.callback_query(F.data.startswith("users"))
async def get_users(callback: CallbackQuery):
    """ Handler for callback to get all users """
    await callback.message.answer(text="Список всех пользователей")
    await update_user_list(callback)
    await callback.answer()


# @router.callback_query(F.data.startswith("edit_user_"))
# async def handler_user_accept(callback: CallbackQuery):
#     """ Handler for editting user info """
#     user_id = callback.data.split('_')[1]
#     user = await get_user_by_id(user_id=user_id)
#     await is_user_admin(chat=callback, text=f"Редактирование пользователя {user.name}")
#     await callback.answer()


@router.callback_query(F.data.startswith("delete_user_"))
async def handler_user_accept(callback: CallbackQuery, state: FSMContext):
    """ Handler for deleting user  """
    user_id = callback.data.split('_')[1]
    user = await get_user_by_id(user_id=user_id)
    await is_user_admin(chat=callback, text=f"Удаление пользователя {user.name}")
    await callback.answer()


@router.message(F.text.lower() == 'заявки')
async def show_all_requests(message: Message):
    """ Handler for button Requests for administrator """
    await is_user_admin(chat=message, text='Список заявок', menu=kb.add_back_menu)
    await update_requests_all_list(message)


