# -*- coding: utf-8 -*-
"""为 8 道缺图应用题绘制精确配图
线段图 5 种模板 + 圆半径图 1 张，PIL 绘制，数学关系严格按题干数值。
输出: C:/Users/weifa/WorkBuddy/2026-11-05-18-17-26/fig_images/*.png
"""
import sys, os, math
sys.path.insert(0, r'E:/workbuddy工作区/.workbuddy/binaries/python/envs/default/Lib/site-packages')
from PIL import Image, ImageDraw, ImageFont

OUT = r'C:/Users/weifa/WorkBuddy/2026-11-05-18-17-26/fig_images'
os.makedirs(OUT, exist_ok=True)

W, H = 900, 420
BG = (255, 255, 255)
INK = (40, 40, 40)
BLUE = (43, 108, 176)
RED = (192, 57, 43)
GREEN = (39, 130, 84)

def font(sz, bold=False):
    for p in [r'C:/Windows/Fonts/msyhbd.ttc' if bold else r'C:/Windows/Fonts/msyh.ttc',
              r'C:/Windows/Fonts/simhei.ttf', r'C:/Windows/Fonts/arial.ttf']:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            continue
    return ImageFont.load_default()

def new_canvas():
    img = Image.new('RGB', (W, H), BG)
    return img, ImageDraw.Draw(img)

# ---------- 模板A：全程 x 千米，已行驶 a/b，还剩? ----------
def seg_remaining(total, frac_num, frac_den, fname, note=''):
    """一条线段分 frac_den 份，前 frac_num 份标已行驶，后段标 ?千米"""
    img, d = new_canvas()
    f20 = font(22); f24 = font(24, True)
    x0, x1, y = 120, 780, 150
    d.line([(x0, y), (x1, y)], fill=INK, width=4)
    seg = (x1 - x0) / frac_den
    # 分割刻度
    for i in range(frac_den + 1):
        x = x0 + i * seg
        d.line([(x, y - 12), (x, y + 12)], fill=INK, width=3)
    # 已行驶括线（前 frac_num 份）
    ya = y + 45
    xa0, xa1 = x0, x0 + frac_num * seg
    d.line([(xa0, ya), (xa1, ya)], fill=BLUE, width=3)
    d.line([(xa0, ya - 10), (xa0, ya)], fill=BLUE, width=3)
    d.line([(xa1, ya - 10), (xa1, ya)], fill=BLUE, width=3)
    t = f'已行驶 {frac_num}/{frac_den}'
    tw = d.textlength(t, font=f20)
    d.text(((xa0 + xa1 - tw) / 2, ya + 8), t, fill=BLUE, font=f20)
    # 剩余括线
    yb = y - 55
    xb0, xb1 = xa1, x1
    d.line([(xb0, yb), (xb1, yb)], fill=RED, width=3)
    d.line([(xb0, yb), (xb0, yb + 10)], fill=RED, width=3)
    d.line([(xb1, yb), (xb1, yb + 10)], fill=RED, width=3)
    t = '? 千米'
    tw = d.textlength(t, font=f24)
    d.text(((xb0 + xb1 - tw) / 2, yb - 34), t, fill=RED, font=f24)
    # 全程括线
    yc = y + 105
    d.line([(x0, yc), (x1, yc)], fill=INK, width=3)
    d.line([(x0, yc - 10), (x0, yc)], fill=INK, width=3)
    d.line([(x1, yc - 10), (x1, yc)], fill=INK, width=3)
    t = f'全程 {total} 千米'
    tw = d.textlength(t, font=f20)
    d.text(((x0 + x1 - tw) / 2, yc + 8), t, fill=INK, font=f20)
    if note:
        d.text((120, 30), note, fill=INK, font=f20)
    img.save(os.path.join(OUT, fname))
    print('saved', fname)

