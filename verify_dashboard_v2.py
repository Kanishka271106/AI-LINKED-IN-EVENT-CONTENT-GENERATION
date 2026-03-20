import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_new_endpoints():
    print(f"Testing new endpoints at {BASE_URL}...")
    
    # 1. Test Stats
    try:
        r = requests.get(f"{BASE_URL}/api/stats")
        print(f"[OK] /api/stats: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
    except Exception as e:
        print(f"[FAIL] /api/stats: {e}")

    # 2. Test Analytics
    try:
        r = requests.get(f"{BASE_URL}/api/analytics")
        print(f"[OK] /api/analytics: {r.status_code}")
        data = r.json()
        print(f"   Timelines: Events ({len(data['events_timeline'])}), Posts ({len(data['posts_timeline'])})")
        print(f"   Quality: {data['quality_distribution']}")
    except Exception as e:
        print(f"[FAIL] /api/analytics: {e}")

    # 3. Test Events History
    try:
        r = requests.get(f"{BASE_URL}/api/events")
        print(f"[OK] /api/events: {r.status_code}")
        events = r.json().get('events', [])
        print(f"   Found {len(events)} events")
        
        if events:
            ev_id = events[0]['id']
            r_det = requests.get(f"{BASE_URL}/api/events/{ev_id}/images")
            print(f"[OK] /api/events/{ev_id}/images: {r_det.status_code}")
            print(f"   Event Detail Images: {len(r_det.json().get('images', []))}")
    except Exception as e:
        print(f"[FAIL] /api/events history: {e}")

if __name__ == "__main__":
    test_new_endpoints()
