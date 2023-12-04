from bot import bot
import pdb


async def notify_user_test(user_id, text):
    # bot = bot_context.get()
    # chat = await bot.get_chat(user_id)
    # await bot.send_message(chat_id=chat.id, text=f"You registration is confirmed by admin!")
    try:

        await bot.send_message(user_id, text=text)
    except Exception as e:
        print(f"Failed to send message to user {user_id}: {e}")




