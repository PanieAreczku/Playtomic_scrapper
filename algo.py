# padel_notifier/algo.py
from datetime import time as dtime
import os
from scheduler import run

if __name__ == '__main__':
    days = 14
    min_time = dtime(17, 0)
    max_time = dtime(22, 0)
    duration = 90
    interval = 120  # seconds
    user_key = os.getenv('PUSHOVER_USER_KEY')
    notify = False
    include_weekends = False

    run(
        days,
        min_time,
        max_time,
        duration,
        interval,
        user_key,
        notify,
        include_weekends
    )