from ..models import Member

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
    
def MakeGroups(_num_group, _member_list):
    pass