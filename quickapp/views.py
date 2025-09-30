from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .triage_service import MedicalTriageService
from .youtube_search import YouTubeSearchService

import smtplib
from email.message import EmailMessage
import os
import requests
from math import radians, sin, cos, asin, sqrt





# Create your views here.
def home(request):
    return render(request , 'home.html')
def user(request):
    return render(request, 'user.html')
def Doctor(request):
    return render(request, 'doclogin.html')
def signup(request):
    return render(request, 'signup.html')

def triage(request):
    if request.method == 'POST':
        text = request.POST.get('q','')
        if not text.strip():
            return redirect('/')
        
        # Initialize enhanced triage service
        triage_service = MedicalTriageService()
        
        # Get enhanced NLP analysis
        triage_result = triage_service.analyze_symptoms(text)
        
        # Get doctors filtered by suggested specialties
        doctors = Doctor_data.objects.all()
        if triage_result.suggested_specialties:
            priority = [d for d in doctors if d.specialization in triage_result.suggested_specialties]
            others = [d for d in doctors if d not in priority]
            doctors = priority + others

        return render(request, 'home.html', {
            'triage_text': text,
            'triage_action': triage_result.action,
            'triage_severity': triage_result.severity,
            'triage_message': triage_result.message,
            'immediate_actions': triage_result.immediate_actions,
            'video_recommendations': triage_result.video_recommendations,
            'triage_doctors': doctors[:6],
        })
    return redirect('/')

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
        # profile fields
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        height_cm = request.POST.get('height_cm') or None
        weight_kg = request.POST.get('weight_kg') or None
        blood_group = request.POST.get('blood_group')
        diabetes = bool(request.POST.get('diabetes'))
        blood_pressure = bool(request.POST.get('blood_pressure'))
        cholesterol = bool(request.POST.get('cholesterol'))
        ulcer = bool(request.POST.get('ulcer'))
        heart_problem = bool(request.POST.get('heart_problem'))
        liver_problem = bool(request.POST.get('liver_problem'))
        brain_tumor = bool(request.POST.get('brain_tumor'))
        cancer_related = bool(request.POST.get('cancer_related'))
        symptoms = request.POST.get('symptoms')
        address = request.POST.get('address')
        if usrData.objects.filter(username = username).exists():
            messages.info(request , "username already taken")
            return redirect('signup')
        elif usrData.objects.filter(email = email).exists():
            return redirect('signup')
        else:
            user = usrData(username = username , email=email, name=name,mobile=mobile , password=password)
            user.save()
            # create profile
            profile_kwargs = dict(
                user=user,
                gender=gender or None,
                blood_group=blood_group or None,
                diabetes=diabetes,
                blood_pressure=blood_pressure,
                cholesterol=cholesterol,
                ulcer=ulcer,
                heart_problem=heart_problem,
                liver_problem=liver_problem,
                brain_tumor=brain_tumor,
                cancer_related=cancer_related,
                symptoms=symptoms or None,
            )
            if height_cm: profile_kwargs['height_cm'] = int(height_cm)
            if weight_kg: profile_kwargs['weight_kg'] = int(weight_kg)
            if dob: profile_kwargs['dob'] = dob
            # geocode address
            lat = lon = None
            if address:
                try:
                    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
                    if api_key:
                        resp = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params={'address': address, 'key': api_key}, timeout=10)
                        data = resp.json()
                        if data.get('status') == 'OK':
                            loc = data['results'][0]['geometry']['location']
                            lat, lon = loc['lat'], loc['lng']
                except Exception:
                    pass
            PatientProfile.objects.create(address=address or None, latitude=lat, longitude=lon, **profile_kwargs)
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
    # Suggestion engine: rank doctors by patient profile
    suggested = []
    try:
        profile = usr.profile
        hints = []
        if getattr(profile, 'heart_problem', False) or getattr(profile, 'blood_pressure', False) or getattr(profile, 'cholesterol', False):
            hints.append('Cardiologists')
        if getattr(profile, 'liver_problem', False):
            hints.append('General Medicine')
        if getattr(profile, 'brain_tumor', False):
            hints.append('Neurologists')
        if getattr(profile, 'ulcer', False):
            hints.append('General Medicine')
        if getattr(profile, 'cancer_related', False):
            hints.append('Oncologist')
        if getattr(profile, 'diabetes', False):
            hints.append('General Medicine')
        # naive symptom keyword mapping
        if profile.symptoms:
            s = profile.symptoms.lower()
            if 'skin' in s or 'rash' in s: hints.append('Dermatologists')
            if 'tooth' in s or 'teeth' in s or 'gum' in s: hints.append('Dentist')
            if 'bone' in s or 'joint' in s or 'fracture' in s: hints.append('Orthopedic')
            if 'eye' in s or 'vision' in s: hints.append('Ophthalmologist')
            if 'pregnan' in s or 'gyne' in s: hints.append('Gynecologist')
            if 'child' in s or 'pediatric' in s: hints.append('Pediatrician')
        priority = [d for d in doc if d.specialization in hints]
        others = [d for d in doc if d not in priority]
        suggested = priority + others
    except Exception:
        suggested = list(doc)
    # distance sort if lat/lng available
    try:
        plat = usr.profile.latitude
        plon = usr.profile.longitude
        if plat is not None and plon is not None:
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371
                dlat = radians(lat2-lat1)
                dlon = radians(lon2-lon1)
                a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
                c = 2*asin(sqrt(a))
                return R*c
            def doc_distance(d):
                if d.latitude is None or d.longitude is None:
                    return float('inf')
                return haversine(plat, plon, d.latitude, d.longitude)
            # compute distance and rough ETA (driving ~30km/h)
            for d in suggested:
                if d.latitude is not None and d.longitude is not None:
                    dist = doc_distance(d)
                    d.distance_km = round(dist, 1)
                    avg_speed_kmh = 30.0
                    d.eta_min = int(max(1, round((dist / avg_speed_kmh) * 60)))
                else:
                    d.distance_km = None
                    d.eta_min = None
            suggested = sorted(suggested, key=lambda d: (d.distance_km is None, d.distance_km if d.distance_km is not None else 1e9))
    except Exception:
        pass
    return render(request,'usrp.html',{'user':usr,'docd':suggested})


