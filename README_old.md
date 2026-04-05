# Insight Engine V2 (Native & Optimized)

This project has been consolidated into a native, single-folder application as requested.

## Features
- **Fast Backend:** Single Python script (`app.py`) using FastAPI.
- **Modern Frontend:** Single HTML file (`index.html`) using Tailwind CSS.
- **Optimized Database:** SQLite with indexes for high-speed local access.
- **Google Auth:** Integrated for login and registration.
- **Password Reset:** Simplified password recovery mechanism.
- **Profile Management:** Edit profile and link Telegram ID.
- **Telegram Integration:** Ready-to-use bot link for updates.
- **No Docker/Venv:** Runs natively on your system.

## Setup & Run
1.  **Dependencies:** Ensure you have Python 3 and pip installed.
2.  **Configuration:** Update `.env` with your `GOOGLE_CLIENT_ID` and `TELEGRAM_BOT_TOKEN`.
3.  **Run:**
    ```bash
    ./run_app.sh
    ```
    - Backend will run on: http://localhost:8000
    - Frontend will run on: http://localhost:8080 (or open index.html directly)

## Files
- `app.py`: The entire backend (API, Auth, Models).
- `index.html`: The entire frontend.
- `requirements.txt`: Python dependencies.
- `.env`: System configuration.
- `run_app.sh`: Script to start the application.

Everything has been packaged into `insight_engine.tar.gz` in your home folder for easy download.
