from __future__ import annotations

from database.connection import SessionLocal, init_db
from jobs.events_job import EventsJob


def main() -> None:
    init_db()
    db = SessionLocal()

    try:
        job = EventsJob(db)
        message = job.run()
        if message is None:
            print("Nenhum evento novo. Telegram não enviado.")
            return

        print("Alertas de eventos enviados com sucesso.")
        print("-" * 60)
        print(message.replace("<b>", "").replace("</b>", ""))
    finally:
        db.close()


if __name__ == "__main__":
    main()
