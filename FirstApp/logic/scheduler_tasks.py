from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
import datetime as d
from datetime import datetime

# this method will schedule the automation process task
from FirstApp.automation_process import automation_process


def task_scheduler(lecturer, subject, subject_code, video_length):

    jobstores = {
        'mongo': MongoDBJobStore(),
    }

    sched = BackgroundScheduler(jobstores=jobstores)
    after_20s = datetime.now() + d.timedelta(seconds=30)
    sched.add_job(automation_process, args=[lecturer, subject, subject_code, video_length], trigger='date', run_date=after_20s, id='Automation_1')
    sched.start()

    job = sched.get_job(job_id='Automation_1')
    MongoDBJobStore().add_job(job=job)


    return sched