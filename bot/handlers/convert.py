from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.database import get_connection

router = Router()


@router.message(Command("convert"))
async def cmd_convert(message: Message):
    args = message.text.split()[1:]

    # /convert [amount] <from> <to>
    if len(args) == 3:
        try:
            amount = float(args[0])
        except ValueError:
            await message.answer("Неверный формат. Пример: /convert 2 usd kzt")
            return
        from_cur, to_cur = args[1].upper(), args[2].upper()
    elif len(args) == 2:
        amount = 1.0
        from_cur, to_cur = args[0].upper(), args[1].upper()
    else:
        await message.answer("Пример: /convert 2 usd kzt или /convert usd kzt")
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            # берём последний успешный запрос
            cur.execute(
                "SELECT id FROM requests WHERE status='success' ORDER BY requested_at DESC LIMIT 1"
            )
            req = cur.fetchone()
            if not req:
                await message.answer("В базе нет данных о курсах.")
                return

            request_id = req["id"]

            cur.execute(
                "SELECT currency, rate FROM responses WHERE request_id = %s AND currency IN %s",
                (request_id, (from_cur, to_cur)),
            )
            rates = {
                row["currency"]: float(row["rate"])
                for row in cur.fetchall()
            }

    from_found = from_cur in rates
    to_found = to_cur in rates

    if not from_found and not to_found:
        await message.answer(
            f"Валюты {from_cur} и {to_cur} отсутствуют в базе данных.")
        return
    if not from_found:
        await message.answer(f"Валюта {from_cur} отсутствует в базе данных.")
        return
    if not to_found:
        await message.answer(f"Валюта {to_cur} отсутствует в базе данных.")
        return

    # все курсы хранятся относительно базовой валюты (USD)
    # rate = сколько единиц валюты за 1 USD
    result = amount * (rates[to_cur] / rates[from_cur])
    await message.answer(
        f"{amount} {from_cur} = <b>{result:.4f} {to_cur}</b>",
        parse_mode="HTML",
    )
