import asyncio
import logging
import sys
from datetime import datetime
import pdb

from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto, InputMedia, ContentType as Ct, \
    InputMediaVideo, ReplyKeyboardMarkup, KeyboardButton
import app.keyboards as kb
from app.middlewares.media_middle_ware import MediaMiddleWare
from aiogram.fsm.context import FSMContext


from app.database.service import add_user, get_all_operations, get_all_addresses, add_media, get_user_by_tg_id, \
    update_media, add_request_with_user_id, get_requests_by_user_id
from app.keyboards.addresses_pagination import list_all_addresses
from app.keyboards.builders import inline_builder
from app.states import RequestCreate

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

router = Router()


@router.callback_query(F.data == "add_request")
async def add_request(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Для создании заявки на финансирование необходимо заполнить данные")
    type_operations = await get_all_operations()
    await callback.message.answer(text="Выберите тип операции", reply_markup=inline_builder(
        [operation.name for operation in type_operations],
        [f"set_operation_{operation.id}" for operation in type_operations]
    ))
    await state.set_state(RequestCreate.set_operation)
    await callback.answer()


@router.callback_query(F.data.startswith("set_operation_"))
async def set_operation(callback: CallbackQuery, state: FSMContext):
    operation_id = callback.data.split('_')[2]
    await state.update_data(type_id=operation_id)
    addresses = await get_all_addresses()
    menu = await list_all_addresses(addresses, page=1)
    await callback.message.answer(text="Выберите адрес ПВЗ:", reply_markup=menu)
    await callback.answer()
    await state.set_state(RequestCreate.set_address)


@router.callback_query(F.data.startswith("address_page_"))
async def process_address_pagination(callback: CallbackQuery, state: FSMContext):
    """handler for pagination addresess"""
    page = int(callback.data.split("_")[2])
    addresses = await get_all_addresses()
    menu = await list_all_addresses(addresses, page=page)
    await callback.message.edit_text(text="Выберите адрес ПВЗ:", reply_markup=menu)
    await callback.answer()


@router.callback_query(F.data.startswith("address_"))
async def set_address(callback: CallbackQuery, state: FSMContext):
    """Handler for setting request address"""
    address_id = callback.data.split('_')[1]
    await state.update_data(address_id=address_id)
    await callback.message.answer(text="Укажите необходимую сумму затрат\nПишем сумму фактических затрат, без учёта 6% ")
    await callback.answer()
    await state.set_state(RequestCreate.set_summ)


@router.message(RequestCreate.set_summ)
async def set_summ(message: Message, state: FSMContext):
    """Handler for setting sum of request"""
    user_input = message.text
    await state.update_data(tg_id=message.from_user.id)
    if not user_input.isdigit():
        await message.reply("Пожалуйста, введите только цифры.")
        return
    user_sum = int(user_input)
    await state.update_data(summ=user_sum)
    await message.answer(text="Укажите причину затрат")
    await state.set_state(RequestCreate.set_purpose)


@router.message(RequestCreate.set_purpose)
async def set_purpose(message: Message, state: FSMContext):
    """Handler for setting purpose of request"""
    user_purpose = message.text
    await state.update_data(purpose=user_purpose)
    await message.answer(text="Напишите подробное описание затрат")
    await state.set_state(RequestCreate.set_description)


@router.message(RequestCreate.set_description)
async def set_description(message: Message, state: FSMContext):
    """Handler for setting description of request"""
    user_description = message.text
    await state.update_data(description=user_description)
    state_data = await state.get_data()
    await message.answer("Сохранить заявку?", reply_markup=inline_builder(
        ["Да",  "Нет"],
        ["save_request", "main_page"]
    ))
    await state.set_state(RequestCreate.save_request)


@router.callback_query(F.data == "save_request")
# @router.message(RequestCreate.save_request)
async def save_request(callback: CallbackQuery, state: FSMContext):
    """Handler for saving request"""
    state_data = await state.get_data()
    user_id = state_data.get("tg_id")

    if user_id:
        user = await get_user_by_tg_id(tg_id=user_id)
        request_info = {
            "user_id": user.id,
            "date": datetime.today(),
            "type_id": state_data.get("type_id"),
            "status_id": 1,
            "address_id": state_data.get("address_id"),
            "summ": state_data.get("summ"),
            "description": state_data.get("description"),
            "purpose":  state_data.get("purpose")
        }
        request_id = await add_request_with_user_id(request_info)
        await callback.message.edit_text(text=f"Заявка №{request_id} сохранена", reply_markup=inline_builder(
            ["Назад в главное меню"],
            ["main_page"]
        ))
        await state.clear()
        await callback.answer()












































































































#
#
