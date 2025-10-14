#!/usr/bin/env python
"""
Test script to debug what happens in usr_log_session function
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

def simulate_usr_log_session():
    """Simulate what happens in usr_log_session function"""
    print("=== SIMULATING usr_log_session ===")

    # Get user (simulate session)
    username = 'basha'  # From debug output
    try:
        usr = usrData.objects.get(username=username)
        print(f"User found: {usr.username}")
    except usrData.DoesNotExist:
        print("User not found!")
        return

    # Get all doctors
    doc = Doctor_data.objects.all()
    print(f"Total doctors: {len(doc)}")

    # Suggestion engine: rank doctors by patient profile
    suggested = []
    try:
        profile = usr.profile
        print(f"Profile found: lat={profile.latitude}, lng={profile.longitude}")

        hints = []
        if getattr(profile, 'heart_problem', False) or getattr(profile, 'blood_pressure', False) or getattr(profile, 'cholesterol', False):
            hints.append('Cardiologists')
        # ... other hints logic ...

        priority = [d for d in doc if d.specialization in hints]
        others = [d for d in doc if d not in priority]
        suggested = priority + others
        print(f"Hints: {hints}")
        print(f"Priority doctors: {len(priority)}, Other doctors: {len(others)}")

    except Exception as e:
        print(f"Profile access failed: {e}")
        suggested = list(doc)

    print(f"Doctors to process: {len(suggested)}")

    # Distance sort if lat/lng available
    try:
        plat = usr.profile.latitude
        plon = usr.profile.longitude
        print(f"User coordinates: lat={plat}, lng={plon}")

        if plat is not None and plon is not None:
            print("Calculating distances...")

            def doc_distance(d):
                if d.latitude is None or d.longitude is None:
                    return float('inf')
                return haversine_distance(plat, plon, d.latitude, d.longitude)

            # Calculate distance and ETA for each doctor
            for d in suggested:
                print(f"\nProcessing doctor: {d.fname} {d.lname}")
                print(f"  Doctor coords: lat={d.latitude}, lng={d.longitude}")

                if d.latitude is not None and d.longitude is not None:
                    if d.latitude <= 90 and d.latitude >= -90:  # Valid latitude check
                        dist = doc_distance(d)
                        d.distance_km = round(dist, 1)
                        print(f"  Distance calculated: {d.distance_km} km")

                        # Context-aware speed calculation
                        if dist < 5:  # City driving
                            avg_speed_kmh = 25.0
                        elif dist < 50:  # Regional roads
                            avg_speed_kmh = 45.0
                        else:  # Highway
                            avg_speed_kmh = 65.0

                        # Add 10 minutes buffer for parking/appointment setup
                        travel_time_min = (dist / avg_speed_kmh) * 60
                        buffer_time_min = 10
                        d.eta_min = int(max(1, round(travel_time_min + buffer_time_min)))

                        print(f"  ETA calculated: {d.eta_min} min (speed: {avg_speed_kmh} km/h)")
                        print(f"  Template will show: distance_km={d.distance_km}, eta_min={d.eta_min}")
                    else:
                        print("  ERROR: Invalid doctor coordinates (latitude out of range)")
                        d.distance_km = None
                        d.eta_min = None
                else:
                    print("  No doctor coordinates - distance/ETA will be None")
                    d.distance_km = None
                    d.eta_min = None

            # Sort by distance
            suggested = sorted(suggested, key=lambda d: (d.distance_km is None, d.distance_km if d.distance_km is not None else 1e9))
            print("\nDoctors sorted by distance:")
            for i, d in enumerate(suggested):
                dist_info = f"{d.distance_km} km, {d.eta_min} min" if d.distance_km else "No distance data"
                print(f"  {i+1}. {d.fname} {d.lname}: {dist_info}")

        else:
            print("User has no coordinates - distance sorting skipped")

    except Exception as e:
        print(f"Distance calculation failed: {e}")
        import traceback
        traceback.print_exc()

    print(f"\nFinal result: {len(suggested)} doctors returned to template")

if __name__ == "__main__":
    simulate_usr_log_session()