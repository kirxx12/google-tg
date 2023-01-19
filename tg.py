import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram import executor
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton
from aiogram.utils.exceptions import BadRequest
import json

from main import set_access, table, link_for_table, change


SETTINGS = {'TOKEN': '5822265582:AAFQEFK5YiKluBxFSRunEp15hsHbVlh3RLw'}
bot = Bot(SETTINGS['TOKEN'])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class CreateTable(StatesGroup):
    GET_GMAIL = State()
    GET_NAME_FOR_TABLE = State()
    GET_NAME_FOR_SHEET = State()


class GetLink(StatesGroup):
    GET_NAME = State()
    GET_LINK = State()


class GetAccess(StatesGroup):
    START = State()
    GET_GMAIL = State()
    GET_TABLE_NAME = State()


class SetValue(StatesGroup):
    START = State()
    GET_TABLE_NAME = State()
    GET_POS = State()
    GET_VALUE = State()


@dp.message_handler(commands=['start'])
async def my_start(message):
    btns = [InlineKeyboardButton(text='Создать таблицу',
                                 callback_data='create_table'),
            InlineKeyboardButton(text='В меню',
                                 callback_data='menu')]
    start_btns = InlineKeyboardMarkup(row_width=1)
    start_btns.add(*btns)
    await message.answer('Привет, чтобы начать, создай свою первую таблицу, нажав кнопку ниже!',
                         reply_markup=start_btns)


@dp.callback_query_handler(text='create_table')
async def create_table(call, state):
    await CreateTable.GET_GMAIL.set()
    await call.message.answer('Введите свою почту')


@dp.message_handler(state=CreateTable.GET_GMAIL)
async def get_gmail(message, state):
    async with state.proxy() as data:
        data['gmail'] = message.text
    await CreateTable.next()
    await message.answer('Теперь введи название новой таблицы')


@dp.message_handler(state=CreateTable.GET_NAME_FOR_TABLE)
async def get_name_for_table(message, state):
    async with state.proxy() as data:
        data['title'] = message.text
    await CreateTable.next()
    await message.answer('И последнее, введи название для страницы в этой таблице')


@dp.message_handler(state=CreateTable.GET_NAME_FOR_SHEET)
async def get_name_for_sheet(message, state):
    async with state.proxy() as data:
        data['sheet'] = message.text
        try:
            table(data['gmail'],
                  {'title': data['title'],
                   'sheetName': data['sheet'],
                   'nameForRowJSON': data['title']})
        except:
            await message.answer('Что-то пошло не так')
        else:
            btns = [
                InlineKeyboardButton(text='Создать таблицу',
                                     callback_data='create_table'),
                InlineKeyboardButton(text='Вывести список всех таблиц',
                                     callback_data='get_tables'),
                InlineKeyboardButton(text='Изменить значение в таблице',
                                     callback_data='set_value'),
                InlineKeyboardButton(text='Получить доступ к таблице',
                                     callback_data='get_access'),
            ]
            reply = InlineKeyboardMarkup(row_width=1)
            reply.add(*btns)
            await message.answer('Таблица создана!', reply_markup=reply)
            await state.finish()


@dp.callback_query_handler(text='get_tables')
async def get_tables(call, state):
    with open('access.json', 'r') as f:
        data = json.load(f)
        tables = data.keys()
        response = '\n' + '\n'.join(tables) + '\n'
        btn = InlineKeyboardButton(text='Меню', callback_data='menu')
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(btn)
        await call.message.answer(f'Список всех доступных таблиц:{response}',
                                  reply_markup=markup)


@dp.callback_query_handler(text='get_link')
async def get_name_for_link(call, state):
    await GetLink.GET_NAME.set()
    await call.message.answer('Введи название таблицы,'+
                              ' ссылку на которую хочешь получить')
    await GetLink.next()


