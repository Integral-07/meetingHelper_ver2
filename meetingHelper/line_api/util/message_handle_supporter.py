import random
from ..models import Member, System
from itertools import cycle

def isGradeclassFieldEmpty(_user_id):

    member = Member.objects.get(user_id=_user_id)

    if member.grade_class == "":
        return True
    else:
        return False


def isNameFieldEmpty(_user_id):

    member = Member.objects.get(user_id=_user_id)
    
    if member.name == "":
        return True
    else:
        return False
    
def MakeGroups(_num_groups):
    
    """
    メンバを均等にグループ分けする
    :param members: 出席予定のメンバリスト
    :param num_groups: 作成するグループ数
    :return: グループ分けされた辞書
    """
    system = System.objects.get(id=0)
    gradeIndex = system.grade_index

    gradeIndex_first = gradeIndex % 3 + 1
    gradeIndex_second = (gradeIndex + 1) % 3 + 1

    group1 = list(Member.objects.filter(absent_reason="", grade_class="GradeClass" + str(gradeIndex_first)))
    group2 = list(Member.objects.filter(absent_reason="", grade_class="GradeClass" + str(gradeIndex_second)))
    group3 = list(Member.objects.filter(absent_reason="", grade_class="GradeClass" + str(gradeIndex)))

    random.shuffle(group1)
    random.shuffle(group2)
    random.shuffle(group3)

    groups = [[] for _ in range(_num_groups)]

    # ラウンドロビン方式で各グループにメンバを分配
    idx = 0
    for member in group1:
        groups[idx % _num_groups].append(member)
        idx += 1
        
    for member in group2:
        groups[idx % _num_groups].append(member)
        idx += 1

    for member in group3:
        groups[idx % _num_groups].append(member)
        idx += 1


    return groups