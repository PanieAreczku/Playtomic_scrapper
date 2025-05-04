# padel_notifier/availability.py
from datetime import datetime, timedelta, time as dtime
import pytz
import requests
from mapping import RESOURCE_MAPPING

class AvailabilityScanner:
    def __init__(self, tenant_id: str, tz_name: str):
        self.tenant_id = tenant_id
        self.timezone = pytz.timezone(tz_name)

    def get_date_range(self, days: int = 14, include_weekends: bool = False) -> list[str]:
        now = datetime.now(self.timezone)
        dates: list[str] = []
        for i in range(days):
            dt = now + timedelta(days=i)
            if include_weekends or dt.weekday() < 5:
                dates.append(dt.strftime('%Y-%m-%d'))
        return dates

    def fetch(self, date_str: str) -> list[dict]:
        start_min = f"{date_str}T00:00:00"
        start_max = f"{(datetime.fromisoformat(date_str) + timedelta(days=1)).date()}T00:00:00"
        url = 'https://api.playtomic.io/v1/availability'
        params = dict(sport_id='PADEL', start_min=start_min, start_max=start_max, tenant_id=self.tenant_id)
        headers = {'Content-Type': 'application/json', 'User-Agent': 'padel-notifier'}
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        # Exclude blocked courts
        blocked = {"648a9a72-cc0e-4061-8f45-8fd42fe70338", "dfc644f3-88ea-439f-9e2b-cbef817f59f8"}
        return [item for item in data if item['resource_id'] not in blocked]

    def parse_slots(
        self,
        entries: list[dict],
        min_time: dtime,
        max_time: dtime,
        duration: int
    ) -> list[dict]:
        results: list[dict] = []
        utc = pytz.utc
        for entry in entries:
            court = RESOURCE_MAPPING.get(entry['resource_id'], entry['resource_id'])
            for slot in entry.get('slots', []):
                dt_str = f"{entry['start_date']} {slot['start_time']}"
                dt_utc = utc.localize(datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S'))
                local_dt = dt_utc.astimezone(self.timezone)
                if min_time <= local_dt.time() <= max_time and slot['duration'] == duration:
                    results.append({
                        'court': court,
                        'datetime': local_dt,
                        'duration': duration,
                        'price': slot['price'],
                    })
        return results