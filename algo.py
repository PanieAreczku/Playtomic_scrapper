# padel_notifier/algo.py
from datetime import time as dtime
import os
from scheduler import run

if __name__ == '__main__':
    days = 14
    min_time = dtime(17, 0)
    max_time = dtime(22, 0)
    duration = 90
    interval = 600  # seconds
    user_key = os.getenv('PUSHOVER_USER_KEY')
    notify = True
    include_weekends = True

    # Read email recipients from an env var like:
    #   EMAIL_RECIPIENTS="alice@example.com,bob@example.com"
    raw = os.getenv('EMAIL_RECIPIENTS', '')
    email_recipients = [e.strip() for e in raw.split(',') if e.strip()]

    run(
        days=days,
        min_time=min_time,
        max_time=max_time,
        duration=duration,
        interval=interval,
        user_key=user_key,
        email_recipients=email_recipients,  # ← pass them here
        notify=notify,
        include_weekends=include_weekends
    )
