from datetime import datetime, timezone, timedelta

MSK = timezone(timedelta(hours=3))


def parse_dt(s: str) -> datetime | None:
    s = s.strip()
    for fmt in ["%d.%m.%Y %H:%M", "%d.%m.%Y"]:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=MSK, second=0, microsecond=0)
        except ValueError:
            continue
    return None


def parse_range(args: list[str]) -> tuple[datetime, datetime] | None:
    text = " ".join(args).strip()
    now = datetime.now(MSK).replace(second=0, microsecond=0)

    # диапазон через " - "
    if " - " in text:
        parts = text.split(" - ", 1)
        start = parse_dt(parts[0])
        end = parse_dt(parts[1])
        if not start or not end:
            return None
        # если конец без времени — до конца того дня
        if ":" not in parts[1]:
            end = end.replace(hour=23, minute=59)
        return start, end

    dt = parse_dt(text)
    if not dt:
        return None

    # только дата без времени — весь день
    if ":" not in text:
        start = dt.replace(hour=0, minute=0)
        end = dt.replace(hour=23, minute=59)
    else:
        # конкретное время — от него до сейчас
        start = dt
        end = now

    return start, end


def today_range() -> tuple[datetime, datetime]:
    now = datetime.now(MSK).replace(second=0, microsecond=0)
    start = now.replace(hour=0, minute=0)
    return start, now
