from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .triage_service import MedicalTriageService
from .youtube_search import YouTubeSearchService
from functools import wraps
from django.db import models

import smtplib
from email.message import EmailMessage
import os
import requests
from math import radians, sin, cos, asin, sqrt
from django.utils import timezone

# Custom decorators for session-based authentication
def user_login_required(view_func):
    """Decorator to ensure user is logged in"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check for cross-access
        if 'doc' in request.session:
            messages.error(request, "You are logged in as a doctor. Please logout and login as a patient.")
            return redirect('doctor')
        if 'usr' not in request.session:
            messages.error(request, "Please log in as a patient to access this page")
            return redirect('user')
        return view_func(request, *args, **kwargs)
    return wrapper

def doctor_login_required(view_func):
    """Decorator to ensure doctor is logged in"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check for cross-access
        if 'usr' in request.session:
            messages.error(request, "You are logged in as a patient. Please logout and login as a doctor.")
            return redirect('user')
        if 'doc' not in request.session:
            messages.error(request, "Please log in as a doctor to access this page")
            return redirect('doctor')
        return view_func(request, *args, **kwargs)
    return wrapper





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


@user_login_required
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


@user_login_required
def save_coords(request):
    if request.method == 'POST':
        try:
            username = request.session.get('usr')
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

@doctor_login_required
def dochome(request):
    email = request.session['doc']
    doc = Doctor_data.objects.get(email=email)
    fname = doc.fname
    lname = doc.lname
    name = fname + " " + lname
    
    # Get appointments for this doctor (excluding ignored ones)
    apo = user_appointment.objects.filter(demail=email).exclude(status='ignored').order_by('-created_at')
    
    return render(request, 'dochome.html', {'doc': doc, 'name': name, 'apo': apo})


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

@doctor_login_required
def docget_data(request):
    # Only show doctors to other doctors, not to patients
    All_data = Doctor_data.objects.all().filter()
    print(All_data)
    data = {
        'key' : All_data
    }
    return render(request , 'All_docdata.html',data)



