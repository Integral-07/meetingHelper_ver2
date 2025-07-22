from django.urls import path
from . import views
from line_api.views import send_auth_info

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.user_login, name="login"),
    path('dash_board/', views.dash_board, name="dash_board"), 
    path('member_edit/<member_id>/', views.member_edit, name='member_edit'),
    path('member_delete/<member_id>/', views.member_delete, name='member_delete'),
    path("schedule_edit/", views.schedule_edit, name="schedule_edit"),
    path("chief_edit/", views.chief_edit, name="chief_edit"),
    path("send_auth_info/", send_auth_info, name="send_to_chief")
]