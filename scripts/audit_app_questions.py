# -*- coding: utf-8 -*-
"""应用题真实审计：数学库 solve 题型逐题检查（图需求 + 应用题特征）"""
import sqlite3, re, io, sys
sys.stdout.reconfigure(encoding='utf-8')

DB = r'C:/Users/weifa/WorkBuddy/2026-11-05-18-17-26/shuatixia-kids.db'
BANK = 'bk_1c78b98fa76f32bda3'
conn = sqlite3.connect(DB)
c = conn.cursor()

print('== 题库总览 ==')
for r in c.execute("SELECT id, subject, grade, total_count FROM question_banks"):
    print(r)

print('\n== 数学库 type 分布 ==')
dist = dict(c.execute("SELECT type, COUNT(*) FROM questions WHERE bank_id=? GROUP BY type", (BANK,)).fetchall())
print(dist)

print('\n== 数学库 solve 图字段状态 ==')
c.execute("SELECT COUNT(*) FROM questions WHERE bank_id=? AND type='solve'", (BANK,))
total_solve = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM questions WHERE bank_id=? AND type='solve' AND images IS NOT NULL AND images NOT IN ('','[]','null')", (BANK,))
with_img = c.fetchone()[0]
print(f'solve总数={total_solve}, 有图={with_img}, 无图={total_solve-with_img}')

# 需要"看图"才能作答的关键词（真缺图判定）
FIG = re.compile('如图|下图|看图|右图|左图|图中|图上|图里|示意图|线段图|统计图|条形图|扇形图|钟面|画一画|涂一涂|折一折|剪一剪|拼一拼|摆一摆|量一量|数一数|连一连|量得|刻度')
# 非应用题特征（纯计算/概念/指令式）
CALC = re.compile(r'脱式|口算|竖式计算|直接写出得数|计算下面|计算下列|简便计算|怎样算|只列式|估算')
def stem_is_bare_expr(s):
    t = re.sub(r'[\s\d\.\+\-\*×÷/＝=()（）①②③④⑤⑥⑦⑧⑨⑩]', '', s)
    return len(t) <= 3

c.execute("SELECT id, chapter, stem, answer, seq FROM questions WHERE bank_id=? AND type='solve' ORDER BY seq", (BANK,))
rows = c.fetchall()
print(f'\n== 拉取 solve 题干 {len(rows)} 条 ==')

fig_rows = [r for r in rows if FIG.search(r[2])]
print(f'题干含图/操作关键词（真缺图候选）: {len(fig_rows)}')
for r in fig_rows:
    print(' [图]', r[0], '|', r[1], '|', r[2][:80].replace('\n', ' '))

calc_rows = [r for r in rows if CALC.search(r[2]) or stem_is_bare_expr(r[2])]
print(f'\n疑似纯计算/指令式（非应用题候选）: {len(calc_rows)}')
for r in calc_rows:
    print(' [?]', r[0], '|', r[1], '|', r[2][:80].replace('\n', ' '))

print('\n== solve 章节分布 ==')
chap = {}
for r in rows:
    key = r[1].split(' · ')[0] if r[1] else '(空)'
    chap[key] = chap.get(key, 0) + 1
for k, v in sorted(chap.items()):
    print(f'  {k}: {v}')

print('\n== 其他库 solve 分布 ==')
for r in c.execute("SELECT bank_id, COUNT(*) FROM questions WHERE type='solve' GROUP BY bank_id"):
    print(r)

c.execute("SELECT COUNT(*) FROM questions WHERE bank_id=? AND type IN ('fill','single','judge') AND (stem LIKE '%看图%' OR stem LIKE '%如图%' OR stem LIKE '%下图%' OR stem LIKE '%图中%')", (BANK,))
print('\n数学库非solve题型中含看图/如图词:', c.fetchone()[0])

out = r'C:/Users/weifa/WorkBuddy/2026-11-05-18-17-26/solve_audit_dump.txt'
with io.open(out, 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(f'{r[4]}\t{r[0]}\t{r[1]}\t{r[2]}\tANS:{r[3]}\n')
print('\n已导出逐题清单:', out)
conn.close()
