#!/usr/bin/env python
"""
Debug script to check user coordinates and distance calculations
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from quickapp.models import usrData, Doctor_data
from math import radians, sin, cos, asin, sqrt

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using haversine formula"""
    R = 6371  # Earth radius in kilometers

    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    return R * c

def debug_user_coordinates():
    """Debug user coordinates"""
    print("=== USER COORDINATES DEBUG ===")

    users = usrData.objects.all()
    for user in users:
        print(f"\nUser: {user.username} ({user.name})")
        try:
            profile = user.profile
            print(f"  Profile exists: lat={profile.latitude}, lng={profile.longitude}")
            if profile.latitude and profile.longitude:
                print("  Status: COORDINATES SET")
            else:
                print("  Status: COORDINATES MISSING")
        except:
            print("  Status: NO PROFILE EXISTS")

def debug_doctor_coordinates():
    """Debug doctor coordinates"""
    print("\n=== DOCTOR COORDINATES DEBUG ===")

    doctors = Doctor_data.objects.all()
    for doctor in doctors:
        print(f"\nDoctor: {doctor.fname} {doctor.lname}")
        print(f"  Coordinates: lat={doctor.latitude}, lng={doctor.longitude}")
        if doctor.latitude and doctor.longitude:
            if doctor.latitude > 90 or doctor.latitude < -90:
                print("  Status: INVALID LATITUDE")
            elif doctor.longitude > 180 or doctor.longitude < -180:
                print("  Status: INVALID LONGITUDE")
            else:
                print("  Status: VALID COORDINATES")
        else:
            print("  Status: COORDINATES MISSING")

def test_distance_calculation():
    """Test distance calculation with current data"""
    print("\n=== DISTANCE CALCULATION TEST ===")

    # Get first user with coordinates
    users_with_coords = []
    for user in usrData.objects.all():
        try:
            if user.profile.latitude and user.profile.longitude:
                users_with_coords.append(user)
        except:
            pass

    if not users_with_coords:
        print("No users with coordinates found!")
        return

    user = users_with_coords[0]
    user_lat = user.profile.latitude
    user_lng = user.profile.longitude

    print(f"Using user: {user.username} at ({user_lat}, {user_lng})")

    doctors = Doctor_data.objects.all()
    for doctor in doctors:
        print(f"\nDoctor: {doctor.fname} {doctor.lname}")
        if doctor.latitude and doctor.longitude and doctor.latitude <= 90 and doctor.latitude >= -90:
            distance = haversine_distance(user_lat, user_lng, doctor.latitude, doctor.longitude)
            print(".1f")

            # Test speed calculation
            if distance < 5:
                speed = 25.0
            elif distance < 50:
                speed = 45.0
            else:
                speed = 65.0

            travel_time = (distance / speed) * 60
            total_time = travel_time + 10  # 10 min buffer

            print(".0f")
        else:
            print("  ERROR: Invalid or missing coordinates")

if __name__ == "__main__":
    debug_user_coordinates()
    debug_doctor_coordinates()
    test_distance_calculation()