def save_coords(request):
    if request.method == 'POST':
        try:
            username = request.session.get('usr')
            if not username:
                return redirect('user')
            usr = usrData.objects.get(username=username)
            lat = request.POST.get('lat')
            lon = request.POST.get('lon')
            if lat and lon:
                profile = getattr(usr, 'profile', None)
                if profile is None:
                    profile = PatientProfile.objects.create(user=usr)
                profile.latitude = float(lat)
                profile.longitude = float(lon)
                profile.save()
        except Exception:
            pass
        return redirect('/user_home/')




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
        map_embed = request.POST.get('map_embed')
        # optional manual lat/lng
        lat_in = request.POST.get('latitude')
        lng_in = request.POST.get('longitude')
        # persist manual lat/lng if provided
        doc = Doctor_data(
            fname=fname,
            lname=lname,
            gender=gender,
            price=price,
            email=email,
            mobile=mobile,
            specialization=specialization,
            hospital=hospital,
            address=address,
            password=password,
            map_embed=map_embed,
            latitude=float(lat_in) if lat_in else None,
            longitude=float(lng_in) if lng_in else None,
        )
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
    mob=usr.mobile
    # str(mob)
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
        msg['Subject'] = 'Congratulations You have new patient - OP Request!'
        msg.set_content("Successfully placed your OP \n Thank you for Choosing Our Platform to Improve Your Health \n You will Receive an Conformation Mail from Doctor Shortly..")
        msg['To'] = email
        server.send_message(msg)
        server.quit()
        print(email+" Patient mail sent successfully")
        # Doctor Notification

        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login('bashamasthan31@gmail.com','teqi qyea ovhm unek')
        msg = EmailMessage()
        msg['From'] = 'Quick Info '
        msg['Subject'] = 'About Your Booking Status'
        msg.set_content(f"You have a new patient appointment \n Name : "+ pname + " Sex: "+ gender +"\n Problem :" + problem + " \n Mobile : %d \n Gmail %s " %(mob,usr.email))
        msg['To'] = demail
        server.send_message(msg)
        server.quit()

        print(demail+" Doctor mail sent successfully")
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

def search_videos(request):
    """AJAX endpoint for searching YouTube videos based on user input"""
    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        if not query:
            return JsonResponse({'videos': [], 'error': 'No query provided'})
        
        try:
            youtube_search = YouTubeSearchService()
            videos = youtube_search.search_medical_videos(query, max_results=6)
            
            # Format videos for frontend
            formatted_videos = []
            for video in videos:
                formatted_videos.append({
                    'title': video['title'],
                    'video_id': video['video_id'],
                    'description': video['description'],
                    'thumbnail': video.get('thumbnail', ''),
                    'channel_title': video.get('channel_title', ''),
                    'embed_url': youtube_search.get_video_embed_url(video['video_id']),
                    'watch_url': youtube_search.get_video_watch_url(video['video_id'])
                })
            
            return JsonResponse({'videos': formatted_videos})
            
        except Exception as e:
            return JsonResponse({'videos': [], 'error': str(e)})
    
    return JsonResponse({'videos': [], 'error': 'Invalid request method'})