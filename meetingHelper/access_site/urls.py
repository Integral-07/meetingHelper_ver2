from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("login/", views.login),
    path("signup/", views.signup, name="signup"),
    path('line/login/', views.line_login, name='line_login'),
    path('line/callback/', views.line_callback, name='line_callback'),
    path('member_list/', views.member_list, name="member_list"), 
    path('member_edit/<member_id>/', views.member_edit, name='member_edit'),
    path('member_delete/<member_id>/', views.member_delete, name='member_delete')
]