# Currency Tracker

A microservice that periodically fetches exchange rates from a public API and stores them in a PostgreSQL database. Built as a background service that runs on a schedule, logs all activity, and keeps a clean history of every request made.

## Purpose

The goal is to have a self-contained service that runs continuously, pulls fresh currency data at a configured interval, and persists it in a relational database. It also separates failed requests from successful ones so you can track API reliability over time.

## Features

- Fetches exchange rates from exchangerate-api.com on a configurable interval
- Stores every request attempt in the database, including failed ones
- Saves all returned rates linked to their originating request
- Rotating log files: `app.log` for all events, `errors.log` for errors only
- Fully containerised with Docker Compose, database included
- Environment-based configuration, no hardcoded values

## How to Run

Make sure you have Docker and Docker Compose installed.

```bash
# 1. Clone the repository
git clone https://github.com/MURDERRA/Currency-API
cd Currency-API

# 2. Copy the example env file and fill in your values
cp .env.example .env

# 3. Start everything
docker compose up -d --build

# 4. Check logs
docker compose logs -f app
```

To run the JOIN query manually and see the collected history:

```bash
docker compose exec app python -m app.queries
```

## Architecture

```md
currency-tracker/
├── app/
│   ├── main.py        # entry point, sets up logging and scheduler
│   ├── config.py      # reads settings from .env
│   ├── database.py    # connection, table creation, saving results
│   ├── fetcher.py     # HTTP request to the API, error handling
│   └── queries.py     # JOIN query for history, runnable standalone
├── logs/              # mounted volume, persists outside the container
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

Two tables are used in the database. `requests` records every fetch attempt with its status. `responses` stores individual currency rates and references `requests` via a foreign key. This way failed requests are tracked without orphaned rate data.

The SQL query that pulls the full history:

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

## Environment Variables

Copy `.env.example` to `.env` and set the following:

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

When running via Docker Compose, `POSTGRES_HOST` is overridden automatically to point to the `db` service inside the Docker network.
