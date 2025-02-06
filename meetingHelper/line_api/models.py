from django.db import models

class Member(models.Model):

    user_id = models.CharField(primary_key=True, max_length=100, verbose_name="ユーザID(LINEID)")
    name = models.CharField(default="", max_length=100, verbose_name="名前")
    grade_class = models.CharField(default="", max_length=100, verbose_name="学年区分")
    absent_flag = models.IntegerField(default=0, verbose_name="欠席連絡フラグ")
    groupsep_flag = models.IntegerField(default=0, verbose_name="グループ分けフラグ")

    absent_reason = models.TextField(default="", max_length=2000, verbose_name="欠席理由")



class System(models.Model):

    grade_index = models.IntegerField(default=0)
    chief_id = models.CharField(default="", max_length=100, verbose_name="委員長ID")

    flag_register = models.CharField(default="NULL", max_length=100, verbose_name="フラグレジスタ")