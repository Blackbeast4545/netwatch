import random

class GeoIPLookup:
    def __init__(self):
        # Predefined locations for demo purposes
        self.demo_locations = [
            {'latitude': 40.7128, 'longitude': -74.0060, 'country': 'United States', 'city': 'New York', 'timezone': 'America/New_York'},
            {'latitude': 51.5074, 'longitude': -0.1278, 'country': 'United Kingdom', 'city': 'London', 'timezone': 'Europe/London'},
            {'latitude': 35.6762, 'longitude': 139.6503, 'country': 'Japan', 'city': 'Tokyo', 'timezone': 'Asia/Tokyo'},
            {'latitude': 28.6139, 'longitude': 77.2090, 'country': 'India', 'city': 'New Delhi', 'timezone': 'Asia/Kolkata'},
        ]
        print("Using demo GeoIP lookup (for testing purposes)")

    def get_location(self, ip):
        try:
            # Skip private IP addresses
            if ip.startswith(('10.', '172.', '192.168.', '127.')):
                return None
                
            # Return a random location for demo purposes
            return random.choice(self.demo_locations)
        except Exception as e:
            print(f"GeoIP lookup error for {ip}: {str(e)}")
            return None

    def __del__(self):
        pass