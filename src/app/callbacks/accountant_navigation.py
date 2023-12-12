from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.notify.notify_utils import notify_user_test, send_csv
from app.states import GetConfirmedRequestsByDate
import config
from app.database.service import get_requests_with_status
from dateutil.parser import parse

router = Router()


@router.callback_query(F.data == "get_confirmed_requests")
async def get_requests_for_acccountant(callback: CallbackQuery, state: FSMContext) -> None:
    """Handler for confirmed requests for accountant"""
    await state.set_state(GetConfirmedRequestsByDate.get_start_date)
    await callback.message.edit_text("Введите начальную дату в формате YYYY-MM-DD")
    await callback.answer()
    # confirmed_requests = await get_requests_with_status(status_id=config.CONFIRMED_REQUEST_STATUS)


@router.message(GetConfirmedRequestsByDate.get_start_date)
async def get_start_date(message: Message, state: FSMContext):
    """Hander for getting start date from user"""
    input_date = message.text
    try:
        start_date = parse(input_date)
    except ValueError:
        await message.answer(f"Неверный формат даты - {input_date}")
        return
    # pdb.set_trace()
    await state.update_data(start_date=start_date)
    await message.answer(text="Введите конечyю дату в формате YYYY-MM-DD")
    await state.set_state(GetConfirmedRequestsByDate.get_end_date)


@router.message(GetConfirmedRequestsByDate.get_end_date)
async def get_start_date(message: Message, state: FSMContext):
    """Hander for getting end date from user"""
    input_date = message.text
    data = await state.get_data()
    start_date = data.get('start_date')
    current_user = data.get('current_user')
    try:
        end_date = parse(input_date)
    except ValueError:
        await message.answer(f"Неверный формат даты - {input_date}")
        return
    # pdb.set_trace()
    all_confirmed_requests = await get_requests_with_status(status_id=config.CONFIRMED_REQUEST_STATUS,
                                                            start_date=start_date, end_date=end_date)

    if all_confirmed_requests:
        await send_csv(chat_id=current_user.tg_id, requests=all_confirmed_requests)
    else:
        await message.answer("Заявок в выбранный период нет")

