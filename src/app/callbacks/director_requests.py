from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

import config
from app.database.service import get_users, get_all_requests, get_user_by_tg_id, get_requests_by_user_id, \
    get_requests_with_status, update_request, get_request_by_id
from app.keyboards.builders import inline_builder
import pdb

from app.notify.notify_utils import notify_user_test
from app.states import UpdateStatusRequest

router = Router()


@router.callback_query(F.data == "new_requests")
@router.callback_query(F.data == "confirmed_requests")
@router.callback_query(F.data == "rejected_requests")
async def get_requests(callback: CallbackQuery, state: FSMContext) -> None:
    request_type = callback.data.split('_')[0]
    # pdb.set_trace()
    status = {"new": 2,
              "confirmed": 3,
              "rejected": 4,
              "paid": 5
              }
    requests = await get_requests_with_status(status_id=status.get(request_type))
    if not requests:
        new_requests_text = "Заявок пока нет, при появлении новых заявок вы получите уведомление"
        other_requests_text = "Заявок пока нет"
        await callback.message.answer(new_requests_text if request_type == "new" else other_requests_text)
        await callback.answer()
    for request in requests:
        request_info = f"Номер заявки: {request.id}\n" \
                       f"Дата заявки: {request.date}\n" \
                       f"Тип операции: {request.type.name}\n" \
                       f"Сумма заявки: {request.summ}\n" \
                       f"Адрес ПВЗ: {request.address.name}\n" \
                       f"Имя инициатора: {request.user.name}\n" \
                       f"Отчество инициатора: {request.user.middle_name}\n" \
                       f"Фамилия инициатора: {request.user.last_name}\n" \
                       f"Статус заявки: {request.status.name}\n" \
                       f"Адреc: {request.address.name}\n" \
                       f"Описание: {request.description}\n" \
                       f"Цель: {request.purpose}"
        buttons = []
        if request.status_id == status["confirmed"]:
            buttons = ["Одобрить заявку", "Отклонить заявку", "Просмотр медиа заявки"]
            callbacks = [f"confirm_request_{request.id}", f"reject_request_{request.id}", f"media_request_{request.id}"]
        else:
            buttons = ["Просмотр медиа заявки"]
            callbacks = [f"media_request_{request.id}"]
        await callback.message.answer(request_info, reply_markup=inline_builder(
            buttons,
            callbacks,
        ))
        await callback.answer()
    await callback.message.answer("Меню", reply_markup=inline_builder(
        ["◀️ Назад в заявки", "Главное меню"],
        [
            {
                    "new": "new_requests",
                    "confirmed": "confirmed_requests",
                    "rejected": "rejected_requests"
            }.get(request_type),
            "main_page"
        ]
    ))


@router.callback_query(F.data.startswith("confirm_request_"))
async def get_requests(callback: CallbackQuery, state: FSMContext) -> None:
    request_id = int(callback.data.split('_')[2])
    # pdb.set_trace()
    request_data = {"status_id": "3"}
    current_request = await get_request_by_id(request_id=request_id)
    await notify_user_test(user_id=current_request.user.id, text=f"Заявка №{current_request.id} одобрена")
    await update_request(request_id=request_id, request_data=request_data)
    await callback.answer()
    await callback.message.answer("Заявка обработана", reply_markup=inline_builder("◀️ Назад", "new_requests"))


@router.callback_query(F.data.startswith("reject_request_"))
async def get_requests(callback: CallbackQuery, state: FSMContext) -> None:
    request_id = int(callback.data.split('_')[2])
    await state.update_data(request_id=request_id)
    await callback.message.answer("Укажите комментарий к отклоенной заявке", reply_markup=inline_builder(
        ["Отмена"],
        ["rejected_requests"]
    ))
    await state.set_state(UpdateStatusRequest.set_comment)
    await callback.answer()


@router.message(UpdateStatusRequest.set_comment)
async def process_reject_comment(message: Message, state: FSMContext):
    state_data = await state.get_data()
    request_id = state_data.get('request_id')
    comment = message.text
    request_data = {"status_id": "4", "comment": comment}
    current_request = await get_request_by_id(request_id=request_id)
    await notify_user_test(user_id=current_request.user.id, text=f"Заявка №{current_request.id} "
                                                                 f"отклонена со следующей причине - "
                                                                 f"{current_request.comment}")
    await update_request(request_id=request_id, request_data=request_data)
    await state.clear()
    await message.answer("Заявка обработана", reply_markup=inline_builder("◀️ Назад", "rejected_requests"))





