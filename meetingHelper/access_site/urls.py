from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("login/", views.login),
    path("signup/", views.signup, name="signup"),
    path('line/login/', views.line_login, name='line_login'),
    path('line/callback/', views.line_callback, name='line_callback'),
]