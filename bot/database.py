import psycopg2
from psycopg2.extras import RealDictCursor
from bot.config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


def init_backup_db():
    """Создаёт резервные таблицы если не существуют."""
    ddl = """
    CREATE TABLE IF NOT EXISTS requests_backup (LIKE requests INCLUDING ALL);
    CREATE TABLE IF NOT EXISTS responses_backup (LIKE responses INCLUDING ALL);
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()


def sync_backup():
    """Синхронизация в резервные таблицы — вставляет только новые записи."""
    sql = """
    INSERT INTO requests_backup
        SELECT * FROM requests
        WHERE id NOT IN (SELECT id FROM requests_backup);

    INSERT INTO responses_backup
        SELECT * FROM responses
        WHERE id NOT IN (SELECT id FROM responses_backup);
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
