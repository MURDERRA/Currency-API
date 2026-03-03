def format_rates(rows: list, title: str) -> list[str]:
    if not rows:
        return ["Записей не найдено."]

    lines = [f"<b>{title}</b>\n"]
    for row in rows:
        lines.append(f"{row['currency']}: {row['rate']} "
                     f"| 1 USD = {row['usd_price']} {row['currency']} "
                     f"| {row['recorded_at'].strftime('%d.%m.%Y %H:%M')}")

    return _split_messages(lines)


def format_requests(data: list) -> list[str]:
    if not data:
        return ["Запросов не найдено."]

    lines = ["<b>История запросов</b>\n"]
    for item in data:
        req = item["request"]
        rates = item["rates"]
        lines.append(
            f"\nID {req['id']} | {req['requested_at'].strftime('%d.%m.%Y %H:%M')} МСК "
            f"| {req['status']} | база: {req['base']}")
        for r in rates:
            lines.append(
                f"  {r['currency']}: rate={r['rate']} | usd_price={r['usd_price']}"
            )
        if rates:
            lines.append("  ...")

    return _split_messages(lines)


def _split_messages(lines: list[str]) -> list[str]:
    messages, current = [], ""
    for line in lines:
        if len(current) + len(line) + 1 > 4096:
            messages.append(current)
            current = ""
        current += line + "\n"
    if current:
        messages.append(current)
    return messages
