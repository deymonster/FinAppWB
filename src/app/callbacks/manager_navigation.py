# from aiogram import Router, F
# from aiogram.types import CallbackQuery
#
#
# from app.database.service import get_requests_by_user_id, get_user_by_tg_id
# from app.keyboards.builders import inline_builder
#
# router = Router()
#
#
# @router.callback_query(F.data == "requests")
# async def get_requests(callback: CallbackQuery) -> None:
#     tg_id = callback.message.from_user.id
#     user = await get_user_by_tg_id(tg_id=tg_id)
#     requests = await get_requests_by_user_id(user_id=user.id)
#     if not requests:
#         await callback.message.edit_text("Заявок пока нет, мы можете создать заявку из главного меню")
#         await callback.answer()
#     for request in requests:
#         request_info = f"Дата заявки: {request.date}\n" \
#                        f"Тип операции: {request.type.name}\n" \
#                        f"Сумма заявки: {request.summ}\n" \
#                        f"Адрес ПВЗ: {request.address.name}\n" \
#                        f"Имя инициатора: {request.user.name}\n" \
#                        f"Отчество инициатора: {request.user.middle_name}\n" \
#                        f"Фамилия инициатора: {request.user.last_name}\n" \
#                        f"Статус заявки: {request.status.name}\n" \
#                        f"Адреc: {request.address.name}"
#         await callback.message.answer(request_info, reply_markup=inline_builder(
#             ["Изменить", "Удалить", "Отправить на рассмотрение"],
#             [f"edit_request_{request.id}", f"delete_request_{request.id}", f"send_request_{request.id}"]
#         ))
#         await callback.answer()
#     await callback.message.answer("Главное меню", reply_markup=inline_builder("◀️ Назад", "main_page"))
