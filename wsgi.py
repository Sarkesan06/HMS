from app import create_app
from apscheduler.schedulers.background import BackgroundScheduler
from app.appointment_checker import check_and_send_reminders


app = create_app()


def _job_wrapper():
    with app.app_context():
        check_and_send_reminders()


# Start reminder scheduler for gunicorn/wsgi deployments.
scheduler = BackgroundScheduler()
scheduler.add_job(_job_wrapper, "interval", minutes=1, id="appointment_reminder_job", replace_existing=True)
scheduler.start()