@user_login_required
def usr_appointments(request):
    try:
        username = request.session['usr']
        usr = usrData.objects.get(username=username)
        pname = usr.name
        mob = usr.mobile
    except usrData.DoesNotExist:
        messages.error(request, "User not found. Please log in again")
        return redirect('user')
    
    if request.method == 'POST':
        try:
            # Get basic appointment details
            page = request.POST['page']
            date = request.POST['date']
            time = request.POST['time']
            gender = request.POST['gender']
            demail = request.POST['demail']
            pusername = request.POST['pusername']
            problem = request.POST['problem']
            booking_type = request.POST.get('booking_type', 'self')
            booked_by = request.POST.get('booked_by', username)
            
            # Get patient name (can be different from logged-in user)
            patient_name = request.POST.get('pname', pname)
            
            # Validate required fields
            if not all([page, date, time, gender, demail, problem, patient_name]):
                messages.error(request, "Please fill in all required fields")
                return redirect('/usr_appointments/')
            
            # Create appointment with basic details
            appointment = user_appointment(
                booking_type=booking_type,
                booked_by=booked_by,
                demail=demail,
                pname=patient_name,
                day=date,
                time=time,
                gender=gender,
                problem=problem,
                page=page,
                pusername=pusername if booking_type == 'self' else None
            )
            
            # Add additional details for others booking
            if booking_type == 'others':
                appointment.patient_email = request.POST.get('patient_email')
                appointment.patient_mobile = request.POST.get('patient_mobile') or None
                appointment.patient_dob = request.POST.get('patient_dob') or None
                appointment.patient_height_cm = request.POST.get('patient_height_cm') or None
                appointment.patient_weight_kg = request.POST.get('patient_weight_kg') or None
                appointment.patient_blood_group = request.POST.get('patient_blood_group')
                appointment.address = request.POST.get('address')
                appointment.symptoms = request.POST.get('symptoms')
                
                # Health conditions
                appointment.diabetes = bool(request.POST.get('diabetes'))
                appointment.blood_pressure = bool(request.POST.get('blood_pressure'))
                appointment.cholesterol = bool(request.POST.get('cholesterol'))
                appointment.ulcer = bool(request.POST.get('ulcer'))
                appointment.heart_problem = bool(request.POST.get('heart_problem'))
                appointment.liver_problem = bool(request.POST.get('liver_problem'))
                appointment.brain_tumor = bool(request.POST.get('brain_tumor'))
                appointment.cancer_related = bool(request.POST.get('cancer_related'))
            else:
                # For self booking, try to get data from user profile
                try:
                    profile = usr.profile
                    appointment.diabetes = getattr(profile, 'diabetes', False)
                    appointment.blood_pressure = getattr(profile, 'blood_pressure', False)
                    appointment.cholesterol = getattr(profile, 'cholesterol', False)
                    appointment.ulcer = getattr(profile, 'ulcer', False)
                    appointment.heart_problem = getattr(profile, 'heart_problem', False)
                    appointment.liver_problem = getattr(profile, 'liver_problem', False)
                    appointment.brain_tumor = getattr(profile, 'brain_tumor', False)
                    appointment.cancer_related = getattr(profile, 'cancer_related', False)
                    appointment.symptoms = getattr(profile, 'symptoms', '')
                    appointment.address = getattr(profile, 'address', '')
                except:
                    # If no profile exists, leave as default (False)
                    pass
            
            appointment.save()
            
            # Send confirmation email to patient
            try:
                # Determine recipient email
                if booking_type == 'self':
                    recipient_email = usr.email
                    recipient_name = usr.name
                else:
                    recipient_email = appointment.patient_email or usr.email
                    recipient_name = patient_name
                
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login('futurebound.tech@gmail.com', 'vhrb jdtk rdnt widx')
                msg = EmailMessage()
                msg['From'] = 'Quick Info'
                msg['Subject'] = 'Appointment Booked Successfully - Quick Info'
                msg.set_content(f"Dear {recipient_name},\n\nYour appointment has been successfully booked!\n\nAppointment Details:\n- Doctor: {demail}\n- Date: {date}\n- Time: {time}\n- Problem: {problem}\n\nYou will receive a confirmation from the doctor shortly.\n\nThank you for choosing Quick Info for your healthcare needs!")
                msg['To'] = recipient_email
                server.send_message(msg)
                server.quit()
                print(f"Patient email sent successfully to {recipient_email}")
            except Exception as e:
                print(f"Error sending patient email: {e}")
            
            # Send notification email to doctor
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login('futurebound.tech@gmail.com', 'vhrb jdtk rdnt widx')
                msg = EmailMessage()
                msg['From'] = 'Quick Info'
                msg['Subject'] = f'New Appointment Request - {patient_name}'
                
                # Create detailed email content
                email_content = f"""You have a new patient appointment request:

PATIENT DETAILS:
- Name: {patient_name}
- Age: {page}
- Gender: {gender.title()}
- Problem: {problem}
- Date: {date}
- Time: {time}

BOOKING INFORMATION:
- Booked by: {usr.name} ({usr.email})
- Booking type: {'Self' if booking_type == 'self' else 'For someone else'}

"""
                
                # Add additional details for others booking
                if booking_type == 'others':
                    email_content += f"""ADDITIONAL PATIENT INFORMATION:
- Email: {appointment.patient_email or 'Not provided'}
- Mobile: {appointment.patient_mobile or 'Not provided'}
- Date of Birth: {appointment.patient_dob or 'Not provided'}
- Height: {appointment.patient_height_cm or 'Not provided'} cm
- Weight: {appointment.patient_weight_kg or 'Not provided'} kg
- Blood Group: {appointment.patient_blood_group or 'Not provided'}
- Address: {appointment.address or 'Not provided'}

HEALTH CONDITIONS:
- Diabetes: {'Yes' if appointment.diabetes else 'No'}
- Blood Pressure: {'Yes' if appointment.blood_pressure else 'No'}
- Cholesterol: {'Yes' if appointment.cholesterol else 'No'}
- Ulcer: {'Yes' if appointment.ulcer else 'No'}
- Heart Problem: {'Yes' if appointment.heart_problem else 'No'}
- Liver Problem: {'Yes' if appointment.liver_problem else 'No'}
- Brain Tumor: {'Yes' if appointment.brain_tumor else 'No'}
- Cancer Related: {'Yes' if appointment.cancer_related else 'No'}

Additional Symptoms: {appointment.symptoms or 'None provided'}

"""
                else:
                    email_content += f"""CONTACT INFORMATION:
- Patient Email: {usr.email}
- Patient Mobile: {usr.mobile}

"""
                
                email_content += "Please log in to your dashboard to accept/ignore this appointment and provide your response."
                
                msg.set_content(email_content)
                msg['To'] = demail
                server.send_message(msg)
                server.quit()
                print(f"Doctor email sent successfully to {demail}")
            except Exception as e:
                print(f"Error sending doctor email: {e}")
            
            messages.success(request, "Appointment booked successfully!")
            return redirect('/user_home/')
            
        except Exception as e:
            messages.error(request, f"Error booking appointment: {str(e)}")
            print(f"Appointment booking error: {e}")
            return redirect('/usr_appointments/')
    
    # Get all doctors
    doc = Doctor_data.objects.all()
    
    # Get selected doctor from URL parameter
    selected_doctor_email = request.GET.get('doctor', '')
    selected_doctor = None
    if selected_doctor_email:
        try:
            selected_doctor = Doctor_data.objects.get(email=selected_doctor_email)
        except Doctor_data.DoesNotExist:
            selected_doctor = None
    
    return render(request, 'user_appointment.html', {
        'doc': doc, 
        'selected_doctor': selected_doctor,
        'selected_doctor_email': selected_doctor_email
    })


