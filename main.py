from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import sqlite3
from aiogram.dispatcher.filters.state import State, StatesGroup
import random
import asyncio
import string
import json
import aiohttp

help_chat = -919023328

bot = Bot(token='5843422546:AAEzI0mp90UjdEJb-7kc0TXQsWKAnIonQwk')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class states(StatesGroup):
    help = State()
    changecookies = State()

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER, username TEXT, cookie TEXT DEFAULT 0)")
cursor.execute("CREATE TABLE IF NOT EXISTS help (user_id INTEGER, msg_id INTEGER)")

mainkeyboard = ReplyKeyboardMarkup(resize_keyboard=True)
mainkeyboard.add(KeyboardButton("💎 Премиум"), KeyboardButton("❓ Какие лимитки мы поймали"), KeyboardButton("📔 Наш ТГК"))
mainkeyboard.add(KeyboardButton("🍪 Мой куки"), KeyboardButton("📝 Отзывы"))
mainkeyboard.add(KeyboardButton("🛠 Поддержка"), KeyboardButton("❓ FAQ"))
mainkeyboard.add(KeyboardButton("👨‍💻 GitHub"))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (message.from_user.id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (message.from_user.id, message.from_user.username))
        conn.commit()
        await message.reply("<b>Это бот по ловле UGC лимиток!</b>", parse_mode="HTML", reply_markup=mainkeyboard)
    await message.reply("<b>⬇️ Главное меню ⬇️</b>", parse_mode="HTML", reply_markup=mainkeyboard)

@dp.message_handler(content_types=types.ContentTypes.TEXT, text="💎 Премиум")
async def prem(message: types.Message):
    await message.reply("<b>Бот бесплатный :) Премиум подписок пока-что нет</b>", parse_mode="HTML", reply_markup=mainkeyboard)

@dp.message_handler(content_types=types.ContentTypes.TEXT, text="📔 Наш ТГК")
async def TGK(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="📔 Ссылка", url="https://t.me/aiogrammader"))
    await message.reply("📔 Наш ТГК", parse_mode="HTML", reply_markup=keyboard)

@dp.message_handler(content_types=types.ContentTypes.TEXT, text="❓ Какие лимитки мы поймали")
async def howlimited(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="Ссылка", url="https://t.me/aiogrammader"))
    await message.reply("<b>Наш канал где публикуются пойманые лимитки</b>", parse_mode="HTML", reply_markup=keyboard)

@dp.message_handler(content_types=types.ContentTypes.TEXT, text="🍪 Мой куки")
async def cookie(message: types.Message):
    cursor.execute("SELECT cookie FROM users WHERE user_id = ?", (message.from_user.id,))
    cookies = cursor.fetchone()[0]
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="🍪 Сменить куки", callback_data="changecookie"))
    async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookies}) as client:
        response = await client.get("https://users.roblox.com/v1/users/authenticated", ssl = False)
        data = await response.json()
        if data.get('id') == None:
            await message.reply("<b><u>Вам нужно сменить куки!</u></b>", parse_mode="HTML", reply_markup=keyboard)
            return
        await message.reply("<b>С куки <u>всё отлично!</u></b>", parse_mode="HTML", reply_markup=keyboard)

@dp.message_handler(content_types=types.ContentTypes.TEXT, text="📝 Отзывы")
async def review(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="📝 Отзывы", url="https://t.me/aiogrammader"))
    await message.reply("📝 Отзывы", parse_mode="HTML", reply_markup=keyboard)

@dp.message_handler(content_types=types.ContentTypes.TEXT, text="🛠 Поддержка")
async def help(message: types.Message):
    await message.reply("<b>Напишите свой вопрос</b>", parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())
    await states.help.set()

@dp.message_handler(content_types=types.ContentTypes.TEXT, text="❓ FAQ")
async def faq(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="❓ FAQ", url="https://t.me/aiogrammader"))
    await message.reply("<b>❓ FAQ</b>", parse_mode="HTML", reply_markup=keyboard)

