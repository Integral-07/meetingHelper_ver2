from apscheduler.schedulers.background import BackgroundScheduler
from line_api.models import Member, System
from datetime import date
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)



def get_current_system():
    try:
        return System.objects.get(id=0)
    except System.DoesNotExist:
        logging.info("System with id=0 not found.")
        return None

def clear_user_status():

    today = date.today()
    weekday_number = today.weekday()

    day_of_weeks = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    system = get_current_system()
    if system is None:
        logging.error("System情報が取得できませんでした。clear_user_statusをスキップします。")
        return
    schedule = system.meeting_DayOfWeek

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
            logging.info("Cleared Status!!")
        else:
            logging.info("failed to clear status...")


def clear_authinfo_times():

    System.objects.all().update(auth_info_times=0)


def start():

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