@doctor_login_required
def cmsg(request):
    if request.method == 'POST':
        msg = request.POST['msg']
        # Handle message functionality here if needed

    return redirect('/dochome/')

@doctor_login_required
def update_appointment_status(request):
    """Update appointment status (accept, reject, ignore)"""
    if request.method == 'POST':
        try:
            appointment_id = request.POST.get('appointment_id')
            status = request.POST.get('status')
            
            appointment = user_appointment.objects.get(id=appointment_id, demail=request.session['doc'])
            appointment.status = status
            appointment.save()
            
            return JsonResponse({'success': True, 'message': f'Appointment {status} successfully'})
        except user_appointment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Appointment not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@doctor_login_required
def doctor_reply(request):
    """Doctor reply to appointment"""
    if request.method == 'POST':
        try:
            appointment_id = request.POST.get('appointment_id')
            reply = request.POST.get('reply')
            
            appointment = user_appointment.objects.get(id=appointment_id, demail=request.session['doc'])
            appointment.doctor_reply = reply
            appointment.reply_date = timezone.now()
            appointment.status = 'accepted'  # Auto-accept when doctor replies
            appointment.save()
            
            messages.success(request, "Reply sent successfully!")
            return redirect('/dochome/')
        except user_appointment.DoesNotExist:
            messages.error(request, "Appointment not found")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return redirect('/dochome/')

@user_login_required
def user_dashboard(request):
    """User dashboard to view appointments and doctor replies"""
    try:
        username = request.session['usr']
        usr = usrData.objects.get(username=username)
        
        # Get all appointments booked by this user (both self and others)
        # Handle both old appointments (pusername) and new appointments (booked_by)
        appointments = user_appointment.objects.filter(
            models.Q(booked_by=username) | 
            models.Q(pusername=username)
        ).order_by('-created_at')
        
        # If no appointments found, check for legacy appointments and update them
        if appointments.count() == 0:
            # Check if there are any legacy appointments (empty booked_by and pusername)
            legacy_appointments = user_appointment.objects.filter(booked_by='', pusername='')
            if legacy_appointments.exists():
                # Update legacy appointments with current user
                legacy_appointments.update(booked_by=username, pusername=username)
                # Get updated appointments
                appointments = user_appointment.objects.filter(booked_by=username).order_by('-created_at')
        
        # Get appointment statistics
        total_appointments = appointments.count()
        pending_appointments = appointments.filter(status='pending').count()
        accepted_appointments = appointments.filter(status='accepted').count()
        rejected_appointments = appointments.filter(status='rejected').count()
        completed_appointments = appointments.filter(status='completed').count()
        
        stats = {
            'total': total_appointments,
            'pending': pending_appointments,
            'accepted': accepted_appointments,
            'rejected': rejected_appointments,
            'completed': completed_appointments,
        }
        
        return render(request, 'user_dashboard.html', {
            'user': usr,
            'appointments': appointments,
            'stats': stats
        })
    except usrData.DoesNotExist:
        messages.error(request, "User not found")
        return redirect('user')


def logout_view(request):
    # Clear both user and doctor sessions
    if 'usr' in request.session:
        del request.session['usr']
    if 'doc' in request.session:
        del request.session['doc']
    logout(request)
    return redirect('/')

def unauthorized_access(request):
    """Handle unauthorized access attempts"""
    messages.error(request, "You don't have permission to access this page. Please log in with the correct account type.")
    return redirect('/')

def check_cross_access(request):
    """Check if user is trying to access wrong type of account"""
    if 'usr' in request.session and 'doc' in request.session:
        # Both sessions exist, clear both and redirect
        del request.session['usr']
        del request.session['doc']
        messages.error(request, "Session conflict detected. Please log in again.")
        return redirect('/')
    return None

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