# -*- coding: utf-8 -*-
"""重新关联 8 道补图题（图片文件已在 NAS 磁盘上，仅重建 DB 关联）"""
import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://192.168.31.88:18900'
EMAIL = 'ADMIN_EMAIL_PLACEHOLDER'
PASSWORD = 'ADMIN_PASSWORD_PLACEHOLDER'

def post(path, data, token=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'),
                               headers={'Content-Type': 'application/json'})
    if token: r.add_header('x-app-token', token)
    return json.loads(urllib.request.urlopen(r, timeout=15).read().decode('utf-8'))['data']

tok = post('/api/auth/login-password', {'email': EMAIL, 'password': PASSWORD})['token']

# 第一轮上传返回的路径（文件已在 NAS data/images/ 目录）
MAP = [
    ('q_py6u1_fa3a10818a', '/api/images/img_1794803973448_2b2c33bb.png'),
    ('q_py6u1_90decb92cb', '/api/images/img_1794803973526_b57175d9.png'),
    ('q_py6u1_92e4fddd9e', '/api/images/img_1794803973575_38962b69.png'),
    ('q_py6u1_2bbdd4bb4b', '/api/images/img_1794803973609_46c45aea.png'),
    ('q_py6u1_0c7dfff05c', '/api/images/img_1794803973638_98a603eb.png'),
    ('q_py6u1_c00d0dbd5a', '/api/images/img_1794803973668_bd973457.png'),
    ('q_py6u1_09f7c89a7b', '/api/images/img_1794803973722_5f519da5.png'),
    ('q_exam00294',        '/api/images/img_1794803973773_fb562768.png'),
]
for qid, path in MAP:
    r = post(f'/api/questions/{qid}/image', {'path': path}, token=tok)
    print(qid, '->', r['images'])
print('重新关联完成')
