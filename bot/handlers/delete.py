from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.database import get_connection
from bot.utils.date_parser import parse_range

router = Router()


def delete_by_ids(ids: list[int]) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM requests WHERE id = ANY(%s)", (ids, ))
            count = cur.rowcount
        conn.commit()
    return count


@router.message(Command("delete"))
async def cmd_delete(message: Message):
    args = message.text.split()[1:]

    if not args:
        await message.answer("Укажи параметр:\n"
                             "/delete count 10 — последние N запросов\n"
                             "/delete id 42 — конкретный запрос\n"
                             "/delete date 01.03.2026\n"
                             "/delete date 01.03.2026 - 03.03.2026")
        return

    mode = args[0].lower()

    if mode == "count":
        if len(args) < 2 or not args[1].isdigit():
            await message.answer("Укажи число: /delete count 10")
            return
        n = int(args[1])
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM requests ORDER BY requested_at DESC LIMIT %s",
                    (n, ))
                ids = [row["id"] for row in cur.fetchall()]
        if not ids:
            await message.answer("Записей не найдено.")
            return
        count = delete_by_ids(ids)
        await message.answer(f"Удалено {count} запросов.")

    elif mode == "id":
        if len(args) < 2 or not args[1].isdigit():
            await message.answer("Укажи ID: /delete id 42")
            return
        count = delete_by_ids([int(args[1])])
        if count:
            await message.answer(f"Запрос ID {args[1]} удалён.")
        else:
            await message.answer(f"Запрос с ID {args[1]} не найден.")

    elif mode == "date":
        result = parse_range(args[1:])
        if not result:
            await message.answer("Неверный формат даты.")
            return
        start, end = result
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM requests WHERE requested_at_msk BETWEEN %s AND %s",
                    (start, end),
                )
                count = cur.rowcount
            conn.commit()
        await message.answer(f"Удалено {count} запросов за указанный период.")

    else:
        await message.answer("Неизвестный режим. Используй: count, id, date")
