import logging
import pdb


from aiogram import Router, F
from aiogram.filters import CommandStart, Command

from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.database.service import get_user_role, get_users, get_user_by_id, delete_user_by_id, get_roles
from app.states import UserRoleState, AdminMenu, UserCreate
from aiogram.fsm.context import FSMContext

from app.utils import send_message_by_username

router = Router()

user_data = {}


@router.message(F.text.lower() == 'пользователи')
async def show_users(message: Message, state: FSMContext):
    """ Handler for button  Users"""
    user_state = await state.get_data()
    user_role = user_state.get('role')
    if user_role == 'Администратор':
        await message.answer('Список пользователей', reply_markup=kb.users_menu)
        await update_user_list(message)
    else:
        await message.answer('У вас нет доступа к данному меню')


@router.message(F.text.lower() == 'назад')
async def main_admin_menu(message: Message, state: FSMContext):
    """ Handler for back button """
    user_state = await state.get_data()
    user_role = user_state.get('role')
    menu = await kb.get_menu(user_role)
    await message.answer(text='Главное меню', reply_markup=menu)


@router.callback_query(F.data.startswith("delete_user_"))
async def delete_user(callback: CallbackQuery):
    """ Handler for deleting user """
    user_id = callback.data.split('delete_user_')[1]
    user = await get_user_by_id(user_id)
    if user:
        menu = await kb.confirmation(user)
        await callback.message.answer(f'Вы уверены, что хотите удалить пользователя {user.name}?',
                                      reply_markup=menu)
    else:
        await callback.message.answer(f'Пользователь {user.name} не найден!')
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_user_"))
async def confirm_delete_user(callback: CallbackQuery):
    """ Handler for confirmation User """
    user_id = callback.data.split('delete_user_')[1]
    user = await get_user_by_id(user_id)
    if user:
        await delete_user_by_id(user_id)
        await callback.message.answer(f'Пользователь {user.name} удален')
        # update users list
        await callback.message.answer(text="Список пользователей")
        await update_user_list(callback)
    else:
        await callback.message.answer(f'Пользователь не найден!')
    await callback.answer()


@router.callback_query(F.data.startswith("cancel_delete_user_"))
async def cancel_delete_user(callback: CallbackQuery):
    """ Handler for reject deleting User """
    await callback.message.answer("Удаление отменено")
    await update_user_list(callback)
    await callback.answer()





@router.message(F.text.lower() == 'добавить пользователя')
async def show_users(message: Message, state: FSMContext):
    """ Handler for adding User """
    user_state = await state.get_data()
    user_role = user_state.get('role')
    if user_role == 'Администратор':
        await message.answer(text='Укажите имя пользователя')
        await state.set_state(UserCreate.set_name)
    else:
        await message.answer('У вас нет доступа к данному меню')


@router.callback_query(F.data.startswith("role_id_"))
async def select_user_role(callback: CallbackQuery, state: FSMContext):
    """ Handler for selecting user Role at user adding """
    role_id = callback.data.split('role_id_')[1]
    await state.update_data(role_id=role_id)
    await callback.message.answer(text="Введите имя пользователя в Телеграм в формате @Username")
    await state.set_state(UserCreate.set_telegramm_id)
    await callback.answer()


@router.message(UserCreate.set_telegramm_id)
async def send_invitation_to_user(message: Message, state: FSMContext):
    """ Handler for getting Telegram username """
    username = message.text
    text = "Вас приветствует бот для создания заявок. " \
           "Администратор бота добавил вас как пользователя, подтвердите пожалуйста"
    menu = await kb.user_invitation()
    await send_message_by_username(username=username, text=text, reply_markup=menu)


@router.callback_query(F.data.startswith("user_accept"))
async def handler_user_accept(callback: CallbackQuery, state: FSMContext):
    """ Handler for getting Telegramm ID of the User when User confirm"""
    telegram_id = callback.from_user.id
    await state.update_data(tg_id=telegram_id)
    print(f'User {callback.from_user.username} is confirmed')
    await state.set_state(UserCreate.confirmation)



# @router.message(UserCreate.set_role)
# async def set_role(message: Message, state: FSMContext):
#     """ Handler for choosing role of the user"""
#     roles = await get_roles()
#     # pdb.set_trace()
#     menu = await kb.list_all_roles(roles)
#     await message.answer(text="Выберите роль пользователя", reply_markup=menu)
#     await state.set_state(UserCreate.set_telegramm_id)


# @router.callback_query(F)
# async def back_to_main_menu_admin(callback: CallbackQuery,
#                                   callback_data: kb.MenuCallbackFactory):
#
#     await callback.message.answer('Back to main menu')
    # tg_id = callback.from_user.id
    # user_role = await get_user_role(tg_id)
    # if user_role:
    #     main_menu_keyboard = await kb.get_menu(user_role)
    #     await callback.message.answer("Главное меню", reply_markup=main_menu_keyboard)
    # else:
    #     await callback.message.answer("Ошибка: неизвестная роль пользователя.")


# @router.callback_query(F.text == 'Пользователи')
# async def show_users(callback: CallbackQuery):
#     tg_id = callback.from_user.id
#     user_role = user_states.get(tg_id)
#     if user_role == 'admin':
#         users_markup = await kb.users()
#         await callback.message.answer('Список пользователей:', reply_markup=users_markup)
#     else:
#         await callback.message.answer('У вас нет доступа к списку пользователей.')



    # @router.message(F.text == 'Пользователи')
# async def users(message: Message):
#     await message.answer('Выберите пользователя', reply_markup=await kb.users())


# @router.callback_query(F.data.startswith('user_'))
# async def user_selected(callback: CallbackQuery):
#     user_id = callback.data.split('_')[1]
#     await callback.message.answer(f'Вы выбрали пользователя {user_id}')
#     markup = await kb.requests(user_id)
#     await callback.answer('Выбрано!')
#     await callback.message.answer('Заявки пользователя:', reply_markup=markup)

#
# @router.message(F.text == 'Заявки')
# async def users(message: Message):
#     await message.answer('Выберите заявку пользовател', reply_markup=await kb.requests())






