import requests
from django.shortcuts import render
from django.http import JsonResponse
import secrets
import urllib.parse
from django.conf import settings
from django.shortcuts import redirect,  get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from line_api.models import Member, System
from line_api.util.message_handle_supporter import identifyGrade, GradeClass2Grade
from .forms import MemberEditForm, ScheduleEditForm, ChiefEditForm
from linebot import LineBotApi

def index(request):

    return render(request, "access_site/index.html")

def user_login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/meeting_helper_access_site/dash_board/')  # ログイン後のリダイレクト先
        else:
            # 認証失敗時の処理
            messages.error(request, 'Invalid UserName or Password.')
            return redirect("/meeting_helper_access_site/login/")
    else:
        return render(request, 'access_site/login.html', {'error': ''})

"""
def line_login(request):

    state = secrets.token_urlsafe(16)  # CSRF対策用のランダムな値を生成
    request.session['oauth_state'] = state  # セッションに保存して後で検証

    # LINEログインの認可URLを作成
    line_auth_url = "https://access.line.me/oauth2/v2.1/authorize"
    params = {
        "response_type": "code",
        "client_id": settings.LINE_CHANNEL_ID,  # settings.pyに設定
        "redirect_uri": request.build_absolute_uri(),
        "state": state,
        "scope": "profile openid",
        "nonce": secrets.token_urlsafe(16)  # リプレイアタック防止
    }
    auth_url = f"{line_auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


def line_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")

    # CSRF対策の検証
    if state != request.session.get("oauth_state"):
        return JsonResponse({"error": "Invalid state"}, status=400)

    # アクセストークン取得
    token_url = "https://api.line.me/oauth2/v2.1/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.LINE_REDIRECT_URI,
        "client_id": settings.LINE_CHANNEL_ID,
        "client_secret": settings.LINE_CHANNEL_SECRET,
    }
    response = requests.post(token_url, data=data)
    token_info = response.json()

    # ユーザー情報取得
    profile_url = "https://api.line.me/v2/profile"
    headers = {"Authorization": f"Bearer {token_info['access_token']}"}
    profile_response = requests.get(profile_url, headers=headers)
    profile_data = profile_response.json()

    return JsonResponse(profile_data)  # JSONでユーザー情報を返す
"""

def signup(request):

    return render(request, "access_site/signup.html")

@login_required(login_url="/meeting_helper_access_site/login/")
def dash_board(request):


    members = Member.objects.all().order_by("-grade_class")
    nickname_list = []

    for member in members:

        try:
            line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
            profile = line_bot_api.get_profile(member.user_id)
            nick_name = profile.display_name #-> 表示名
        except Exception as e:
            print(e)
            nick_name = "不明"
        nickname_list.append(nick_name)

    first_grade, second_grade, third_grade = GradeClass2Grade()

    day_of_week = System.objects.get(id=0).meeting_DayOfWeek

    chief_id = System.objects.get(id=0).chief_id
    chief_name = Member.objects.get(user_id=chief_id).name
    try:
        line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
        profile = line_bot_api.get_profile(chief_id)
        chief_nickname = profile.display_name #-> 表示名
    except Exception as e:
        print(e)
        chief_nickname = "不明"

    params = {

        "first_grade_class": "GradeClass" + str(first_grade),
        "second_grade_class": "GradeClass" + str(second_grade),
        "third_grade_class": "GradeClass" + str(third_grade),
        "member_info": zip(members, nickname_list),
        "day_of_week": day_of_week,
        "chief_name": chief_name,
        "chief_nickname": chief_nickname
    }

    return render(request, "access_site/users.html", params)