# ---------- 模板B：甲 x 个，乙比甲多 p/q，乙?个 ----------
def seg_more(m_a, p, q, fname, note=''):
    """甲线段 + 乙线段（甲 + 多出 p/q 段，问号）"""
    img, d = new_canvas()
    f20 = font(22); f24 = font(24, True)
    x0, y1, y2 = 170, 130, 250
    unit = 560 / q            # 甲 = (q-p) 单位示意，按 q 等分画
    # 甲：整数段（q 份里取 q-p 份长度为甲？不——甲本身画 1 个整段）
    # 采用教材画法：甲画整条，乙 = 甲 + 甲的 p/q
    ax1 = x0 + 470            # 甲线段长
    extra = 470 * p // q      # 多出的部分长
    # 甲
    d.line([(x0, y1), (ax1, y1)], fill=INK, width=4)
    d.text((40, y1 - 14), '甲：', fill=INK, font=f24)
    # 甲括线
    yc1 = y1 + 40
    d.line([(x0, yc1), (ax1, yc1)], fill=INK, width=3)
    d.line([(x0, yc1 - 10), (x0, yc1)], fill=INK, width=3)
    d.line([(ax1, yc1 - 10), (ax1, yc1)], fill=INK, width=3)
    t = f'{m_a} 个'
    d.text(((x0 + ax1) / 2 - 30, yc1 + 6), t, fill=INK, font=f20)
    # 乙 = 甲 + extra
    bx1 = ax1 + extra
    d.line([(x0, y2), (bx1, y2)], fill=INK, width=4)
    d.text((40, y2 - 14), '乙：', fill=INK, font=f24)
    # 乙的“比甲多 p/q”部分（红色）
    d.line([(ax1, y2 - 12), (ax1, y2 + 12)], fill=RED, width=3)
    d.line([(bx1, y2 - 12), (bx1, y2 + 12)], fill=RED, width=3)
    ye = y2 - 55
    d.line([(ax1, ye), (bx1, ye)], fill=RED, width=3)
    d.line([(ax1, ye), (ax1, ye + 10)], fill=RED, width=3)
    d.line([(bx1, ye), (bx1, ye + 10)], fill=RED, width=3)
    t = f'比甲多 {p}/{q}'
    tw = d.textlength(t, font=f20)
    d.text(((ax1 + bx1 - tw) / 2, ye - 32), t, fill=RED, font=f20)
    # 乙问号括线
    yb = y2 + 40
    d.line([(x0, yb), (bx1, yb)], fill=BLUE, width=3)
    d.line([(x0, yb - 10), (x0, yb)], fill=BLUE, width=3)
    d.line([(bx1, yb - 10), (bx1, yb)], fill=BLUE, width=3)
    t = '? 个'
    tw = d.textlength(t, font=f24)
    d.text(((x0 + bx1) / 2 - 24, yb + 6), t, fill=BLUE, font=f24)
    # 虚线对齐：乙起点与甲起点、甲终点
    for xx in [ax1]:
        for yy in [y1 + 55, y2 - 65]:
            pass
    if note:
        d.text((120, 25), note, fill=INK, font=f20)
    img.save(os.path.join(OUT, fname))
    print('saved', fname)

# ---------- 圆 + 半径 ----------
def circle_radius(r_cm, fname):
    img = Image.new('RGB', (520, 560), BG)
    d = ImageDraw.Draw(img)
    f24 = font(24, True); f20 = font(20)
    cx, cy, R = 260, 250, 150
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=INK, width=4)
    # 圆心
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)
    d.text((cx + 10, cy + 8), 'O', fill=INK, font=f24)
    # 半径（右上方向）
    ang = math.radians(-40)
    px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
    d.line([(cx, cy), (px, py)], fill=BLUE, width=4)
    t = f'r = {r_cm} 厘米'
    tw = d.textlength(t, font=f24)
    d.text(((cx + px) / 2 - tw / 2 + 40, (cy + py) / 2 - 36), t, fill=BLUE, font=f24)
    d.text((150, 470), '（图中圆内一条半径长 5 厘米）', fill=INK, font=f20)
    img.save(os.path.join(OUT, fname))
    print('saved', fname)

# ============ 生成 8 张图 ============
# 7 道线段图（题干数值一一对应）
seg_remaining(360, 3, 4, 'seg_q_py6u1_fa3a10818a.png')   # 全程360，已行3/4，还剩?
seg_remaining(210, 3, 4, 'seg_q_py6u1_90decb92cb.png')   # 全程210，已行3/4
seg_remaining(480, 2, 3, 'seg_q_py6u1_92e4fddd9e.png')   # 全程480，已行2/3
seg_more(120, 1, 3, 'seg_q_py6u1_2bbdd4bb4b.png')        # 甲120，乙比甲多1/3
seg_more(96, 1, 3, 'seg_q_py6u1_0c7dfff05c.png')         # 甲96
seg_more(150, 1, 3, 'seg_q_py6u1_c00d0dbd5a.png')        # 甲150
seg_more(80, 1, 3, 'seg_q_py6u1_09f7c89a7b.png')         # 甲80
# 1 道圆半径图
circle_radius(5, 'cir_q_exam00294.png')                  # 圆内半径5厘米，求直径
print('\n全部完成，输出目录:', OUT)
