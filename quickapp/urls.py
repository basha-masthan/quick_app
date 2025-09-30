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
    path('Doctorreg/',Doctorreg,name="Doctorreg"),
    path('docreg/',dodocreg  ,name="dodocreg" ),
    path('doclogin/',doclogin  ,name="doclogin" ),
    path('dochome/',dochome),
    path('cmsg/',cmsg),
    path("docgetdata/",docget_data , name="data"),
    path('logout/',logout_view),
    path('save_coords/',save_coords,name='save_coords'),
    path('triage/',triage,name='triage'),
    path('search_videos/',search_videos,name='search_videos'),
]
