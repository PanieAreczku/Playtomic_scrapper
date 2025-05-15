# padel_notifier/scheduler.py
import time
import logging
from datetime import timedelta
from typing import List, Optional

import pandas as pd
from availability import AvailabilityScanner
from notification import PushoverClient
from email_notifier import EmailNotifier  # ← import your new class
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
    email_recipients: list[str] | None = None,
    notify: bool = False,
    include_weekends: bool = False
) -> None:
    scanner = AvailabilityScanner(TENANT_ID, TIMEZONE)
    dates = scanner.get_date_range(days, include_weekends)

    pushover = PushoverClient(user_key)
    email_notifier = EmailNotifier()  # ← instantiate once
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
            df['date'] = df['datetime'].dt.strftime('%Y-%m-%d')
            df['day'] = df['datetime'].dt.strftime('%a').str.upper()
            df['time'] = df['datetime'].dt.strftime('%H:%M')
            df = df[['date', 'day', 'time', 'court', 'duration']].drop_duplicates(
                subset=['date', 'time', 'duration'],
                keep='first'
            )

        # 3) Initial vs subsequent runs
        if initial_run:
            title = "Initial available courts"
            if all_slots:
                table = df.to_string(index=False)
                logger.info(f"{title}:\n{table}")
                if notify:
                    message = f"{title}:\n```\n{table}\n```"
                    pushover.send(message)
                    if email_recipients:
                        # send email too
                        email_notifier.send_email(
                            recipients=email_recipients,
                            subject=title,
                            body=table,
                            is_html=False
                        )
            else:
                logger.info("No courts available")
            initial_run = False

        else:
            if new_slots_found:
                df_new = pd.DataFrame(new_slots_found)
                df_new['date'] = df_new['datetime'].dt.strftime('%Y-%m-%d')
                df_new['day'] = df_new['datetime'].dt.strftime('%a').str.upper()
                df_new['time'] = df_new['datetime'].dt.strftime('%H:%M')
                df_new = df_new[['date', 'day', 'time', 'court', 'duration']]

                table_new = df_new.to_string(index=False)
                logger.info(f"New slots found:\n{table_new}")
                if notify:
                    message = f"New slots found:\n```\n{table_new}\n```"
                    pushover.send(message)

                    if email_recipients:
                        email_notifier.send_email(
                            recipients=email_recipients,
                            subject="New slots found",
                            body=table_new,
                            is_html=False
                        )

        # 4) sleep quietly
        time.sleep(interval)
