# 🏓 Playtomic Court Availability Scraper

A Python script that checks for available padel courts via the Playtomic API and sends notifications via Pushover when new time slots appear within a defined time window. Designed for personal use to track court availability for a specific venue over the next two weeks.

## 📦 Features

- Scrapes court availability for the next 15 days
- Filters by time range and court duration
- Sends real-time Pushover notifications
- Automatically filters out blocked courts
- Periodically scans every 10 minutes to detect new available slots
- Outputs results in a readable table format

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Playtomic_scrapper.git
   cd Playtomic_scrapper

To run the script use file algo.py
python algo.py


Playtomic_scrapper/
├── algo.py              # Main script
├── scheduler.py         # Slot scanning and notification logic
├── .env                 # Your local API keys and config
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
