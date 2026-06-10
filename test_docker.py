import requests, json
base = 'http://localhost:8000'
tests = [
    ('GET /', '/'),
    ('GET /api/stats/summary', '/api/stats/summary'),
    ('GET /api/records', '/api/records?page=1&page_size=3'),
    ('GET /api/stats/monthly', '/api/stats/monthly?year=2026'),
    ('GET /api/stats/weekly', '/api/stats/weekly?year=2026&month=6'),
    ('GET /api/stats/yearly', '/api/stats/yearly'),
    ('GET /api/stats/pace-trend', '/api/stats/pace-trend?period=monthly'),
    ('GET /api/stats/personal-bests', '/api/stats/personal-bests'),
    ('GET /api/goals', '/api/goals'),
    ('GET /api/export/csv', '/api/export/csv'),
    ('GET /api/export/json', '/api/export/json'),
    ('GET /api/goals/year/2026/progress', '/api/goals/year/2026/progress'),
]
ok = fail = err = 0
for name, path in tests:
    try:
        r = requests.get(base + path, timeout=5)
        s = r.status_code
        if s == 200:
            ok += 1
            print(f'[OK] {name} -> {s}')
        else:
            fail += 1
            print(f'[FAIL] {name} -> {s}: {r.text[:150]}')
    except Exception as e:
        err += 1
        print(f'[ERROR] {name} -> {e}')

print('\n--- POST/PUT Tests ---')
try:
    r = requests.post(base + '/api/records', json={'date':'2026-06-10','distance':3.0,'duration':1200,'avg_pace':400.0,'location':'Test','weather':'Sunny','feeling':'Good'}, timeout=5)
    print(f'POST /api/records -> {r.status_code}')
    if r.status_code == 200:
        ok += 1
    else:
        fail += 1
        print(f'  Response: {r.text[:200]}')
except Exception as e:
    err += 1
    print(f'[ERROR] POST /api/records -> {e}')

try:
    r = requests.put(base + '/api/records/1', json={'feeling': 'Great'}, timeout=5)
    print(f'PUT /api/records/1 -> {r.status_code}')
    if r.status_code == 200:
        ok += 1
    else:
        fail += 1
        print(f'  Response: {r.text[:200]}')
except Exception as e:
    err += 1
    print(f'[ERROR] PUT /api/records/1 -> {e}')

print(f'\nOK: {ok}, FAIL: {fail}, ERROR: {err}, Total: {ok+fail+err}')

print('\n--- Frontend Test ---')
try:
    r = requests.get('http://localhost:80', timeout=5)
    print(f'GET http://localhost:80 -> {r.status_code}, length: {len(r.text)}')
    has_vue = 'vue' in r.text.lower() or 'app' in r.text.lower()
    print(f'Contains Vue app markup: {has_vue}')
except Exception as e:
    print(f'[ERROR] Frontend -> {e}')
