from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.service import get_user_by_id, update_user, get_roles, get_role_by_id
from app.keyboards.builders import inline_builder
from app.states import EditUser

import pdb

router = Router()


@router.callback_query(F.data.startswith('edit_user_'))
async def edit_user(callback: CallbackQuery, state: FSMContext):
    user_id = callback.data.split('_')[2]
    user = await get_user_by_id(user_id=user_id)
    await state.update_data(user=user)
    status = "Подтвержденный" if user.confirmed_status else "Неподтвержденный"

    await callback.message.answer("Выберите что хотите изменить", reply_markup=inline_builder(
        [f"Имя - {user.name}", f"Отчество - {user.middle_name}", f"Фамилия - {user.last_name}",
          f"Роль - {user.role.name}", f"Статус - {status}", " ◀ Назад в главное меню"],
        ["сhoose_name", "сhoose_middle_name",
         "choose_last_name", "edit_role",
         "edit_status", "main_page"]
    ))
    await callback.answer()


@router.callback_query(F.data.startswith('сhoose_'))
async def choose_edit(callback: CallbackQuery, state: FSMContext):
    # pdb.set_trace()
    attribute = callback.data.split('сhoose_')[1]
    name_attribute = {
        "name": "имени",
        "middle_name": "отчества",
        "last_name": "фамилии"
    }
    data = await state.get_data()
    user = data.get('user')
    await callback.message.answer(f"Текущее значение {name_attribute.get(attribute)} пользователя - {getattr(user, attribute)}")
    await callback.message.answer(f"Введите новое значение для {name_attribute.get(attribute)}")
    await state.set_state(getattr(EditUser, attribute))
    await callback.answer()


@router.message(EditUser.name)
@router.message(EditUser.middle_name)
@router.message(EditUser.last_name)
async def set_attribute(message: Message, state: FSMContext):
    # pdb.set_trace()
    new_value = message.text
    current_state = await state.get_state()
    attribute = current_state.split(':')[1]
    user_data = {attribute: new_value}
    data = await state.get_data()
    user = data.get('user')
    await state.update_data(user_data=user_data)
    await state.set_state(current_state)
    await message.answer("Сохранить изменения?", reply_markup=inline_builder(
        ["Сохранить", "Отмена"],
        ["confirm_update_user", f"edit_user_{user.id}"]
    ))


@router.callback_query(F.data == 'confirm_update_user')
async def confirm_update_user(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data.get('user')
    user_data = data.get('user_data')
    await update_user(user_id=user.id, user_data=user_data)
    await state.clear()
    await callback.message.edit_text('Изменения сохранены', reply_markup=inline_builder(
        ["Меню редактирования"],
        [f"edit_user_{user.id}"]
    ))
    await callback.answer()


@router.callback_query(F.data == 'edit_role')
async def edit_role_user(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data.get('user')
    user = await get_user_by_id(user_id=user.id)
    await callback.message.edit_text(f"Текущая роль пользователя - {user.role.name}")
    await state.set_state(EditUser.role)
    roles = await get_roles()
    await callback.message.answer("Выберите роль пользователя", reply_markup=inline_builder(
        [role.name for role in roles],
        [f"set_role_{role.id}" for role in roles]
    ))
    await callback.answer()


@router.callback_query(F.data.startswith('set_role_'))
async def set_role_user(callback: CallbackQuery, state: FSMContext):
    role_id = callback.data.split('_')[2]
    data = await state.get_data()
    user = data.get('user')
    role = await get_role_by_id(role_id=role_id)
    if user:
        user_data = {"role_id": role_id, "confirmed_status": True}
        await update_user(user_id=user.id, user_data=user_data)
        await callback.message.answer(f"Роль пользователя изменена на {role.name}", reply_markup=inline_builder(
            ["Меню редактирования"],
            [f"edit_user_{user.id}"]
        ))
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith('edit_status'))
async def confirm_user(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data.get('user')
    user = await get_user_by_id(user_id=user.id)
    status = "Подтвержденный" if user.confirmed_status else "Неподтвержденный"
    await callback.message.edit_text(f"Текущий статус пользователя - {status}")
    await callback.message.answer("Подтвердить регистрацию пользователя", reply_markup=inline_builder(
        ["Подтверить", "Отмена"],
        ["confirm_status_user", f"edit_user_{user.id}"]
    ))
    await callback.answer()


@router.callback_query(F.data == "confirm_status_user")
async def update_status_user(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data.get('user')
    user = await get_user_by_id(user_id=user.id)
    user_data = {
        "confirmed_status": True
    }
    await update_user(user_id=user.id, user_data=user_data)
    await callback.message.edit_text("Статус пользователя изменена на подтвержденный", reply_markup=inline_builder(
        ["Меню редактирования"],
        [f"edit_user_{user.id}"]
    ))
    await callback.answer()
