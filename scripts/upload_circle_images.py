# -*- coding: utf-8 -*-
"""上传圆专题 10 张插图并关联到新入库的 10 道题（先 SQL 已完成，现走 API）"""
import sys, os, json, time, uuid, re, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://192.168.31.88:18900'
EMAIL = 'ADMIN_EMAIL_PLACEHOLDER'
PASSWORD = 'ADMIN_PASSWORD_PLACEHOLDER'
IMGDIR = r'C:/Users/weifa/Desktop/WorkBuddy下载/圆专题_插图'

def post(path, data, token=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8'),
                               headers={'Content-Type': 'application/json'})
    if token: r.add_header('x-app-token', token)
    return json.loads(urllib.request.urlopen(r, timeout=30).read().decode('utf-8'))['data']

def get(path, token=None):
    r = urllib.request.Request(BASE + path)
    if token: r.add_header('x-app-token', token)
    return json.loads(urllib.request.urlopen(r, timeout=30).read().decode('utf-8'))['data']

def upload(fp, token):
    boundary = '----wb' + uuid.uuid4().hex
    with open(fp, 'rb') as f:
        body = f.read()
    part = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{os.path.basename(fp)}"\r\n'
            f'Content-Type: image/png\r\n\r\n').encode('utf-8') + body + f'\r\n--{boundary}--\r\n'.encode('utf-8')
    r = urllib.request.Request(BASE + '/api/images/upload', data=part,
                               headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
    r.add_header('x-app-token', token)
    return json.loads(urllib.request.urlopen(r, timeout=60).read().decode('utf-8'))['data']

# 等服务就绪
for i in range(20):
    try:
        urllib.request.urlopen(BASE + '/api/health', timeout=3); break
    except Exception: time.sleep(2)
print('服务就绪')

tok = post('/api/auth/login-password', {'email': EMAIL, 'password': PASSWORD})['token']
BANK = 'bk_1c78b98fa76f32bda3'
CH = '第五单元 圆 · 生活情境应用题'

# 拉该章全部题（分页列表带 id+stem）
qmap = {}   # stem归一化 → id
for page in range(1, 20):
    d = get(f'/api/banks/{BANK}/questions?page={page}&size=100', token=tok)
    qs = d.get('questions', [])
    if not qs: break
    for q in qs:
        if q.get('chapter') == CH:
            key = re.sub(r'[\s，。：；、（）()？?！!．.,，“”"]', '', q['stem'])[:30]
            qmap[key] = q['id']
    if page * 100 >= d.get('total', 0): break
print(f'章节内题数: {len(qmap)}')

# 题干前30字 → 图映射（题干开头与 md 顺序一致）
import json as J
DATA = J.load(open(r'C:/Users/weifa/WorkBuddy/2026-11-05-18-17-26/preview_data.json', encoding='utf-8'))
MAP = []
for q in DATA['q1']:
    key = re.sub(r'[\s，。：；、（）()？?！!．.,，“”"]', '', q['stem'])[:30]
    MAP.append((key, os.path.join(IMGDIR, q['img'].split('/')[-1])))

ok = 0
for key, fp in MAP:
    qid = qmap.get(key)
    if not qid:
        print('未找到题:', key[:20]); continue
    r1 = upload(fp, tok)
    r2 = post(f'/api/questions/{qid}/image', {'path': r1['path']}, token=tok)
    print(f'{qid} <- {r1["path"]}  ({os.path.basename(fp)})')
    ok += 1
print(f'\n关联完成 {ok}/10')
