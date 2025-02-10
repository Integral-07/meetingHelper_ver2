from apscheduler.schedulers.background import BackgroundScheduler
from line_api.models import Member, System



def periodic_execution():
    
    data = {
        "absent_flag": 0,
        "groupsep_flag": 0,
        "absent_reason": ""
    }

    Member.objects.all().update(**data)

    print("Cleared Status!!")

def clear_authinfo_times():

    System.objects.all().update(auth_info_times=0)

    print("Auth Info Reopened")


def start():
    day_of_weeks = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    schedule = System.objects.get(id=0).meeting_DayOfWeek

    schedule_dayafter_index = day_of_weeks.index(schedule) + 1
    if schedule_dayafter_index >= 7:
        schedule_dayafter_index = 0

    scheduler = BackgroundScheduler()
    scheduler.add_job(periodic_execution, 'cron', hour=1, day_of_week=day_of_weeks[schedule_dayafter_index])
    scheduler.add_job(clear_authinfo_times, 'cron', hour=1)
    scheduler.start()