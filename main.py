import config, logging, psycopg2, functions, random, os, datetime
from weather import getweather
from pathlib import Path
from stt import STT
from config import bot_token, db_name, db_user, db_password, db_host
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)
logfile = str(datetime.date.today()) + '.log' # формируем имя лог-файла

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

hello = types.MenuButtonCommands(text='test')
stt = STT()

# ------Старт-----
@dp.message_handler(commands=["start"], regexp="/")
async def start_command(message: types.Message):
    await message.answer("Привет")

# ------Погода-----
@dp.message_handler(commands=["weather"], regexp="/")
async def weather(message: types.Message):
    await message.answer(getweather())


# ------Игра-----
@dp.message_handler(commands=["smb_rules"], regexp="/")
async def smb_rules(message: types.Message):
    await message.answer("Правила игры кто-то Дня:\n1. Зарегистрируйтесь в игру по команде /smbreg\n"
                         "2. Подождите пока зарегистрируются все (или большинство)\n3. Запустите розыгрыш по команде /smb\n"
                         "4. Просмотр статистики канала по команде /smbstats\n \nВажно, розыгрыш проходит только раз в день, повторная команда выведет результат игры.\n \n"
                         "Сброс розыгрыша происходит каждый день в 12 часов ночи по UTC+2 (примерно в два часа ночи по Москве)")

@dp.message_handler(commands=["smb_reg"], regexp="/")
async def smb_reg(message: types.Message):
    reg_text=functions.reg(message)
    await message.answer(reg_text)


@dp.message_handler(commands=["smb"], regexp="/")
async def smb(message: types.Message):
    output_message=functions.smb(message)
    await message.answer(output_message)

@dp.message_handler(commands=["smb_stats"], regexp="/")
async def smb_stats(message: types.Message):
    stats=functions.stats (message)
    await message.answer(f"Топ кого-то за все время:\n {stats[0]}Всего участников - {stats[1]}")


# ------Перевод-----
@dp.message_handler(content_types=[types.ContentType.VOICE, types.ContentType.AUDIO, types.ContentType.DOCUMENT])
async def voice_message_handler(message: types.Message):
    if message.content_type == types.ContentType.VOICE:
        file_id = message.voice.file_id
    elif message.content_type == types.ContentType.AUDIO:
        file_id = message.audio.file_id
    elif message.content_type == types.ContentType.DOCUMENT:
        file_id = message.document.file_id
    else:
        await message.reply("Формат документа не поддерживается")
        return
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"{file_id}.tmp")
    await bot.download_file(file_path, destination=file_on_disk)
    text = stt.audio_to_text(file_on_disk)
    if not text:
        text = "Формат документа не поддерживается"
    await message.answer(text)
    os.remove(file_on_disk)  # Удаление временного файла


# ------Модер-----
@dp.message_handler(content_types=[types.ContentType.TEXT, types.ContentType.CONTACT])
async def moder(message: types.Message):
    text = message.text.lower()
    for word in config.words:
        if word in text:
            await message.delete()

if __name__ == '__main__':
    executor.start_polling(dp)
