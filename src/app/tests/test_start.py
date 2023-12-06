import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types import User
from aiogram.types import Chat

import config
# from app.database.models import User as DBUser


class MockedMessage(Message):
    def __init__(self,
                 chat: Chat = None,
                 message_id: int = 0,
                 date: int = 0,
                 text: str = None,
                 **kwargs):
        user = User(id=123, is_bot=False, first_name="TestUser")
        chat = chat or Chat(id=123, type="private", first_name="TestUser")
        super().__init__(
            message_id=message_id,
            date=date,
            chat=chat,
            from_user=user,
            text=text,
            **kwargs
        )


class MockedCallbackQuery(CallbackQuery):
    def __init__(self, data: str, from_user_id: int = 1):
        user = User(id=from_user_id,  is_bot=False, first_name="TestUser")
        chat_instance = "test_chat_instance"
        super().__init__(id="test_id", data=data, chat_instance=chat_instance, from_user=user)


@pytest.mark.asyncio
async def test_administrator_role():
    # Создание пользователя с ролью администратора
    user_with_admin_role = DBUser(role_id=config.ADMIN_ROLE_ID)
    mocked_message = MockedMessage(text='/start', from_user_id=user_with_admin_role.tg_id)
    # Имитация сообщения от пользователя
    await start(mocked_message, FSMContext())  # Передача сообщения обработчику /start
    # Добавьте здесь проверки, которые вам нужны для этой роли


@pytest.mark.asyncio
async def test_manager_role():
    # Создание пользователя с ролью менеджера
    user_with_manager_role = User(role_id=config.MANAGER_ROLE_ID)
    mocked_message = MockedMessage(text='/start', from_user_id=user_with_manager_role.tg_id)
    # Имитация сообщения от пользователя
    await start(mocked_message, FSMContext())  # Передача сообщения обработчику /start
    # Добавьте здесь проверки, которые вам нужны для этой роли
