from __future__ import annotations

from database.connection import SessionLocal, init_db
from jobs.daily_radar_job import DailyRadarJob


def main() -> None:
    init_db()
    db = SessionLocal()

    try:
        job = DailyRadarJob(db)
        message = job.run()
        print("Radar enviado com sucesso.")
        print("-" * 60)
        print(message.replace("<b>", "").replace("</b>", ""))
    finally:
        db.close()


if __name__ == "__main__":
    main()
