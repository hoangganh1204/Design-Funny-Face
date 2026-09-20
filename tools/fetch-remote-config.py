#!/usr/bin/env python3
"""fetch-remote-config.py — pull an app's Firebase Remote Config exactly like the app does,
using the Google keys embedded in the APK. Returns every remote param: asset tokens, remote
content lists (JSON), and A/B flags. No login required.

Auto-reads the keys from the decompiled strings.xml, or pass them explicitly:
    python3 fetch-remote-config.py --res <App>/decompiled/resources/res      # auto
    python3 fetch-remote-config.py --api-key AIza... --app-id 1:NNN:android:xxx
Output: JSON of {param: value} to stdout (also saved to /tmp/rc.json). Keep tokens out of git.
"""
import json, re, sys, os, urllib.request

def read_keys_from_res(res):
    s = open(os.path.join(res, 'values/strings.xml'), encoding='utf-8').read()
    g = lambda n: (re.search(r'<string name="%s">([^<]*)' % n, s) or [None, None])[1]
    return g('google_api_key'), g('google_app_id')

def fetch(api_key, app_id, fid='reskin-fetch-0000000000'):
    proj = app_id.split(':')[1]                       # project number
    url = ('https://firebaseremoteconfig.googleapis.com/v1/projects/%s/namespaces/'
           'firebase:fetch?key=%s' % (proj, api_key))
    body = json.dumps({'appId': app_id, 'appInstanceId': fid}).encode()
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def main():
    a = sys.argv
    if '--res' in a:
        api_key, app_id = read_keys_from_res(a[a.index('--res') + 1])
    else:
        api_key = a[a.index('--api-key') + 1]; app_id = a[a.index('--app-id') + 1]
    if not api_key or not app_id: sys.exit('missing google_api_key / google_app_id')
    r = fetch(api_key, app_id)
    ent = r.get('entries', {})
    json.dump({'entries': ent}, open('/tmp/rc.json', 'w'))
    print('state:', r.get('state'), '· params:', len(ent), '· saved /tmp/rc.json', file=sys.stderr)
    for k in sorted(ent): print(' ', k, file=sys.stderr)
    print(json.dumps(ent, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
