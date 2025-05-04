# padel_notifier/scheduler.py
import time
import logging
from datetime import timedelta
import pandas as pd
from availability import AvailabilityScanner
from notification import PushoverClient
from config import TENANT_ID, TIMEZONE

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def run(
    days: int,
    min_time,
    max_time,
    duration: int,
    interval: int,
    user_key: str,
    notify: bool = False,
    include_weekends: bool = False
) -> None:
    scanner = AvailabilityScanner(TENANT_ID, TIMEZONE)
    dates = scanner.get_date_range(days, include_weekends)
    client = PushoverClient(user_key)
    seen = set()

    while True:
        all_slots = []
        for date in dates:
            raw = scanner.fetch(date)
            slots = scanner.parse_slots(raw, min_time, max_time, duration)
            for s in slots:
                key = (date, s['court'], s['datetime'], s['duration'], s['price'])
                if key not in seen:
                    seen.add(key)
                    msg = f"{s['court']} {s['datetime']} ({s['duration']}min) ${s['price']}"
                    logger.info('New slot: %s', msg)
                    if notify:
                        client.send(msg)
                all_slots.append(s)
        df = pd.DataFrame(all_slots)
        print(df)
        logger.info('Sleeping for %s seconds', interval)
        time.sleep(interval)