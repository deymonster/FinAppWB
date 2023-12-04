import logging
import sys
import pdb

from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.media_group import MediaGroupBuilder

import app.keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType

import config
from app.database.service import add_user, get_address_by_id, get_all_media_by_request_id, get_request_by_id, \
    get_all_operations, \
    update_request, get_operation_by_id, get_all_addresses, delete_request, get_director
from app.keyboards.addresses_pagination import list_all_addresses
from app.keyboards.builders import inline_builder
from app.notify.notify_utils import notify_user_test
from app.states import UserRegister
from app.database import models
from app.states import EditRequest

from bot import bot

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

router = Router()


@router.callback_query(F.data.startswith("edit_request_"))
async def edit_request(callback: CallbackQuery, state: FSMContext) -> None:
    request_id = callback.data.split('_')[2]
    request = await get_request_by_id(request_id=request_id)
    await state.update_data(request=request)

    await callback.message.answer(f"Выберите что хотите изменить в заявке от {request.date}", reply_markup=inline_builder(
        ["Тип операции", "Адрес", "Сумма затрат", "Причина затрат", "Описание затрат",
         "Медиа заявки",  "◀ Назад к заявкам"],
        ["select_type", "select_address", "select_text_summ", "select_text_purpose", "select_text_description",
         f"media_request_{request_id}", "requests"]
    ))
    await callback.answer()


@router.callback_query(F.data.startswith("delete_request_"))
async def select_request_to_delete(callback: CallbackQuery) -> None:
    request_id = callback.data.split('_')[2]
    request = await get_request_by_id(request_id=request_id)
    await callback.message.answer(f"Вы действительно хотите удалить заявку №{request.id}?", reply_markup=inline_builder(
        ["Да", "Отмена"],
        [f"confirm_delete_request_{request.id}", f"edit_request_{request.id}"]
    ))


@router.callback_query(F.data.startswith("confirm_delete_request_"))
async def confirm_delete_request(callback: CallbackQuery) ->None:
    request_id = callback.data.split('_')[3]
    await delete_request(request_id=request_id)
    await callback.message.answer("Заявка удалена!", reply_markup=inline_builder(
        ["◀️ Назад"],
        ["requests"]
    ))


