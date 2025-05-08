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
    initial_run = True

    while True:
        all_slots       = []
        new_slots_found = []

        # 1) Fetch and dedupe slots
        for date in dates:
            raw   = scanner.fetch(date)
            slots = scanner.parse_slots(raw, min_time, max_time, duration)
            for s in slots:
                key = (date, s['court'], s['datetime'], s['duration'], s['price'])
                all_slots.append(s)
                if key not in seen:
                    seen.add(key)
                    new_slots_found.append(s)

        # 2) Build a clean DataFrame if there are any slots
        if all_slots:
            df = pd.DataFrame(all_slots)
            # split datetime into separate date/time for readability
            df['date'] = df['datetime'].dt.strftime('%Y-%m-%d')
            df['time'] = df['datetime'].dt.strftime('%H:%M')
            df = df[['date', 'court', 'time', 'duration', 'price']]

        # 3) Initial vs subsequent runs
        if initial_run:
            logger.info("Initial available courts:")
            if all_slots:
                table = df.to_string(index=False)
                print(table)  # local console
                if notify:
                    message = "Initial available courts:\n```\n" + table + "\n```"
                    client.send(message)
            else:
                logger.info("No courts available")
            initial_run = False

        else:
            if new_slots_found:
                df_new = pd.DataFrame(new_slots_found)
                df_new['date'] = df_new['datetime'].dt.strftime('%Y-%m-%d')
                df_new['time'] = df_new['datetime'].dt.strftime('%H:%M')
                df_new = df_new[['date', 'court', 'time', 'duration', 'price']]

                table_new = df_new.to_string(index=False)
                logger.info("New slots found:\n" + table_new)
                if notify:
                    message = "New slots found:\n```\n" + table_new + "\n```"
                    client.send(message)

        # 4) sleep quietly
        time.sleep(interval)