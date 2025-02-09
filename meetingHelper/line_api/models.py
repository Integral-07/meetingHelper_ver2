from django.db import models

class Member(models.Model):

    GRADE_CHOICES = [
        ('GradeClass1', 'GradeClass1'),
        ('GradeClass2', 'GradeClass2'),
        ('GradeClass3', 'GradeClass3'),
    ]

    user_id = models.CharField(primary_key=True, max_length=100, verbose_name="ユーザID(LINEID)")
    name = models.CharField(default="", max_length=100, verbose_name="名前")
    grade_class = models.CharField(default="", max_length=100, verbose_name="学年区分", choices=GRADE_CHOICES)
    absent_flag = models.IntegerField(default=0, verbose_name="欠席連絡フラグ")
    groupsep_flag = models.IntegerField(default=0, verbose_name="グループ分けフラグ")

    absent_reason = models.TextField(default="", max_length=2000, verbose_name="欠席理由")



class System(models.Model):

    DAY_OF_WEEKS = [

        ('mon', '月曜日'),
        ('tue', '火曜日'),
        ('wed', '水曜日'),
        ('thu', '木曜日'),
        ('fri', '金曜日'),
        ('sat', '土曜日'),
        ('sun', '日曜日')
    ]

    grade_index = models.IntegerField(default=0)
    chief_id = models.CharField(default="", max_length=100, verbose_name="委員長ID")

    flag_register = models.CharField(default="NULL", max_length=100, verbose_name="フラグレジスタ")

    meeting_DayOfWeek = models.CharField(default="thu", max_length=10, verbose_name="部会の開催翌日の曜日", choices=DAY_OF_WEEKS)

    auth_info_times = models.IntegerField(default=0, verbose_name="認証情報開示回数")