@router.callback_query(F.data == "select_type")
async def edit_type(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    request = data.get("request")
    operations = await get_all_operations()
    await callback.message.answer(f"Текущий тип операции - {request.type.name}", reply_markup=inline_builder(
        [operation.name for operation in operations],
        [f"update_type_{operation.id}" for operation in operations]
    ))
    await callback.answer()


@router.callback_query(F.data.startswith("update_type_"))
async def update_type(callback: CallbackQuery, state: FSMContext) -> None:
    operation_id = callback.data.split('_')[2]
    operation = await get_operation_by_id(operation_id=operation_id)
    data = await state.get_data()
    request = data.get("request")
    request_data = {"type_id": operation_id}
    await update_request(request_id=request.id, request_data=request_data)
    await callback.message.answer(f"Тип операции изменен на {operation.name}", reply_markup=inline_builder(
        ["◀ Назад к заявкам"],
        [f"requests"]
    ))
    await callback.answer()


@router.callback_query(F.data == "select_address")
async def edit_address(callback: CallbackQuery, state: FSMContext) -> None:
    # data = await state.get_data()
    # request = data.get("request")
    addresses = await get_all_addresses()
    menu = await list_all_addresses(addresses, page=1, update=True)
    await callback.message.answer(text="Выберите адрес ПВЗ:", reply_markup=menu)
    await callback.answer()


@router.callback_query(F.data.startswith("update_address_"))
async def set_address(callback: CallbackQuery, state: FSMContext):
    """Handler for updating request address"""
    data = await state.get_data()
    request = data.get("request")
    address_id = callback.data.split('_')[2]
    request_data = {"address_id": address_id}
    address = await get_address_by_id(address_id)
    await update_request(request_id=request.id, request_data=request_data)
    await callback.message.answer(f"Адрес изменен на {address.name}", reply_markup=inline_builder(
        ["◀ Назад к заявкам"],
        [f"requests"]
    ))
    await callback.answer()


@router.callback_query(F.data.startswith("update_address_page_"))
async def process_address_pagination(callback: CallbackQuery, state: FSMContext):
    """handler for pagination addresess"""
    page = int(callback.data.split("_")[3])
    addresses = await get_all_addresses()
    menu = await list_all_addresses(addresses, page=page, update=True)
    await callback.message.edit_text(text="Выберите адрес ПВЗ:", reply_markup=menu)
    await callback.answer()


@router.callback_query(F.data.startswith('select_text_'))
async def select_sum(callback: CallbackQuery, state: FSMContext):
    attribute = callback.data.split('select_text_')[1]
    data = await state.get_data()
    request = data.get("request")
    name_attribute = {
        "summ": "суммы",
        "purpose": "причины",
        "description": "описания"
    }
    await callback.message.answer(
        f"Текущее значение {name_attribute.get(attribute)} заявки - {getattr(request, attribute)}")
    await callback.message.answer(f"Введите новое значение для {name_attribute.get(attribute)}")
    await state.set_state(getattr(EditRequest, attribute))
    await callback.answer()


@router.message(EditRequest.summ)
@router.message(EditRequest.purpose)
@router.message(EditRequest.description)
async def update_attribute(message: Message, state: FSMContext):
    new_value = message.text
    current_state = await state.get_state()
    attribute = current_state.split(':')[1]
    request_data = {attribute: new_value}
    data = await state.get_data()
    request = data.get("request")
    await state.update_data(request_data=request_data)
    await state.set_state(current_state)
    await message.answer("Сохранить изменения?", reply_markup=inline_builder(
        ["Сохранить", "Отмена"],
        ["confirm_update_request", f"edit_request_{request.id}"]
    ))


@router.callback_query(F.data == 'confirm_update_request')
async def confirm_update_request(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    request = data.get('request')
    request_data = data.get('request_data')
    await update_request(request_id=request.id, request_data=request_data)
    await state.clear()
    await callback.message.edit_text('Изменения сохранены', reply_markup=inline_builder(
        ["Меню редактирования заявки"],
        [f"edit_request_{request.id}"]
    ))
    await callback.answer()


@router.callback_query(F.data.startswith("send_request_"))
async def send_request(callback: CallbackQuery) -> None:
    request_id = callback.data.split('_')[2]
    request = await get_request_by_id(request_id=request_id)
    if request.status_id == 2:
        await callback.message.answer("Заявка уже отправлена на рассмотрение")
    # TODO обработка других статусов - рассмотреть различные варианты
    else:
        request_data = {"status_id": "2"}
        await update_request(request_id=request.id, request_data=request_data)
        await callback.message.answer(f"Заявка №{request_id} отправлена на рассмотрение")
        director = await get_director()
        if director:
            await notify_user_test(user_id=director.tg_id, text=config.REQUEST_NEW)
    await callback.answer()


@router.callback_query(F.data.startswith("media_request_"))
async def get_media_request(callback: CallbackQuery, state: FSMContext, user: models.User = None) -> None:
    # pdb.set_trace()
    state_data = await state.get_data()
    current_user = state_data.get('current_user')
    request_id = callback.data.split('_')[2]
    all_media = await get_all_media_by_request_id(request_id=request_id)
    media_group = MediaGroupBuilder(caption="Фото заявки")
    for media in all_media:
        media_group.add(type="photo", media=media.file_id, disable_content_type_detection=True)
    await callback.message.answer_media_group(media=media_group.build(), protect_content=True)
    await callback.message.answer(text="Назад", reply_markup=inline_builder(
        ["Главное меню" if current_user.role_id == config.DIRECTOR_ROLE_ID else "Заявки"],
        ["main_page" if current_user.role_id == config.DIRECTOR_ROLE_ID else "requests"]
    ))
    await callback.answer()

