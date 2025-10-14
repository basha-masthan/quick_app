#!/usr/bin/env python
"""
Set up Google Maps API key and test geocoding
"""

import os
import requests

def setup_google_maps_api():
    """Set up Google Maps API key"""
    api_key = "AIzaSyDicdx-eDzQ0MeWEmdN_IjLSiXo16HZ2-M"

    # Set environment variable
    os.environ['GOOGLE_MAPS_API_KEY'] = api_key

    print("Google Maps API Key Set Successfully!")
    print(f"API Key: {api_key[:20]}...")
    print()

    # Test the API key
    test_geocoding(api_key)

def test_geocoding(api_key):
    """Test geocoding with a sample address"""
    print("Testing Google Maps Geocoding API...")

    # Test with a known address
    test_address = "Tirupati, Andhra Pradesh, India"

    try:
        response = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json',
            params={
                'address': test_address,
                'key': api_key
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                location = data['results'][0]['geometry']['location']
                lat, lng = location['lat'], location['lng']
                print("[SUCCESS] Geocoding API working!")
                print(f"Test Address: {test_address}")
                print(".6f")
                print("API is ready for use.")
            else:
                print(f"[ERROR] API Error: {data['status']}")
                if 'error_message' in data:
                    print(f"Error Message: {data['error_message']}")
        else:
            print(f"[ERROR] HTTP Error: {response.status_code}")

    except Exception as e:
        print(f"[ERROR] Connection Error: {e}")

if __name__ == "__main__":
    setup_google_maps_api()