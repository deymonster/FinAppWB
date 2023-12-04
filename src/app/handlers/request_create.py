import asyncio
import logging
import sys
from datetime import datetime
import pdb

from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto, InputMedia, ContentType as Ct, \
    InputMediaVideo
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

# @router.callback_query(F.data.startswith("operation_type_"))
# async def select_type_operation(callback: CallbackQuery, state: FSMContext):
#     """Handler for selecting operation type"""
#     operation_id = callback.data.split('_')[2]
#     await state.update_data(type_id=operation_id)
#     # pdb.set_trace()
#     addresses = await get_all_addresses()
#     menu = await list_all_addresses(addresses, page=1)
#     await callback.message.answer(text="Выберите адрес ПВЗ:", reply_markup=menu)
#     await callback.answer()
#     await state.set_state(RequestCreate.set_address)


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
    await message.answer(text="Прикрепите фото/видео материалы к заявке")
    await state.set_state(RequestCreate.set_media)


@router.message(RequestCreate.set_media)
async def get_media_from_user(message: Message, state: FSMContext, album: list[Message] = None):
    """Handler for user media files"""
    # pdb.set_trace()
    content_types = [types.ContentType.PHOTO, types.ContentType.VIDEO]
    if message.content_type in content_types:
        media_group = []
        # album = [message]  # Преобразовать сообщение в список для обработки одиночного файла
        # await process_media(album, state, message)
        if album:
            for msg in album:
                if msg.photo:
                    file_id = msg.photo[-1].file_id
                    media_group.append(InputMediaPhoto(media=file_id))
                elif msg.video:
                    file_id = msg.video.file_id
                    media_group.append(InputMediaVideo(media=file_id))
        else:
            if message.photo:
                file_id = message.photo[-1].file_id
                media_group.append(InputMediaPhoto(media=file_id))
            elif message.video:
                file_id = message.video[-1]
                media_group.append(InputMediaVideo(media=file_id))
    media_ids = await asyncio.gather(*[add_media(file_id=file.media) for file in media_group])
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
        for media_id in media_ids:
            await update_media(media_id=media_id, request_id=request_id)
        await message.answer(text="Заявка сохранена", reply_markup=inline_builder(
            ["Назад в главное меню"],
            ["main_page"]
        ))
        await state.clear()
    else:
        await message.answer(text="Необходимо прикрепить медиа файлы")


async def process_media(album: list[Message], state: FSMContext, message: Message):
    """Process media files"""
    media_group = []
    for msg in album:
        if msg.photo:
            file_id = msg.photo[-1].file_id
            media_group.append(InputMediaPhoto(media=file_id))
        elif msg.video:
            file_id = msg.video.file_id
            media_group.append(InputMediaVideo(media=file_id))
    media_ids = await asyncio.gather(*[add_media(file_id=file.media) for file in media_group])
    state_data = await state.get_data()
    user_id = state_data.get("tg_id")
    # pdb.set_trace()
    # Создание заявки с прикрепленными медиафайлами
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
        # pdb.set_trace()
        # Создание заявки в базе данных и прикрепление медиафайлов к ней
        request_id = await add_request_with_user_id(request_info)
        for media_id in media_ids:
            await update_media(media_id=media_id, request_id=request_id)
        await message.answer(text="Заявка сохранена", reply_markup=inline_builder(
            ["Назад в главное меню"],
            ["main_page"]
        ))
        await state.clear()


# @router.message(RequestCreate.set_media)
# async def set_media(message: Message, state: FSMContext):
#     """Handler for setting media for request"""
#     media_group_id = message.media_group_id









# @router.message(RequestCreate.set_address)
# async def select_address(message: Message, state: FSMContext):
#     """Handler for selecting address"""
#     await message.answer(text="Выберите адрес ПВЗ")
#     addresses = await get_all_addresses()
#     menu = await kb.list_all_operation(addresses)


#
# @router.callback_query(F.data.startswith("confirm_register_user"))
# async def start_user_register(callback: CallbackQuery, state: FSMContext):
#     """ Handler for begin user registration BEGIN"""
#
#     await callback.message.answer(text="Укажите свое имя")
#     await state.set_state(UserRegister.set_name)
#     await callback.answer()
#
#
# @router.message(UserRegister.set_name)
# async def set_name(message: Message, state: FSMContext):
#     """ Handler for setting username """
#
#     await state.update_data(name=message.text)
#     await message.answer(text="Теперь укажите ваше отчество")
#     await state.set_state(UserRegister.set_middle_name)
#
#
# @router.message(UserRegister.set_middle_name)
# async def set_middle_name(message: Message, state: FSMContext):
#     """ Handler for setting middle_name """
#
#     await state.update_data(middle_name=message.text)
#     await message.answer(text="Теперь укажите вашу фамилию")
#     await state.set_state(UserRegister.set_last_name)
#
#
# @router.message(F.text.lower() == 'все верно!')
# async def confirm_info(message: Message, state: FSMContext):
#     """ Handler for confirm user info """
#     logging.info(f"Handler for button confirm")
#     user_info = await state.get_data()
#     tg_id = message.from_user.id
#     await add_user(tg_id=tg_id, name=user_info['name'], middle_name=user_info['middle_name'],
#                    last_name=user_info['last_name'], role_id=5)
#     await message.answer(text="Данные сохранены", reply_markup=ReplyKeyboardRemove())
#     await state.clear()
#
#
# @router.message(F.text.lower() == 'отмена!')
# async def confirm_info(message: Message, state: FSMContext):
#     """ Handler for cnacel user info """
#     logging.info(f'handler for cancel here')
#     await message.answer(text='Регистрация отменена')
#     await state.clear()
#
#
# @router.message(UserRegister.set_last_name)
# async def set_last_name(message: Message, state: FSMContext):
#     """ Handler for setting last name """
#
#     await state.update_data(last_name=message.text)
#     await message.answer(text="Подтвердите введенные данные")
#     user_info = await state.get_data()
#     logging.info(f'Set last name - User info - {user_info}')
#     menu = kb.confirm_info
#     await message.answer(f"Имя - {user_info['name']}\nОтчество - {user_info['middle_name']}"
#                          f"\nФамилия - {user_info['last_name']} ", reply_markup=menu)
#
#
