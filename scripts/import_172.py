# -*- coding: utf-8 -*-
"""172 题导入：停容器→拉库→SQL 插入→复刻 reorderBankSeq 排序→验证→传回→起容器
排序逻辑 1:1 复刻 server_online.js 的 reorderBankSeq（数学分支），保证下次服务端重排结果一致。
"""
import sys, re, json, sqlite3, hashlib, datetime
sys.stdout.reconfigure(encoding='utf-8')

WS = r'C:/Users/weifa/WorkBuddy/2026-11-05-18-17-26'
DB_LOCAL = WS + r'/live_work.db'
DATA = json.load(open(WS + '/preview_data.json', encoding='utf-8'))
q1, q2 = DATA['q1'], DATA['q2']

BANK = 'bk_1c78b98fa76f32bda3'
CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}

def cn2num(s):
    if not s: return 99
    if s == '十': return 10
    if s[0] == '十': return 10 + CN.get(s[1], 0)
    if '十' in s:
        a, b = s.split('十')
        return CN.get(a, 1) * 10 + CN.get(b, 0)
    return CN.get(s, 99)

MATH_LESSON = [['分数乘整数', 10], ['一个数乘分数', 11], ['求一个数的几分之几', 12], ['分数连乘', 13], ['倒数', 14],
    ['分数除以整数', 20], ['整数除以分数', 21], ['分数除以分数', 22], ['已知一个数的几分之几', 23], ['分数乘除混合', 24],
    ['比的意义', 30], ['比的基本性质', 31], ['按比例分配', 32],
    ['圆的认识', 40], ['圆的周长', 41], ['圆的面积', 42], ['圆环', 43],
    ['分数四则混合', 50], ['稍复杂的分数乘法', 51],
    ['百分数的意义', 60], ['互化', 61], ['求百分率', 62], ['折扣', 63],
    ['事件发生的可能性', 69], ['可能性大小', 70], ['鸡兔同笼', 80]]
MATH_MIXED = ['单元检测', '单元卷', '综合', '复习', '盘点', '阶段练习', '测试', '期末', '期中', '同步练习']

def math_lesson_rank(ch):
    tail = ch.split('·')[-1] if '·' in ch else ch
    if any(k in tail for k in MATH_MIXED): return 999
    for kw, r in MATH_LESSON:
        if kw in tail: return r
    return 500

def sort_key(chapter, seq, first):
    ch = chapter or ''
    m = re.match(r'^第([一二三四五六七八九十]+)单元', ch)
    if m: return (0, cn2num(m.group(1)), math_lesson_rank(ch), first.get(ch, seq))
    if ch.startswith('回顾整理'): return (1, 0, first.get(ch, seq))
    if ch.startswith('智慧广场'): return (2, 0, first.get(ch, seq))
    if ch.startswith('教材外'): return (3, 0, first.get(ch, seq))
    return (4, 0, first.get(ch, seq))

# ===== chapter 生成 =====
FIX = {
    'K01': '第一单元 分数乘法', 'K02': '第一单元 分数乘法', 'K03': '第一单元 分数乘法', 'K04': '第一单元 分数乘法',
    'K05': '智慧广场——鸡兔同笼问题', 'K06': '第三单元 分数除法', 'K07': '第三单元 分数除法',
    'K08': '第三单元 分数除法', 'K09': '第三单元 分数除法', 'K10': '第六单元 分数四则混合运算',
    'K11': '第四单元 比', 'K12': '第四单元 比', 'K13': '第四单元 比', 'K14': '智慧广场——鸡兔同笼问题',
    'K15': '第五单元 圆', 'K16': '第五单元 圆', 'K17': '第五单元 圆',
    'K18': '第六单元 分数四则混合运算', 'K19': '第六单元 分数四则混合运算',
    'K20': '第六单元 分数四则混合运算', 'K21': '第六单元 分数四则混合运算',
    'K22': '第二单元 可能性', 'K23': '第二单元 可能性', 'K24': '第七单元 百分数（一）',
    'K25': '第七单元 百分数（一）', 'K26': '第七单元 百分数（一）', 'K27': '智慧广场——鸡兔同笼问题',
}