@dp.message_handler(state=GetLink.GET_LINK)
async def get_link(message, state):
    btn = InlineKeyboardButton(text='Меню', callback_data='menu')
    reply = InlineKeyboardMarkup(row_width=1)
    reply.add(btn)
    await state.finish()
    await message.answer(link_for_table(message.text), reply_markup=reply)


@dp.callback_query_handler(text='get_access')
async def get_access(call, state):
    await GetAccess.START.set()
    await call.message.answer('Напиши почту, которой нужно предоставить доступ')
    await GetAccess.next()


@dp.message_handler(state=GetAccess.GET_GMAIL)
async def get_access_gmail(message, state):
    async with state.proxy() as data:
        data['gmail'] = message.text
    await GetAccess.next()
    await message.answer('Напиши название таблицы, к которой нужно получить доступ')


@dp.message_handler(state=GetAccess.GET_TABLE_NAME)
async def get_access_table(message, state):
    async with state.proxy() as data:
        data['title'] = message.text
    try:
        set_access(data['gmail'], [data['title']])
    except:
        await state.finish()
        btn = InlineKeyboardButton(text='Меню', callback_data='menu')
        reply = InlineKeyboardMarkup(row_width=1)
        reply.add(btn)
        await message.answer('Что-то пошло не так, попробуй снова',
                             reply_markup=reply)
    else:
        await state.finish()
        btn = InlineKeyboardButton(text='Меню', callback_data='menu')
        reply = InlineKeyboardMarkup(row_width=1)
        reply.add(btn)
        await message.answer(f'Доступ к таблице {data["title"]} предоставлен',
                             reply_markup=reply)


@dp.callback_query_handler(text='set_value')
async def set_value(call, state):
    await SetValue.START.set()
    await call.message.answer('Введи название таблицы, в которую хочешь внести изменения')
    await SetValue.next()


@dp.message_handler(state=SetValue.GET_TABLE_NAME)
async def set_value_table_name(message, state):
    async with state.proxy() as data:
        data['title'] = message.text
    await SetValue.next()
    await message.answer('Введи ячейку, которую хочешь изменить (Например, "C2"')


@dp.message_handler(state=SetValue.GET_POS)
async def set_value_pos(message, state):
    async with state.proxy() as data:
        data['pos'] = message.text 
    await SetValue.next()
    await message.answer('Введи значение для указанной выше ячейки (если нужно очистить ячеку, то введи "empty" или "пусто"')


@dp.message_handler(state=SetValue.GET_VALUE)
async def set_value_value(message, state):
    async with state.proxy() as data:
        data['val'] = message.text
    if data['val'] in ['empty', 'пусто']:
        value = ''
    else:
        value = data['val']
    try:
        change([data['title'], data['pos'], value])
    except:
        await state.finish()
        btn = InlineKeyboardButton(text='Меню', callback_data='menu')
        reply = InlineKeyboardMarkup(row_width=1)
        reply.add(btn)
        await message.answer('Что-то пошло не так, попробуй снова',
                             reply_markup=reply)
    else:
        await state.finish()
        btn = InlineKeyboardButton(text='Меню', callback_data='menu')
        reply = InlineKeyboardMarkup(row_width=1)
        reply.add(btn)
        await message.answer('Значение в ячейке изменено',
                             reply_markup=reply)
    


@dp.callback_query_handler(text='menu')
async def menu(call, state):
    btns = [
                InlineKeyboardButton(text='Создать таблицу',
                                     callback_data='create_table'),
                InlineKeyboardButton(text='Вывести список всех таблиц',
                                     callback_data='get_tables'),
                InlineKeyboardButton(text='Изменить значение в таблице',
                                     callback_data='set_value'),
                InlineKeyboardButton(text='Получить доступ к таблице',
                                     callback_data='get_access'),
                InlineKeyboardButton(text='Получить ссылку на таблицу',
                                     callback_data='get_link')
            ]
    reply = InlineKeyboardMarkup(row_width=1)
    reply.add(*btns)
    await call.message.answer('Выбери опцию', reply_markup=reply)


while __name__ == '__main__':
    executor.start_polling(dp)