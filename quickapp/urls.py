"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from .views import *

urlpatterns = [
    path('', home,name="home"),
    path('user/', user, name="user"),
    path('doctor/',Doctor,name="doctor"),
    path('signup/',signup ,name="signup"),
    path('Usersignup/',Usersignup, name="Usersignup"),
    path('login/',usrlog),
    path('user_home/',usr_log_session),
    path('usr_appointments/',usr_appointments),
    path('user_dashboard/',user_dashboard,name='user_dashboard'),
    path('Doctorreg/',Doctorreg,name="Doctorreg"),
    path('docreg/',dodocreg  ,name="dodocreg" ),
    path('doclogin/',doclogin  ,name="doclogin" ),
    path('dochome/',dochome),
    path('cmsg/',cmsg),
    path('update_appointment_status/',update_appointment_status,name='update_appointment_status'),
    path('doctor_reply/',doctor_reply,name='doctor_reply'),
    path("docgetdata/",docget_data , name="data"),
    path('logout/',logout_view),
    path('save_coords/',save_coords,name='save_coords'),
    path('triage/',triage,name='triage'),
    path('search_videos/',search_videos,name='search_videos'),
    path('unauthorized/',unauthorized_access,name='unauthorized'),
    path('admin_login/', admin_login, name='admin_login'),
    path('admin_logout/', admin_logout, name='admin_logout'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin_doctors/', admin_doctors, name='admin_doctors'),
    path('admin_doctor_create/', admin_doctor_create, name='admin_doctor_create'),
    path('admin_doctor_edit/<str:fname>/', admin_doctor_edit, name='admin_doctor_edit'),
    path('admin_doctor_delete/<str:fname>/', admin_doctor_delete, name='admin_doctor_delete'),
    path('admin_users/', admin_users, name='admin_users'),
    path('admin_user_create/', admin_user_create, name='admin_user_create'),
    path('admin_user_edit/<str:username>/', admin_user_edit, name='admin_user_edit'),
    path('admin_user_delete/<str:username>/', admin_user_delete, name='admin_user_delete'),
    path('admin_appointments/', admin_appointments, name='admin_appointments'),
    path('admin_appointment_edit/<int:appointment_id>/', admin_appointment_edit, name='admin_appointment_edit'),
    path('admin_appointment_delete/<int:appointment_id>/', admin_appointment_delete, name='admin_appointment_delete'),
]