@login_required(login_url="/meeting_helper_access_site/login/")
def member_edit(request, member_id):
    member = get_object_or_404(Member, user_id=member_id)
    
    if request.method == 'POST':
        form = MemberEditForm(request.POST, instance=member)
        if form.is_valid():

            updated_member = Member(user_id=member.user_id, name=form.cleaned_data['name'], grade_class=form.cleaned_data['grade_class'], \
                                        absent_flag=member.absent_flag, groupsep_flag=member.groupsep_flag, absent_reason=form.cleaned_data['absent_reason'])
            updated_member.save()
            return redirect('access_site:dash_board') 
        else:
            form = MemberEditForm(instance=member)

            first_grade, second_grade, third_grade = GradeClass2Grade()

            try:
                line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
                profile = line_bot_api.get_profile(member.user_id)
                nick_name = profile.display_name #-> 表示名
            except Exception as e:
                print(e)
                nick_name = "不明"

            params = {

                "form": form,
                "member": member,
                "nick_name": nick_name,
                "first_grade_class": first_grade,
                "second_grade_class": second_grade,
                "third_grade_class": third_grade,
                "error": "Error occured while update date"
            }

            return render(request, 'access_site/member_edit.html', params)

    else:
        form = MemberEditForm(instance=member)

        first_grade, second_grade, third_grade = GradeClass2Grade()

        try:
            line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
            profile = line_bot_api.get_profile(member.user_id)
            nick_name = profile.display_name #-> 表示名
        except Exception as e:
            print(e)
            nick_name = "不明"

        params = {

            "form": form,
            "member": member,
            "nick_name": nick_name,
            "first_grade_class": first_grade,
            "second_grade_class": second_grade,
            "third_grade_class": third_grade
        }

    return render(request, 'access_site/member_edit.html', params)


@login_required(login_url="/meeting_helper_access_site/login/")
def member_delete(request, member_id):

    member = Member.objects.get(user_id=member_id)
    if request.method == 'POST':
        
        chief_id = System.objects.get(id=0).chief_id
        if chief_id == member_id:

            try:
                line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
                profile = line_bot_api.get_profile(member_id)
                nick_name = profile.display_name #-> 表示名
            except Exception as e:
                print(e)
                nick_name = "不明"
            

            grade = identifyGrade(member.grade_class)

            params = {

                "grade": grade,
                "member": member,
                "nick_name": nick_name,
                "error": "委員長は削除できません"
            }

            return render(request, "access_site/member_delete.html", params)
        
        will_delete_member = get_object_or_404(Member, user_id=member_id)
        will_delete_member.delete()

        return redirect('access_site:dash_board') 
    else:

        try:
            line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
            profile = line_bot_api.get_profile(member_id)
            nick_name = profile.display_name #-> 表示名
        except Exception as e:
            print(e)
            nick_name = "不明"
            

        grade = identifyGrade(member.grade_class)

        params = {

            "grade": grade,
            "member": member,
            "nick_name": nick_name,
        }
    
    return render(request, "access_site/member_delete.html", params)

@login_required(login_url="/meeting_helper_access_site/login/")
def schedule_edit(request):

    system = System.objects.get(id=0)
    if request.method == 'POST':

        form = ScheduleEditForm(request.POST, instance=system)
        if form.is_valid():
            
            updated_system = System(id=system.id, grade_index=system.grade_index, chief_id=system.chief_id, flag_register=system.flag_register, meeting_DayOfWeek=form.cleaned_data['schedule'], auth_info_times=system.auth_info_times)
            updated_system.save()
            
            return redirect('access_site:dash_board') 
        else:

            form = ScheduleEditForm(instance=system)
            params = {
                "form": form,
                "error": "Error occured during updating data"
            }

    else:
        form = ScheduleEditForm(instance=system)
        params = {

            "form": form
        }

    return render(request, "access_site/schedule_edit.html", params)

def chief_edit(request):

    system = System.objects.get(id=0)
    chief = get_object_or_404(Member, user_id=system.chief_id)
    first_grade, second_grade, third_grade = GradeClass2Grade()
    if request.method == 'POST':
        
        selected_option = request.POST.get('next_chief')
        if selected_option:

            updated_system = System(id=system.id, grade_index=system.grade_index, chief_id=selected_option, flag_register=system.flag_register, meeting_DayOfWeek=system.meeting_DayOfWeek, auth_info_times=system.auth_info_times)
            updated_system.save()

            return redirect('access_site:dash_board') 

    
    chief_name = chief.name
    try:
        line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
        profile = line_bot_api.get_profile(system.chief_id)
        chief_nickname = profile.display_name #-> 表示名
    except Exception as e:
        print(e)
        chief_nickname = "不明"

    members = Member.objects.all().order_by("-grade_class")
    params = {

        "chief_name": chief_name,
        "chief_nickname": chief_nickname,
        "members": members,
        "first_grade_class": "GradeClass" + str(first_grade),
        "second_grade_class": "GradeClass" + str(second_grade),
        "third_grade_class": "GradeClass" + str(third_grade)
    }
    
    return render(request, "access_site/chief_edit.html", params)