def norm(s):
    return re.sub(r'[\s，。：；、（）()？?！!．.,，“”"]', '', s)[:60]

conn = sqlite3.connect(DB_LOCAL)
c = conn.cursor()
ex_norm = set(norm(r[0]) for r in c.execute("SELECT stem FROM questions WHERE bank_id=?", (BANK,)))
newq = []          # (chapter, stem, answer, explanation, img_file or None)

# md1 圆专题
for q in q1:
    chapter = '第五单元 圆 · 生活情境应用题'
    stem = q['stem']
    if norm(stem) in ex_norm:
        print('跳过重复(md1):', stem[:30]); continue
    exp = (q.get('explanation') or '').strip()
    newq.append([chapter, stem, q['answer'], ('易错提醒：' + exp) if exp else None,
                 q['img'].split('/')[-1] if q.get('img') else None])

# md2 阶梯训练
for q in q2:
    kno = q['k'].split(' ')[0]
    kname = q['k'].split(' ', 1)[1]
    chapter = f"{FIX[kno]} · 阶梯训练 · {kname}"
    stem = q['stem']
    if norm(stem) in ex_norm:
        print('跳过重复(md2):', stem[:30]); continue
    exp = f"【{q['lv']}】{q['model']}" if q.get('model') else f"【{q['lv']}】"
    newq.append([chapter, stem, q['answer'], exp, None])

print('去重后待插入:', len(newq), '题')

# ===== 插入（seq 续排，created_at 与库内同格式）=====
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
maxseq = c.execute("SELECT COALESCE(MAX(seq),0) FROM questions WHERE bank_id=?", (BANK,)).fetchone()[0]
c.execute("SELECT id FROM users WHERE role='admin' LIMIT 1")  # 确认 admin 存在
rows = []
for i, (chapter, stem, answer, exp, img) in enumerate(newq):
    qid = 'q_md16_' + hashlib.sha1(f'{stem}|{i}'.encode()).hexdigest()[:14]
    rows.append((qid, BANK, maxseq + 1 + i, 'solve', stem, None, answer, exp, chapter, '数学', '六年级', 1.0, now))
c.executemany(
    'INSERT INTO questions (id,bank_id,seq,type,stem,options,answer,explanation,chapter,subject,grade,confidence,created_at) '
    'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', rows)
print('已插入:', len(rows))

# ===== 复刻 reorderBankSeq =====
all_rows = c.execute("SELECT id, chapter, seq FROM questions WHERE bank_id=?", (BANK,)).fetchall()
first = {}
for qid, ch, seq in all_rows:
    if ch not in first or seq < first[ch]: first[ch] = seq
ordered = sorted(all_rows, key=lambda r: sort_key(r[1], r[2], first) + (r[2],))
conn.commit()  # 结束隐式事务后再显式 BEGIN
c.execute("BEGIN")
updates = [(i + 1, qid) for i, (qid, ch, seq) in enumerate(ordered) if seq != i + 1]
c.executemany("UPDATE questions SET seq=? WHERE id=?", updates)
c.execute("DELETE FROM practice_progress WHERE bank_id=?", (BANK,))
c.execute("DELETE FROM chapter_progress WHERE bank_id=?", (BANK,))
c.execute("COMMIT")
print(f'重排完成，更新 {len(updates)} 行')

# 验证：新题 seq 连续 + 章节首题单调
c.execute("UPDATE question_banks SET total_count=(SELECT COUNT(*) FROM questions WHERE bank_id=?), updated_at=? WHERE id=?", (BANK, now, BANK))
print('total_count:', c.execute("SELECT total_count FROM question_banks WHERE id=?", (BANK,)).fetchone()[0])
print('integrity:', c.execute('PRAGMA integrity_check').fetchone()[0])
# 章节序抽查
seen = []
for seq, ch in c.execute("SELECT seq, chapter FROM questions WHERE bank_id=? ORDER BY seq", (BANK,)):
    u = (ch or '').split(' · ')[0]
    if not seen or seen[-1][1] != u: seen.append((seq, u))
print('单元出现顺序:', [f'{s}{u}' for s, u in seen[:12]])
conn.commit()
conn.close()
