HISTORY_QUERY = """
SELECT
    r.id            AS request_id,
    r.base,
    r.requested_at,
    r.status,
    rs.currency,
    rs.rate,
    rs.usd_price,
    rs.recorded_at
FROM requests r
JOIN responses rs ON rs.request_id = r.id
WHERE r.status = 'success'
ORDER BY r.requested_at DESC, rs.currency
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
