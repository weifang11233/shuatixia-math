# -*- coding: utf-8 -*-
"""上传 8 张配图到线上应用并关联题目"""
import sys, os, json, uuid, mimetypes
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request

BASE = 'http://192.168.31.88:18900'
EMAIL = 'ADMIN_EMAIL_PLACEHOLDER'
PASSWORD = 'ADMIN_PASSWORD_PLACEHOLDER'
IMGDIR = r'C:/Users/weifa/WorkBuddy/2026-11-05-18-17-26/fig_images'

def post_json(path, data, token=None):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})
    if token:
        req.add_header('x-app-token', token)
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode('utf-8'))
        return d.get('data', d) if isinstance(d, dict) else d

def upload_image(fp, token):
    boundary = '----wb' + uuid.uuid4().hex
    fname = os.path.basename(fp)
    with open(fp, 'rb') as f:
        body = f.read()
    part = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{fname}"\r\n'
        f'Content-Type: image/png\r\n\r\n'
    ).encode('utf-8') + body + f'\r\n--{boundary}--\r\n'.encode('utf-8')
    req = urllib.request.Request(BASE + '/api/images/upload', data=part,
                                 headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
    req.add_header('x-app-token', token)
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode('utf-8'))
        return d.get('data', d) if isinstance(d, dict) else d

# 1) 登录
tok = post_json('/api/auth/login-password', {'email': EMAIL, 'password': PASSWORD})['token']
print('登录 OK')

# 2) 题目 → 图片映射
MAP = [
    ('q_py6u1_fa3a10818a', 'seg_q_py6u1_fa3a10818a.png'),
    ('q_py6u1_90decb92cb', 'seg_q_py6u1_90decb92cb.png'),
    ('q_py6u1_92e4fddd9e', 'seg_q_py6u1_92e4fddd9e.png'),
    ('q_py6u1_2bbdd4bb4b', 'seg_q_py6u1_2bbdd4bb4b.png'),
    ('q_py6u1_0c7dfff05c', 'seg_q_py6u1_0c7dfff05c.png'),
    ('q_py6u1_c00d0dbd5a', 'seg_q_py6u1_c00d0dbd5a.png'),
    ('q_py6u1_09f7c89a7b', 'seg_q_py6u1_09f7c89a7b.png'),
    ('q_exam00294',        'cir_q_exam00294.png'),
]

ok = 0
for qid, fname in MAP:
    fp = os.path.join(IMGDIR, fname)
    r1 = upload_image(fp, tok)
    path = r1['path']
    r2 = post_json(f'/api/questions/{qid}/image', {'path': path}, token=tok)
    print(f'{qid} <- {path}  images={r2["images"]}')
    ok += 1
print(f'\n完成 {ok}/{len(MAP)}')
