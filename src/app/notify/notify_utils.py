from bot import bot
import pdb
import csv
import io
from aiogram.types import BufferedInputFile, InputFile


async def notify_user_test(user_id, text):
    # bot = bot_context.get()
    # chat = await bot.get_chat(user_id)
    # await bot.send_message(chat_id=chat.id, text=f"You registration is confirmed by admin!")
    try:

        await bot.send_message(user_id, text=text)
    except Exception as e:
        print(f"Failed to send message to user {user_id}: {e}")


async def send_csv(chat_id: int | str, requests: list):
    output = io.StringIO()
    writer = csv.DictWriter(output,
                            fieldnames=["№ заявки", "Ф.И.О", "Дата", "Тип операции", "Статус", "Адрес ПВЗ", "Сумма", "Описание"])
    writer.writeheader()
    for request in requests:
        writer.writerow({
            "№ заявки": request.id,
            "Ф.И.О": f"{request.user.last_name} {request.user.name[0]}. {request.user.middle_name[0]}.",
            "Дата": request.date.strftime("%Y-%m-%d"),
            "Тип операции": request.type.name,
            "Статус": request.status.name,
            "Адрес ПВЗ": request.address.name,
            "Сумма": request.summ,
            "Описание": request.description
        })
    output.seek(0)
    buf = io.BytesIO()

    # extract csv-string, convert it to bytes and write to buffer
    buf.write(output.getvalue().encode())
    buf.seek(0)

    # set a filename with file's extension
    buf.name = f'confirmed_requests.csv'
    bytes_data = buf.getvalue()
    # Создание объекта BufferedInputFile из буфера BytesIO
    buffered_input_file = BufferedInputFile(file=bytes_data, filename=buf.name)
    # pdb.set_trace()
    await bot.send_document(chat_id, document=buffered_input_file)




