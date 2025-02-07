from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from line_api.models import Member



def periodic_execution():
    
    data = {
        "absent_flag": 0,
        "groupsep_flag": 0,
        "absent_reason": ""
    }

    Member.objects.all().update(**data)

    print("ClearedStatus!!")


def start():
  scheduler = BackgroundScheduler()
  scheduler.add_job(periodic_execution, 'cron', day_of_week='thu')# 毎週木曜日に実行
  scheduler.start()