@dp.message_handler(content_types=types.ContentTypes.TEXT, text="👨‍💻 GitHub")
async def faq(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="👨‍💻 GitHub", url="https://github.com/"))
    await message.reply("<b>GitHub автора - там где вы сможете найти <tg-spoiler>(скоро)</tg-spoiler> исходный код бота</b>", parse_mode="HTML", reply_markup=keyboard)

#стейты калбеки

@dp.message_handler(state=states.help)
async def process_help_text(message: types.Message, state: FSMContext):
    await message.reply("<b>Ваш вопрос отправлен, в скорем времени вам ответят!</b>", parse_mode="HTML", reply_markup=mainkeyboard)
    await state.finish()
    help_user = await bot.send_message(help_chat, f"{message.text}")
    cursor.execute("INSERT INTO help (user_id, msg_id) VALUES (?, ?)", (message.from_user.id, help_user.message_id))
    conn.commit()
    await state.finish()

@dp.message_handler(chat_id=help_chat, is_reply=True)
async def answer(message: types.Message):
    try:
        replied_message_id = message.reply_to_message.message_id
        if message.text == "/clear":
            await bot.delete_message(message.chat.id, replied_message_id)
            await bot.delete_message(message.chat.id, message.message_id)
            return
        elif message.text == "/info":
            cursor.execute("SELECT user_id FROM help WHERE msg_id = ?", (replied_message_id,))
            user_id = cursor.fetchone()[0]
            await message.reply(f"UID: {user_id}")
            return
        cursor.execute("SELECT user_id FROM help WHERE msg_id = ?", (replied_message_id,))
        uid = cursor.fetchone()[0]
        await bot.send_message(uid, f"<b>Ваш вопрос: {message.reply_to_message.text}\nОтвет: {message.text}</b>", parse_mode="HTML")
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, replied_message_id)
        dels = await message.answer("Ответ отправлен")
        await asyncio.sleep(2)
        await bot.delete_message(dels.chat.id, dels.message_id)
    except:
        await message.reply("Error брат")
    
@dp.callback_query_handler(lambda c: c.data == "changecookie")
async def changecookie(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.message.chat.id, "<b>Введите новый куки\nНапишите нет если не захотели</b>", parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())
    await states.changecookies.set()

@dp.message_handler(state=states.changecookies)
async def changecookies(message: types.Message, state: FSMContext):
    cookies = message.text
    if cookies.lower() == "нет":
        await message.reply("<b>Понял</b>", parse_mode="HTML", reply_markup=mainkeyboard)
        await state.finish()
        return
    async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookies}) as client:
        response = await client.get("https://users.roblox.com/v1/users/authenticated", ssl = False)
        data = await response.json()
        if data.get('id') == None:
            await message.reply("<b><u>Куки невалид!</u>\nНапишите нет если передумал(-а)</b>", parse_mode="HTML")
            return
        await message.answer("<b>С куки <u>всё отлично!</u></b>", parse_mode="HTML", reply_markup=mainkeyboard)
        await message.delete()
    cursor.execute("UPDATE users SET cookie = ? WHERE user_id = ?", (cookies, message.from_user.id))
    conn.commit()

    with open('config.json', 'r') as file:
        config = json.load(file)
    new_account_value = cookies
    config["accounts"].append(new_account_value)
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

    await state.finish()


#ост

@dp.message_handler(content_types=types.ContentTypes.ANY)
async def idk(message: types.Message):
    await message.reply("<b>Я тебя не понимаю!</b>", reply_markup=mainkeyboard, parse_mode="HTML")

async def check_config():
    while True:
        with open('config.json', 'r') as config_file:
            config_data = json.load(config_file)
        accounts = config_data.get('accounts', [])
        
        for cookie in accounts:
            async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookie}) as client:
                response = await client.get("https://users.roblox.com/v1/users/authenticated", ssl=False)
                data = await response.json()

                if data.get('id') is None:
                    accounts.remove(cookie)
                    config_data['accounts'] = accounts
                    with open('config.json', 'w') as config_file:
                        json.dump(config_data, config_file, indent=4)
        await asyncio.sleep(0.1)




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
  #  loop.create_task(check_config())
    executor.start_polling(dp, skip_updates=True)