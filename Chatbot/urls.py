from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name="main"),
    path('send_msg/', views.send_msg2),
    path('refresh_chat/', views.refresh_chat),
    path('login/', views.login_user),
    path('logout/', views.logout_user),
    path('change_chat/<str:chat_name>', views.change_chat),
    path('create_chat/', views.create_chat, name="create_chat"),
    path('delete_chat/<str:chat_name>', views.delete_chat),
    path('test_form/', views.test_form),
    path('create_user/', views.create_user),
    path('linebot_test/', views.linebot_test2),
    path('delete_msg/<int:index>', views.delete_msg),
    path('rename_chat/', views.rename_chat),
]