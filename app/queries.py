HISTORY_QUERY = """
    SELECT
        r.id            AS request_id,
        r.base,
        r.requested_at_msk    AS requested_at,
        r.status,
        rs.currency,
        rs.rate,
        rs.usd_price,
        rs.recorded_at_msk   AS recorded_at
    FROM requests r
    JOIN responses rs ON rs.request_id = r.id
    WHERE r.status = 'success'
    ORDER BY r.requested_at DESC, rs.currency
    LIMIT 200;
    """


def get_history_query(timezone_mode: str = "utc") -> str:
    if timezone_mode == "msk":
        time_col_r = "r.requested_at_msk"
        time_col_rs = "rs.recorded_at_msk"
    else:
        time_col_r = "r.requested_at"
        time_col_rs = "rs.recorded_at"

    return f"""
    SELECT
        r.id            AS request_id,
        r.base,
        {time_col_r}    AS requested_at,
        r.status,
        rs.currency,
        rs.rate,
        rs.usd_price,
        {time_col_rs}   AS recorded_at
    FROM requests r
    JOIN responses rs ON rs.request_id = r.id
    WHERE r.status = 'success'
    ORDER BY {time_col_r} DESC, rs.currency
    LIMIT 200;
    """


if __name__ == "__main__":
    import json
    from app.database import get_connection

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(HISTORY_QUERY)
            rows = cur.fetchall()

    print(json.dumps([dict(r) for r in rows], indent=2, default=str))
