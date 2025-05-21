from apscheduler.schedulers.background import BackgroundScheduler
from line_api.models import Member, System
from datetime import date


def periodic_execution():

    print("periodic")
    today = date.today()
    weekday_number = today.weekday()

    day_of_weeks = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    schedule = System.objects.get(id=0).meeting_DayOfWeek

    schedule_dayafter_index = day_of_weeks.index(schedule) + 1
    if schedule_dayafter_index >= 7:
        schedule_dayafter_index = 0

    if weekday_number == schedule_dayafter_index:
    
        while(True):
            data = {
                "absent_flag": 0,
                "groupsep_flag": 0,
                "absent_reason": ""
            }

            Member.objects.all().update(**data)

            numRemain = Member.objects.exclude(absent_reason="").count()
            if(numRemain == 0):
                print("Cleared Status!!")
                break
            
            print("faild to clear status")


def clear_authinfo_times():

    System.objects.all().update(auth_info_times=0)

    print("Auth Info Reopened")


def start():

    scheduler = BackgroundScheduler()
    scheduler.add_job(periodic_execution, 'interval', minutes=1)
    scheduler.add_job(clear_authinfo_times, 'cron', hour=1)
    scheduler.start()