from app import create_app
from apscheduler.schedulers.background import BackgroundScheduler
from app.appointment_checker import check_and_send_reminders

app = create_app()

def job_wrapper():
    with app.app_context():
        check_and_send_reminders()

# Schedule the job to run every minute
scheduler = BackgroundScheduler()
scheduler.add_job(job_wrapper, 'interval', minutes=1)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)