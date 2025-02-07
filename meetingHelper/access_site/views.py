import requests
from django.shortcuts import render
from django.http import JsonResponse
import secrets
import urllib.parse
from django.conf import settings
from django.shortcuts import redirect,  get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from line_api.models import Member, System
from line_api.util.message_handle_supporter import identifyGrade, GradeClass2Grade
from .forms import MemberEditForm
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
            return redirect('/meeting_helper_access_site/member_list/')  # ログイン後のリダイレクト先
        else:
            # 認証失敗時の処理
            return render(request, 'access_site/login.html', {'error': 'Invalid UserName or Password.'})
    else:
        return render(request, 'access_site/login.html', {'error': ''})

def line_login(request):

    state = secrets.token_urlsafe(16)  # CSRF対策用のランダムな値を生成
    request.session['oauth_state'] = state  # セッションに保存して後で検証

    # LINEログインの認可URLを作成
    line_auth_url = "https://access.line.me/oauth2/v2.1/authorize"
    params = {
        "response_type": "code",
        "client_id": settings.LINE_CHANNEL_ID,  # settings.pyに設定
        "redirect_uri": request.build_abusolute_uri(),
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

def signup(request):

    return render(request, "access_site/signup.html")

@login_required(login_url="/meeting_helper_access_site/login/")
def member_list(request):


    members = Member.objects.all().order_by("-grade_class")
    nickname_list = []

    for member in members:

        try:
            line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
            profile = line_bot_api.get_profile(member.user_id)
            nick_name = profile.display_name #-> 表示名
        except:
            nick_name = "不明"
        nickname_list.append(nick_name)

    first_grade, second_grade, third_grade = GradeClass2Grade()

    params = {

        "first_grade_class": "GradeClass" + str(first_grade),
        "second_grade_class": "GradeClass" + str(second_grade),
        "third_grade_class": "GradeClass" + str(third_grade),
        "member_info": zip(members, nickname_list)
    }

    return render(request, "access_site/users.html", params)

@login_required(login_url="/meeting_helper_access_site/login/")
def member_edit(request, member_id):
    member = get_object_or_404(Member, user_id=member_id)
    
    if request.method == 'POST':
        form = MemberEditForm(request.POST, instance=member)
        if form.is_valid():
            #form.save()
            updated_member = Member(user_id=member.user_id, name=form.cleaned_data['name'], grade_class=form.cleaned_data['grade_class'], absent_flag=member.absent_flag, groupsep_flag=member.groupsep_flag, absent_reason=member.absent_reason)
            updated_member.save()
            return redirect('member_list')  # メンバー一覧ページにリダイレクト
        else:
            form = MemberEditForm(instance=member)

            first_grade, second_grade, third_grade = GradeClass2Grade()

            try:
                line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
                profile = line_bot_api.get_profile(member.user_id)
                nick_name = profile.display_name #-> 表示名
            except:
                nick_name = "不明"

            params = {

                "form": form,
                "member": member,
                "nick_name": nick_name,
                "first_grade_class": first_grade,
                "second_grade_class": second_grade,
                "third_grade_class": third_grade
            }

            return render(request, 'access_site/member_edit.html', {"error": "Error occured while update date"})

    else:
        form = MemberEditForm(instance=member)

        first_grade, second_grade, third_grade = GradeClass2Grade()

        try:
            line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
            profile = line_bot_api.get_profile(member.user_id)
            nick_name = profile.display_name #-> 表示名
        except:
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

    if request.method == 'POST':
        
        will_delete_member = get_object_or_404(Member, user_id=member_id)
        will_delete_member.delete()

        return redirect('member_list')  # メンバー一覧ページにリダイレクト
    else:

        member = Member.objects.get(user_id=member_id)

        try:
            line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
            profile = line_bot_api.get_profile(member_id)
            nick_name = profile.display_name #-> 表示名
        except:
            nick_name = "不明"
            

        grade = identifyGrade(member.grade_class)
        

        params = {

            "grade": grade,
            "member": member,
            "nick_name": nick_name,
        }
    
    return render(request, "access_site/member_delete.html", params)