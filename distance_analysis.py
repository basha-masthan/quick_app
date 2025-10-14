#!/usr/bin/env python
"""
Detailed analysis of distance and time calculation issues
"""

import os
import sys
import django
import math
from math import radians, sin, cos, asin, sqrt

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from quickapp.models import Doctor_data, usrData, PatientProfile

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

def analyze_coordinates():
    """Analyze coordinate data quality"""
    print("=== DISTANCE & TIME CALCULATION ANALYSIS ===\n")

    # Check doctors
    print("DOCTORS COORDINATE ANALYSIS:")
    print("-" * 50)
    doctors = Doctor_data.objects.all()
    for doctor in doctors:
        lat, lng = doctor.latitude, doctor.longitude
        status = "VALID" if is_valid_coordinates(lat, lng) else "INVALID"
        print(f"{doctor.fname} {doctor.lname}:")
        print(f"  Coordinates: lat={lat}, lng={lng} [{status}]")
        if not is_valid_coordinates(lat, lng):
            print("  ISSUE: Invalid coordinates will break distance calculations")
        print()

    # Check users
    print("USERS COORDINATE ANALYSIS:")
    print("-" * 50)
    users_with_coords = PatientProfile.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    users_without_coords = PatientProfile.objects.filter(latitude__isnull=True, longitude__isnull=True)

    print(f"Users WITH coordinates: {users_with_coords.count()}")
    for profile in users_with_coords:
        lat, lng = profile.latitude, profile.longitude
        status = "VALID" if is_valid_coordinates(lat, lng) else "INVALID"
        print(f"  {profile.user.username}: lat={lat}, lng={lng} [{status}]")

    print(f"\nUsers WITHOUT coordinates: {users_without_coords.count()}")
    for profile in users_without_coords:
        print(f"  {profile.user.username}: No coordinates set")
    print()

def is_valid_coordinates(lat, lng):
    """Check if coordinates are within valid ranges"""
    if lat is None or lng is None:
        return False
    return -90 <= lat <= 90 and -180 <= lng <= 180

def test_distance_calculation():
    """Test distance calculations with sample data"""
    print("DISTANCE CALCULATION TESTING:")
    print("-" * 50)

    # Test with user's coordinates (Tirupati, India area)
    user_lat, user_lng = 14.508240896586742, 79.98318523244404
    print(f"User location: lat={user_lat}, lng={user_lng}")
    print("This appears to be in Tirupati, Andhra Pradesh, India\n")

    # Test with current doctor coordinates
    doctors = Doctor_data.objects.all()
    for doctor in doctors:
        d_lat, d_lng = doctor.latitude, doctor.longitude
        print(f"Doctor: {doctor.fname} {doctor.lname}")
        print(f"  Coordinates: lat={d_lat}, lng={d_lng}")

        if is_valid_coordinates(d_lat, d_lng):
            distance = haversine_distance(user_lat, user_lng, d_lat, d_lng)
            # Test different speeds
            speeds = [30, 40, 50, 60]  # km/h
            print(".1f")
            for speed in speeds:
                time_hours = distance / speed
                time_minutes = time_hours * 60
                print("1.0f")
        else:
            print("  ERROR: Invalid coordinates - distance calculation impossible")
        print()

def analyze_speed_assumptions():
    """Analyze speed assumptions and their impact"""
    print("SPEED ASSUMPTION ANALYSIS:")
    print("-" * 50)

    # Real-world speed considerations
    scenarios = [
        ("City driving", 25, "Stop lights, traffic, urban areas"),
        ("Highway driving", 80, "Open roads, minimal stops"),
        ("Mixed urban/rural", 40, "Current system assumption"),
        ("Traffic congestion", 15, "Rush hour in cities"),
    ]

    print("Different speed assumptions and their impact:")
    for scenario, speed, description in scenarios:
        print("2d")
    print()
    print("RECOMMENDATIONS:")
    print("- Use Google Maps Distance Matrix API for accurate routing")
    print("- Consider traffic conditions and time of day")
    print("- Account for different transportation modes")
    print("- Add buffer time for parking and waiting")

def check_geocoding_setup():
    """Check geocoding API setup"""
    print("GEOCODING SETUP ANALYSIS:")
    print("-" * 50)

    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if api_key:
        print(f"Google Maps API Key: Set (length: {len(api_key)})")
        print("Geocoding should work for new doctor/user creation")
    else:
        print("Google Maps API Key: NOT SET")
        print("ISSUE: New addresses won't be geocoded automatically")
        print("SOLUTION: Set GOOGLE_MAPS_API_KEY environment variable")

    print()

def provide_solutions():
    """Provide detailed solutions"""
    print("=== DETAILED SOLUTIONS ===")
    print()

    print("1. FIX INVALID DOCTOR COORDINATES:")
    print("   - Use admin panel to update doctor addresses")
    print("   - Ensure geocoding works during creation/editing")
    print("   - Manually set coordinates if geocoding fails")
    print()

    print("2. IMPROVE DISTANCE CALCULATION:")
    print("   - Use Google Maps Distance Matrix API instead of haversine")
    print("   - Account for actual driving routes, not straight lines")
    print("   - Consider traffic conditions")
    print()

    print("3. BETTER TIME ESTIMATES:")
    print("   - Use real-time traffic data")
    print("   - Consider different times of day")
    print("   - Add buffer time for parking/appointment setup")
    print()

    print("4. ENHANCE USER EXPERIENCE:")
    print("   - Show distance ranges (nearby, medium, far)")
    print("   - Allow users to filter by maximum travel time")
    print("   - Show alternative transportation options")
    print()

if __name__ == "__main__":
    analyze_coordinates()
    test_distance_calculation()
    analyze_speed_assumptions()
    check_geocoding_setup()
    provide_solutions()