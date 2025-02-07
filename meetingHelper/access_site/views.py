import requests
from django.shortcuts import render
from django.http import JsonResponse
import secrets
import urllib.parse
from django.conf import settings
from django.shortcuts import redirect

def index(request):

    return render(request, "access_site/index.html")

def login(request):

    return render(request, "access_site/login.html")

def line_login(request):

    state = secrets.token_urlsafe(16)  # CSRF対策用のランダムな値を生成
    request.session['oauth_state'] = state  # セッションに保存して後で検証

    # LINEログインの認可URLを作成
    line_auth_url = "https://access.line.me/oauth2/v2.1/authorize"
    params = {
        "response_type": "code",
        "client_id": settings.LINE_CHANNEL_ID,  # settings.pyに設定
        "redirect_uri": settings.LINE_REDIRECT_URI,  # settings.pyに設定
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
