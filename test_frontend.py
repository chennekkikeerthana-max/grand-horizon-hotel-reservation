"""
Verify frontend HTML and static assets loading.
"""
import app

def test_frontend_assets():
    client = app.app.test_client()
    
    # 1. Test root page
    r = client.get('/')
    assert r.status_code == 200, f"Expected 200 for /, got {r.status_code}"
    html = r.get_data(as_text=True)
    assert 'Grand Horizon' in html
    assert 'view-dashboard' in html
    assert 'view-reservations' in html
    print("[PASS] Root HTML rendered successfully with all view containers.")
    
    # 2. Test CSS file
    r = client.get('/static/css/styles.css')
    assert r.status_code == 200
    css = r.get_data(as_text=True)
    assert ':root' in css
    print("[PASS] static/css/styles.css loaded successfully.")
    
    # 3. Test JS files
    scripts = [
        '/static/js/api.js',
        '/static/js/app.js',
        '/static/js/components/dashboard.js',
        '/static/js/components/roomTypes.js',
        '/static/js/components/rooms.js',
        '/static/js/components/guests.js',
        '/static/js/components/reservations.js',
        '/static/js/components/payments.js',
        '/static/js/components/staff.js',
        '/static/js/components/reports.js',
        '/static/js/components/dbmsExplorer.js',
    ]
    for s in scripts:
        r = client.get(s)
        assert r.status_code == 200, f"Failed to load {s}, status {r.status_code}"
    print(f"[PASS] All {len(scripts)} JavaScript component files loaded successfully.")

if __name__ == '__main__':
    test_frontend_assets()
