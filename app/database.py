import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import DB_CONFIG

logger = logging.getLogger(__name__)


def get_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


def init_db():
    """Создаёт таблицы при первом запуске"""
    init_query = """
    CREATE TABLE IF NOT EXISTS requests (
        id          SERIAL PRIMARY KEY,
        base        VARCHAR(10) NOT NULL,
        requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        status      VARCHAR(20) NOT NULL  -- 'success' | 'error'
    );

    CREATE TABLE IF NOT EXISTS responses (
        id          SERIAL PRIMARY KEY,
        request_id  INT NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
        currency    VARCHAR(10) NOT NULL,
        rate        NUMERIC(20, 8) NOT NULL,
        usd_price   NUMERIC(20, 8) NOT NULL,
        recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    
    

    CREATE INDEX IF NOT EXISTS idx_responses_request_id ON responses(request_id);
    CREATE INDEX IF NOT EXISTS idx_requests_requested_at ON requests(requested_at DESC);
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(init_query)
        conn.commit()
    logger.info("Database initialised")


def save_fetch_result(base: str, rates: dict | None, status: str):
    """Сохраняет один цикл опроса API"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO requests (base, status) VALUES (%s, %s) RETURNING id",
                (base, status),
            )
            request_id = cur.fetchone()["id"]

            if rates:
                for currency, rate in rates.items():
                    usd_price = round(1 / rate, 8) if rate else 0
                    cur.execute(
                        "INSERT INTO responses (request_id, currency, rate, usd_price) VALUES (%s, %s, %s, %s)",
                        (request_id, currency, rate, usd_price))

        conn.commit()
