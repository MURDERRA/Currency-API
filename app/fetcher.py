import logging
import requests
from app.config import API_KEY, API_URL, BASE_CURRENCY
from app.database import save_fetch_result

logger = logging.getLogger(__name__)

TIMEOUT = 10  # секунды


def fetch_and_save():
    """Основная задача планировщика."""
    url = f"{API_URL}/{API_KEY}/latest/{BASE_CURRENCY}"
    rates = None
    status = "error"

    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if data.get("result") == "success":
            rates = data["conversion_rates"]
            status = "success"
            logger.info("Fetched %d rates for %s", len(rates), BASE_CURRENCY)
        else:
            logger.error("API returned error: %s", data.get("error-type"))

    except requests.exceptions.Timeout:
        logger.error("Request timed out after %ss", TIMEOUT)
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error: %s", e)
    except requests.exceptions.HTTPError as e:
        logger.error("HTTP error %s: %s", e.response.status_code, e)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
    finally:
        save_fetch_result(BASE_CURRENCY, rates, status)
