from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.database import get_connection
from bot.utils.date_parser import parse_range, today_range
from bot.utils.formatter import format_rates, format_requests
from datetime import datetime

router = Router()


def fetch_rates_for_period(start: datetime, end: datetime) -> list:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT rs.currency, rs.rate, rs.usd_price,
                       rs.recorded_at_msk AS recorded_at
                FROM responses rs
                JOIN requests r ON r.id = rs.request_id
                WHERE r.status = 'success'
                  AND rs.recorded_at_msk >= %s
                  AND rs.recorded_at_msk <= %s
                ORDER BY rs.recorded_at_msk DESC, rs.currency
                LIMIT 500
                """,
                (start, end),
            )
            rows = cur.fetchall()

    # если ничего не нашли — берём последние доступные записи
    if not rows:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT rs.currency, rs.rate, rs.usd_price,
                           rs.recorded_at_msk AS recorded_at
                    FROM responses rs
                    JOIN requests r ON r.id = rs.request_id
                    WHERE r.status = 'success'
                      AND r.id = (
                          SELECT id FROM requests
                          WHERE status = 'success'
                          ORDER BY requested_at DESC LIMIT 1
                      )
                    ORDER BY rs.currency
                    """, )
                rows = cur.fetchall()

    return rows


def fetch_requests_for_period(start: datetime, end: datetime) -> list:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT r.id, r.base, r.requested_at_msk AS requested_at, r.status
                FROM requests r
                WHERE r.requested_at_msk >= %s
                  AND r.requested_at_msk <= %s
                ORDER BY r.requested_at_msk DESC
                """,
                (start, end),
            )
            requests = cur.fetchall()

        if not requests:
            return []

        # для каждого запроса берём последние 10 курсов
        result = []
        with conn.cursor() as cur:
            for req in requests:
                cur.execute(
                    """
                    SELECT currency, rate, usd_price
                    FROM responses
                    WHERE request_id = %s
                    ORDER BY currency
                    LIMIT 10
                    """,
                    (req["id"], ),
                )
                rates = cur.fetchall()
                result.append({"request": req, "rates": rates})

    return result


@router.message(Command("history"))
async def cmd_history(message: Message):
    args = message.text.split()[1:]

    if args:
        result = parse_range(args)
        if not result:
            await message.answer("Неверный формат даты. Примеры:\n"
                                 "/history 01.03.2026\n"
                                 "/history 01.03.2026 10:00\n"
                                 "/history 01.03.2026 - 03.03.2026\n"
                                 "/history 01.03.2026 10:00 - 03.03.2026 18:00"
                                 )
            return
        start, end = result
    else:
        start, end = today_range()

    rows = fetch_rates_for_period(start, end)
    title = f"Курсы с {start.strftime('%d.%m.%Y %H:%M')} по {end.strftime('%d.%m.%Y %H:%M')} МСК"

    for msg in format_rates(rows, title):
        await message.answer(msg, parse_mode="HTML")


@router.message(Command("history_request"))
async def cmd_history_request(message: Message):
    args = message.text.split()[1:]

    if args:
        result = parse_range(args)
        if not result:
            await message.answer("Неверный формат даты.")
            return
        start, end = result
    else:
        start, end = today_range()

    data = fetch_requests_for_period(start, end)

    if not data:
        await message.answer(
            f"За период {start.strftime('%d.%m.%Y %H:%M')} — "
            f"{end.strftime('%d.%m.%Y %H:%M')} МСК запросов не найдено.")
        return

    for msg in format_requests(data):
        await message.answer(msg, parse_mode="HTML")
