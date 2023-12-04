from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message
from app.database.service import get_users, get_all_requests, get_user_role
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from typing import Optional
from aiogram.filters.callback_data import CallbackData


class MenuCallbackFactory(CallbackData, prefix="menu"):
    action: str
    value: Optional[int] = None


# admin_menu = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Пользователи')],
#     [KeyboardButton(text='Заявки')]
# ], resize_keyboard=True, input_field_placeholder='Выберите нужный пункт')


manager_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заявки')]
], resize_keyboard=True)

director_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заявки')]
], resize_keyboard=True)

accountant_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заявки')]
], resize_keyboard=True)


admin_inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Пользователи", callback_data="users"),

            InlineKeyboardButton(text="Заявки", callback_data="requests"),

        ],
        [
            InlineKeyboardButton(text="Добавить пользователя", callback_data="add_user"),
            InlineKeyboardButton(text="Добавить заявку", callback_data="add_request"),
        ]
    ])

manager_inline_menu = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить заявку", callback_data="add_request"),

            InlineKeyboardButton(text="Заявки", callback_data="requests"),

        ]
    ])

director_inline_menu = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Новые заявки", callback_data="new_requests")

        ],
        [
            InlineKeyboardButton(text="Одобренные заявки", callback_data="confirmed_requests")

        ],
        [
            InlineKeyboardButton(text="Отклоненные заявки", callback_data="rejected_requests")
        ]

    ])

accountant_inline_menu = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Одобренные заявки", callback_data="new_requests")

        ]

    ])

main_inline_menu = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Главное меню", callback_data="main_menu")

        ]

    ])


async def get_menu(user_role):
    if user_role == 'Администратор':
        return admin_inline_kb
    elif user_role == 'Менеджер':
        return manager_inline_menu
    elif user_role == 'Директор':
        return director_inline_menu
    elif user_role == 'Бухгалтер':
        return accountant_inline_menu
    else:
        return None


back_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начало")],
        ],
        resize_keyboard=True
    )

add_back_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Назад")], [KeyboardButton(text="Добавить заявку")]
        ],
        resize_keyboard=True
    )


async def list_all_operation(operations):
    buttons = []
    for operation in operations:
        button = InlineKeyboardButton(text=f"{operation.name}",
                                      callback_data=f"operation_type_{operation.id}")
        buttons.append([button])
    operation_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return operation_keyboard


async def list_all_addresses(addresses, page=1, items_per_page=10):
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    current_addresses = addresses[start_index:end_index]
    buttons = []
    for address in current_addresses:
        button = InlineKeyboardButton(text=f"{address.name}",
                                      callback_data=f"address_{address.id}")
        buttons.append([button])
    pagination_buttons = []
    if start_index > 0:
        prev_button = InlineKeyboardButton(text="<< Пред.", callback_data=f"address_page_{page - 1}")
        pagination_buttons.append(prev_button)
    if end_index < len(addresses):
        next_button = InlineKeyboardButton(text="След. >>", callback_data=f"address_page_{page + 1}")
        pagination_buttons.append(next_button)
    buttons.append(pagination_buttons)
    addresses_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return addresses_keyboard


async def user_inline_keyboard(user):
    buttons = [
        [
            InlineKeyboardButton(text="Изменить", callback_data=f"edit_user_{user.id}"),
            InlineKeyboardButton(text="Удалить", callback_data=f"delete_user_{user.id}")
        ]
    ]
    user_inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return user_inline_kb


# async def request_inline_keyboard(request):
#     buttons = [
#         [
#             InlineKeyboardButton(text="Изменить заявку", callback_data=f"edit_request_{request.id}"),
#             InlineKeyboardButton(text="Удалить заявку", callback_data=f"delete_request_{request.id}"),
#             InlineKeyboardButton(text="Медиа заявки", callback_data=f"media_request_{request.id}"),
#             InlineKeyboardButton(text="Отравить заявку", callback_data=f"send_request_{request.id}"),
#         ]
#     ]
#     request_inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return request_inline_kb


async def confirmation(user):
    buttons = [
        [
            InlineKeyboardButton(text="Да", callback_data=f"confirm_delete_user_{user.id}"),
            InlineKeyboardButton(text="Нет", callback_data=f"cancel_delete_user_{user.id}")
        ]
    ]
    confirm_delete_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return confirm_delete_keyboard



async def list_all_roles(roles):
    buttons = []
    for role in roles:
        button = InlineKeyboardButton(text=f"Роль - {role.name}", callback_data=f"role_id_{role.id}")
        buttons.append([button])
    roles_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return roles_keyboard



async def confirm_register():
    buttons = [
        [
            InlineKeyboardButton(text="Зарегистрироваться", callback_data=f"confirm_register_user"),
            InlineKeyboardButton(text="Отмена", callback_data=f"cancel_register_user")
        ]
    ]
    confirm_register_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return confirm_register_keyboard


# async def confirm_info():
#     buttons = [
#         [
#             InlineKeyboardButton(text="Все верно!", callback_data=f"confirm_info"),
#             InlineKeyboardButton(text="Отмена", callback_data=f"cancel_info")
#         ]
#     ]
#     confirm_info_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return confirm_info_keyboard


confirm_info = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Все верно!"),
             KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True
    )
