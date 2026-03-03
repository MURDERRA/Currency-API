from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

INFO_TEXT = """
<b>Currency Tracker Bot</b>

Бот для работы с историей курсов валют.

<b>Команды:</b>
/help — список команд
/convert [кол-во] [из] [в] — конвертация по последнему курсу
  Пример: /convert 2 usd kzt

/history [дата или период] — история курсов
  /history — за сегодня
  /history 01.03.2026
  /history 01.03.2026 10:00
  /history 01.03.2026 - 03.03.2026
  /history 01.03.2026 10:00 - 03.03.2026 18:00

/history_request [дата или период] — история запросов к API
  Те же форматы дат что и у /history

/delete — удаление записей
  /delete count 10 — последние 10 запросов
  /delete id 42 — запрос с ID 42
  /delete date 01.03.2026
  /delete date 01.03.2026 10:00 - 03.03.2026 18:00

Все даты и время принимаются в МСК.
"""

HELP_TEXT = """
/convert [кол-во] [из] [в]
/history [дата или период]
/history_request [дата или период]
/delete count|id|date ...
"""


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(INFO_TEXT, parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode="HTML")
