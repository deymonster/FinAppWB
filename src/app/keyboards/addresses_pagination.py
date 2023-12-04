from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def list_all_addresses(addresses, page=1, items_per_page=10, update=None):
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    current_addresses = addresses[start_index:end_index]
    buttons = []
    for address in current_addresses:
        if not update:
            button = InlineKeyboardButton(text=f"{address.name}",
                                          callback_data=f"address_{address.id}")
            buttons.append([button])
        else:
            button = InlineKeyboardButton(text=f"{address.name}",
                                          callback_data=f"update_address_{address.id}")
            buttons.append([button])
    pagination_buttons = []
    if start_index > 0:
        if not update:
            prev_button = InlineKeyboardButton(text="<< Пред.", callback_data=f"address_page_{page - 1}")
        else:
            prev_button = InlineKeyboardButton(text="<< Пред.", callback_data=f"update_address_page_{page - 1}")
        pagination_buttons.append(prev_button)
    if end_index < len(addresses):
        if not update:
            next_button = InlineKeyboardButton(text="След. >>", callback_data=f"address_page_{page + 1}")
        else:
            next_button = InlineKeyboardButton(text="След. >>", callback_data=f"update_address_page_{page + 1}")
        pagination_buttons.append(next_button)
    buttons.append(pagination_buttons)
    addresses_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return addresses_keyboard
