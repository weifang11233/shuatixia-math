# shuatixia-math · 小小刷题家 · 数学题库内容与工具

六年级数学上册（青岛版六三制）题库的导入数据、程序化配图与运维脚本。

## 目录

| 路径 | 说明 |
|---|---|
| `data/preview_data.json` | 172 题结构化题卡（圆专题 10 题 + 分知识点阶梯训练 162 题，含答案/解析/章节映射） |
| `data/solve_audit_dump.txt` | 196 道应用题逐题审计清单（ID/章节/题干/答案） |
| `scripts/import_172.py` | SQL 直插 + reorderBankSeq 排序复刻（幂等，normStem 前 60 字去重） |
| `scripts/draw_fig_images.py` | PIL 程序化绘制：全程-已行驶-剩? / 甲乙比多 / 圆半径 三类模板 |
| `scripts/audit_app_questions.py` | 应用题真实审计（图依赖词正则扫描 + 非应用题特征识别） |
| `scripts/acceptance_6.py` | 六项验收（章节序/首题/判分/图片/选项/统计） |
| `scripts/upload_fig_images.py` `upload_circle_images.py` `relink_images.py` | 图片上传与题目关联（multipart → /api/images → /questions/:id/image） |
| `scripts/verify_final.py` | 线上终验 |
| `images/` | 8 张程序化配图（7 线段图 + 1 圆半径图） |

## 数据口径

- 圆专题：π 取 3.14，L1→L5 难度递进，每题带双解法与易错提醒
- 阶梯训练：27 知识点 × 6 题（L1→L6），章节映射 `第X单元 · 阶梯训练 · 知识点名`
- 运行环境：fnOS NAS Docker（better-sqlite3 单文件服务端），凭据一律走环境变量/占位符，不落库
