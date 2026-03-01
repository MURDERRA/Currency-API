# Currency Tracker

[English version](README.en.md)

Микросервис, который периодически забирает курсы валют с публичного API и сохраняет их в PostgreSQL. Работает в фоне по расписанию, логирует все события и хранит историю каждого запроса.

## Цель проекта

Иметь самодостаточный сервис, который непрерывно работает, подтягивает свежие данные по валютам с заданным интервалом и сохраняет их в PostgreSQL. Неудачные запросы тоже фиксируются отдельно, чтобы можно было отслеживать надёжность API.

## Возможности

- Получение курсов валют с exchangerate-api.com с настраиваемым интервалом
- Сохранение каждой попытки запроса в базу, включая неудачные
- Хранение всех полученных курсов и их эквивалента в USD, привязанных к запросу
- Ротируемые лог-файлы: `app.log` - для всех событий, `errors.log` - только для ошибок
- Полная контейнеризация через Docker Compose, база данных включена
- Конфигурация через переменные окружения, хардкодные значения отсутствуют

## Запуск

Необходимы Docker и Docker Compose.

```bash
git clone https://github.com/MURDERRA/Currency-API
cd Currency-API

cp .env.example .env

docker compose up -d --build

docker compose logs -f app
```

Чтобы вручную выполнить JOIN-запрос и посмотреть собранную историю:

```bash
docker compose exec app python -m app.queries
```

## Архитектура

```md
currency-tracker/
├── app/
│   ├── main.py        # точка входа, настройка логирования и планировщика
│   ├── config.py      # чтение настроек из .env
│   ├── database.py    # подключение, создание таблиц, сохранение результатов
│   ├── fetcher.py     # HTTP-запрос к API, обработка ошибок
│   └── queries.py     # JOIN-запрос для истории, можно запускать отдельно
├── logs/              # примонтированный volume, хранится и синхронизирован с контейнером
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

В базе используются две таблицы. `requests` фиксирует каждую попытку запроса и её статус. `responses` хранит курсы валют, их эквивалент в USD и ссылается на `requests` через внешний ключ. Так неудачные запросы учитываются без потери целостности данных.

SQL-запрос для выгрузки полной истории:

```sql
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
```

## Переменные окружения

Скопируйте `.env.example` в `.env` и заполните:

```env
API_KEY=your_exchangerate_api_key_here
API_URL=https://v6.exchangerate-api.com/v6
BASE_CURRENCY=USD
FETCH_INTERVAL_MINUTES=10

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=currency_db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```

При запуске через Docker Compose переменная `POSTGRES_HOST` автоматически переопределяется на имя сервиса `db` внутри Docker-сети.
