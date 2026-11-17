# -*- coding: utf-8 -*-
"""线上终验：8 道补图题 images 生效 + 4 道迁移题 type=fill"""
import sys, json, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://192.168.31.88:18900'
EMAIL = 'ADMIN_EMAIL_PLACEHOLDER'
PASSWORD = 'ADMIN_PASSWORD_PLACEHOLDER'
BANK = 'bk_1c78b98fa76f32bda3'

def post(path, data, token=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'),
                               headers={'Content-Type': 'application/json'})
    if token: r.add_header('x-app-token', token)
    resp = urllib.request.urlopen(r, timeout=15).read().decode('utf-8')
    return json.loads(resp)['data']

def get(path, token=None):
    r = urllib.request.Request(BASE + path)
    if token: r.add_header('x-app-token', token)
    return json.loads(urllib.request.urlopen(r, timeout=15).read().decode('utf-8'))['data']

tok = post('/api/auth/login-password', {'email': EMAIL, 'password': PASSWORD})['token']

TARGETS = ['q_py6u1_fa3a10818a','q_py6u1_90decb92cb','q_py6u1_92e4fddd9e',
           'q_py6u1_2bbdd4bb4b','q_py6u1_0c7dfff05c','q_py6u1_c00d0dbd5a',
           'q_py6u1_09f7c89a7b','q_exam00294']
CALC = ['q_py6u1_904fa9676d','q_py6u1_47130a17a8','q_py6u1_da054e645b','q_py6u1_60797fe099']

CHAPTERS = ['第一单元 分数乘法 · 培优同步练习（一）','第一单元 分数乘法 · 培优同步练习（二）',
            '第一单元 分数乘法 · 培优同步练习（三）','第一单元 分数乘法 · 培优同步练习（四）',
            '第一单元 分数乘法 · 培优同步练习（五）','第五单元 圆 · 单元检测（一）']

results = {}
for ch in CHAPTERS:
    post(f'/api/banks/{BANK}/practice/reset', {'chapter': ch}, token=tok)
    cq = urllib.parse.quote(ch)
    for i in range(80):
        d = get(f'/api/banks/{BANK}/practice?chapter={cq}', token=tok)
        q = d.get('question')
        if not q: break
        qid = q['id']
        if qid in TARGETS or qid in CALC:
            results[qid] = {'type': q['type'], 'images': q.get('images')}
        a = post(f'/api/banks/{BANK}/practice/answer',
                 {'question_id': qid, 'answer': 'x', 'chapter': ch}, token=tok)
        if a.get('finished'): break

print('== 8 道补图题 ==')
img_ok = 0
for qid in TARGETS:
    r = results.get(qid)
    imgs = r['images'] if r else None
    has = bool(imgs and len(imgs) > 0)
    img_ok += has
    print(qid, '->', imgs if r else '未刷到')
print(f'补图生效: {img_ok}/8')

print()
print('== 4 道迁移题 ==')
type_ok = 0
for qid in CALC:
    r = results.get(qid)
    t = r['type'] if r else '?'
    type_ok += (t == 'fill')
    print(qid, '->', t)
print(f'迁移生效: {type_ok}/4')
