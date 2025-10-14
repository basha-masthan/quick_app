"""
Django management command to fix invalid doctor coordinates using Google Maps API
"""

import os
import requests
from django.core.management.base import BaseCommand
from quickapp.models import Doctor_data

class Command(BaseCommand):
    help = 'Fix invalid doctor coordinates using Google Maps geocoding API'

    def handle(self, *args, **options):
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')

        if not api_key:
            self.stdout.write(
                self.style.ERROR('GOOGLE_MAPS_API_KEY environment variable not set')
            )
            return

        self.stdout.write('Starting doctor coordinate fix...')

        doctors = Doctor_data.objects.all()
        fixed_count = 0

        for doctor in doctors:
            # Check if coordinates are invalid
            if not self._is_valid_coordinates(doctor.latitude, doctor.longitude):
                self.stdout.write(f'Fixing coordinates for: {doctor.fname} {doctor.lname}')

                # Try to geocode the address
                coords = self._geocode_address(doctor.address, api_key)

                if coords:
                    doctor.latitude = coords['lat']
                    doctor.longitude = coords['lng']
                    doctor.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  Updated: {doctor.address} -> lat={coords["lat"]:.6f}, lng={coords["lng"]:.6f}'
                        )
                    )
                    fixed_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  Failed to geocode: {doctor.address}')
                    )
            else:
                self.stdout.write(f'Skipping {doctor.fname} {doctor.lname} - coordinates already valid')

        self.stdout.write(
            self.style.SUCCESS(f'Fixed coordinates for {fixed_count} doctors')
        )

    def _is_valid_coordinates(self, lat, lng):
        """Check if coordinates are within valid ranges"""
        if lat is None or lng is None:
            return False
        return -90 <= lat <= 90 and -180 <= lng <= 180

    def _geocode_address(self, address, api_key):
        """Geocode an address using Google Maps API"""
        try:
            response = requests.get(
                'https://maps.googleapis.com/maps/api/geocode/json',
                params={'address': address, 'key': api_key},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK':
                    location = data['results'][0]['geometry']['location']
                    return {
                        'lat': location['lat'],
                        'lng': location['lng']
                    }

            self.stdout.write(f'  Geocoding failed: {data.get("status", "Unknown error")}')

        except Exception as e:
            self.stdout.write(f'  Geocoding error: {e}')

        return None