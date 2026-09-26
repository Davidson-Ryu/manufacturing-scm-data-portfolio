"""W1 결과 시각화 → w1_result.png"""
import sqlite3, subprocess, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
for f in font_manager.findSystemFonts():
    if "NotoSansCJK" in f or "Malgun" in f or "AppleGothic" in f:
        font_manager.fontManager.addfont(f); plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name(); break
plt.rcParams["axes.unicode_minus"] = False

ns = {}
exec(open("04_compare_milp.py", encoding="utf-8").read().split("gt, mt =")[0], ns)
g_sets, m_sets, prio, gids = ns["g_sets"], ns["m_sets"], ns["prio"], ns["gids"]
con = sqlite3.connect("w1.db"); sql = open("03_sql_logic.sql", encoding="utf-8").read()
indiv = con.execute([p for p in sql.split(";") if "INDIVIDUAL_CAP_TOTAL" in p][0]).fetchone()[0]
gt, mt = sum(g_sets.values()), sum(m_sets.values())

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1, 2.2]})
bars = a1.bar(["개별 상한\n(장부상)", "규칙 배분\n(Greedy)", "수학적 최적\n(MILP)"], [indiv, gt, mt],
              color=["#B8C4CC", "#1F4E79", "#6FA8DC"])
for b, v in zip(bars, [indiv, gt, mt]): a1.text(b.get_x()+b.get_width()/2, v+30, f"{v:,}", ha="center", fontsize=11)
a1.set_title("출고 가능 세트 합계", fontsize=12); a1.set_ylim(0, indiv*1.15); a1.spines[["top","right"]].set_visible(False)
order = sorted(gids, key=lambda g: prio[g])
x = range(len(order))
a2.bar([i-0.2 for i in x], [g_sets[g] for g in order], width=0.4, label="규칙 배분 (Greedy)", color="#1F4E79")
a2.bar([i+0.2 for i in x], [m_sets[g] for g in order], width=0.4, label="수학적 최적 (MILP)", color="#6FA8DC")
a2.set_title("그룹별 출고 세트 (왼쪽일수록 판매 우선순위 높음)", fontsize=12)
a2.set_xlabel("ALC 그룹 (우선순위 순)"); a2.set_xticks([])
a2.legend(frameon=False); a2.spines[["top","right"]].set_visible(False)
fig.suptitle(f"W1 · 공유 재고 배분: 장부상 {indiv:,} → 실제 {gt:,} (허수 {indiv-gt:,}, -{(indiv-gt)/indiv*100:.0f}%)  ·  가상 데이터", fontsize=12)
plt.tight_layout(); plt.savefig("w1_result.png", dpi=140)
print("saved", indiv, gt, mt)
