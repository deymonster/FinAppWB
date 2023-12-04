from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


admin_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Пользователи')],
    [KeyboardButton(text='Заявки')]
], resize_keyboard=True, input_field_placeholder='Выберите нужный пункт')

users_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Назад"), KeyboardButton(text="Добавить пользователя")],

], resize_keyboard=True, input_field_placeholder='Выберите нужный пункт')


