from apscheduler.schedulers.background import BackgroundScheduler
from line_api.models import Member, System
from datetime import date
import logging
logger = logging.getLogger(__name__)


def get_current_system():
    try:
        return System.objects.get(id=0)
    except System.DoesNotExist:
        logger.warning("System with id=0 not found.")
        return None

def clear_user_status():

    print("system is about to execute clear_user_status")
    today = date.today()
    weekday_number = today.weekday()

    day_of_weeks = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    schedule = get_current_system().meeting_DayOfWeek

    schedule_dayafter_index = day_of_weeks.index(schedule) + 1
    if schedule_dayafter_index >= 7:
        schedule_dayafter_index = 0

    if weekday_number == schedule_dayafter_index:
    
        
        data = {
            "absent_flag": 0,
            "groupsep_flag": 0,
            "absent_reason": ""
        }

        Member.objects.all().update(**data)

        numRemain = Member.objects.exclude(absent_reason="").count()
        if(numRemain == 0):
            print("Cleared Status!!")
        else:
            print("failed to clear status...")


def clear_authinfo_times():

    System.objects.all().update(auth_info_times=0)

    logger.info("Auth Info Reopened")


def start():

    print("ap_schedular started")
    scheduler = BackgroundScheduler()
    #scheduler.add_job(clear_user_status, 'cron', hour=1, id='job_clear_status', replace_existing=True)
    scheduler.add_job(
        clear_user_status,
        'interval',
        minutes=1,
        id='job_clear_status',
    )
    #scheduler.add_job(clear_authinfo_times, 'cron', hour=2, id='job_clear_auth', replace_existing=True)
    scheduler.start()