from django.urls import path
from .import views
from django.contrib import admin

urlpatterns = [
    path("adminlogin/", views.admin_login, name="adminlogin"),
    path("adminhome/", views.admin_home, name="adminhome"),
    path("usermanage/", views.user_manage, name="usermanage"),
    path("blockuser/<str:id>", views.block_user, name="blockuser"),
    path("unblockuser/<str:id>", views.un_block_user, name="unblockuser"),
    path("searchuser/", views.search_for_user, name="searchuser"),
]
