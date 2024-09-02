from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.http import HttpResponse
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import random
import smtplib
from email.message import EmailMessage





# Create your views here.
def home(request):
    return render(request , 'home.html')
def user(request):
    return render(request, 'user.html')
def Doctor(request):
    return render(request, 'doclogin.html')
def signup(request):
    return render(request, 'signup.html')

def Doctorreg(request):
    return render(request,'docregister.html')

# #Authentication
def Usersignup(request):
    if request.method=='POST':
        username = request.POST['username']
        email=request.POST['email']
        name=request.POST['name']
        mobile=request.POST['mobile']
        password=request.POST['password']
        if usrData.objects.filter(username = username).exists():
            messages.info(request , "username already taken")
            return redirect('signup')
        elif usrData.objects.filter(email = email).exists():
            return redirect('signup')
        else:
            user = usrData(username = username , email=email, name=name,mobile=mobile , password=password)
            user.save()
            return redirect('user')
        return render(request , 'user.html')
    
def usrlog(request):
    if request.method == 'POST':
        username = request.POST['username']
        password=request.POST['password']
        try:
            f = usrData.objects.get(username=username,password=password)
            request.session['usr']=f.username
            return redirect('/user_home/')
        except Exception as e:
            return redirect('user')   
        return render(request,'user.html')


def usr_log_session(request):
    doc= Doctor_data.objects.all()
    username = request.session['usr']
    usr=usrData.objects.get(username=username)
    return render(request,'usrp.html',{'user':usr,'docd':doc})




def doclogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password=request.POST['password']
        try:
            f = Doctor_data.objects.get(email=email,password=password)
            request.session['doc']=f.email
            return redirect('/dochome/')
        except Exception as e:
            return redirect('doctor')   
    return render(request,'docregister.html')

def dochome(request):
    apo=user_appointment.objects.all()
    email = request.session['doc']
    doc=Doctor_data.objects.get(email=email)
    fname = doc.fname
    lname=doc.lname
    name=fname+" "+lname
    return render(request,'dochome.html',{'doc':doc,'name':name,'apo':apo})


def Doctorreg(request):
    return render(request,'docregister.html')

def dodocreg(request):
    if request.method == 'POST':
        fname=request.POST['fname']
        lname = request.POST['lname']
        email= request.POST['email']
        gender=request.POST['gender']
        mobile= request.POST['mobile']
        email=request.POST['email']
        specialization = request.POST['spec']
        hospital = request.POST['hop']
        price=request.POST['price']
        address = request.POST['address']
        password=request.POST['password']
        doc = Doctor_data(fname=fname,lname=lname,gender=gender,price=price, email=email,mobile=mobile,specialization=specialization,hospital=hospital,address=address,password=password)
        doc.save()
        return redirect('/doctor/')
    return render(request,'home.html')

def docget_data(request):
    All_data = Doctor_data.objects.all().filter()
    print(All_data)
    data = {
        'key' : All_data
    }
    return render(request , 'All_docdata.html',data)



def usr_appointments(request):
    username = request.session['usr']
    usr=usrData.objects.get(username=username)
    pname=usr.name
    if request.method == 'POST':
        page=request.POST['page']
        date = request.POST['date']
        time = request.POST['time']
        gender=request.POST['gender']
        demail=request.POST['demail']
        pusername=request.POST['pusername']
        problem = request.POST['problem']
        appointment = user_appointment(demail=demail,pname=pname,day=date,time=time,gender=gender,problem=problem,page=page,pusername=pusername)
        appointment.save()
        email=usr.email
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login('bashamasthan31@gmail.com','teqi qyea ovhm unek')
        msg = EmailMessage()
        msg['From'] = 'Quick Info '
        msg['Subject'] = 'About Your Booking Status'
        msg.set_content("Successfully placed your OP \n Thank you for Choosing Our Platform to Improve Your Health \n You will Receive an Conformation Mail from Doctor Shortly..")
        msg['To'] = email
        server.send_message(msg)
        return redirect('/user_home/')
    doc = Doctor_data.objects.all()
    return render(request,'user_appointment.html',{'doc':doc})


def cmsg(request):
    if request.method == 'POST':
        msg = request.POST['msg']

    return redirect('/dochome/')


def logout_view(request):
    logout(request)
    return redirect('/')