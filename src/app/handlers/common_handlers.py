from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from app.database.service import get_user_role, get_users, get_user_by_id, delete_user_by_id, get_roles
from app.states import UserRoleState
from aiogram.fsm.context import FSMContext

from app.utils import update_user_list, update_requests_all_list

router = Router()


@router.message(F.text.lower() == 'назад')
async def main_admin_menu(message: Message, state: FSMContext):
    """ Handler for back button """
    tg_id = message.from_user.id
    user_role = await get_user_role(tg_id)
    menu = await kb.get_menu(user_role)
    await message.answer(text='Главное меню', reply_markup=menu)