from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

import config
from app.database.service import get_users, get_all_requests, get_user_by_tg_id, get_requests_by_user_id
from app.keyboards.builders import inline_builder
import pdb

router = Router()


@router.callback_query(F.data == "users")
async def get_all_users(callback: CallbackQuery) -> None:
    users = await get_users()
    for user in users:

        status = "Подтвержденный" if user.confirmed_status else "Неподтвержденный"
        user_info = f"Имя: {user.name} \n" \
                    f"Отчество: {user.middle_name} \n" \
                    f"Фамилия: {user.last_name} \n" \
                    f"Роль: {user.role.name} \n\n" \
                    f"Статус: {status}"
        await callback.message.answer(user_info, reply_markup=inline_builder(
            ["Изменить", "Удалить"],
            [f"edit_user_{user.id}", f"delete_user_{user.id}"]
        ))
        await callback.answer()
    await callback.message.answer("Главное меню", reply_markup=inline_builder("◀️ Назад", "main_page"))


@router.callback_query(F.data == "requests")
async def get_requests(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    current_user = data.get("current_user")
    # pdb.set_trace()
    if current_user.role_id == config.ADMIN_ROLE_ID:
        requests = await get_all_requests()
    else:
        requests = await get_requests_by_user_id(user_id=current_user.id)
    if not requests:
        await callback.message.edit_text("Заявок пока нет, мы можете создать заявку из главного меню")
        await callback.answer()
    for request in requests:
        request_info = f"Номер заявки: {request.id}\n" \
                    f"Дата заявки: {request.date}\n" \
                    f"Тип операции: {request.type.name}\n"\
                    f"Сумма заявки: {request.summ}\n" \
                    f"Адрес ПВЗ: {request.address.name}\n" \
                    f"Имя инициатора: {request.user.name}\n" \
                    f"Отчество инициатора: {request.user.middle_name}\n" \
                    f"Фамилия инициатора: {request.user.last_name}\n" \
                    f"Статус заявки: {request.status.name}\n" \
                    f"Адреc: {request.address.name}"
        await callback.message.answer(request_info, reply_markup=inline_builder(
            ["Изменить", "Удалить", "Отправить на рассмотрение"],
            [f"edit_request_{request.id}", f"delete_request_{request.id}", f"send_request_{request.id}"]
        ))
        await callback.answer()
    await callback.message.answer("Главное меню", reply_markup=inline_builder("◀️ Назад", "main_page"))





