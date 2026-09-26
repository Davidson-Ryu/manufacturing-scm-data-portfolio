"""W1 · 04 보조 분석: 규칙 기반 배분(Greedy) vs 수학적 최적(MILP)
같은 재고로 이론상 최대 몇 세트까지 가능한지 확인해, Greedy가 얼마를 포기했는지 진단한다."""
import sqlite3, numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

con = sqlite3.connect("w1.db")
sql = open("03_sql_logic.sql", encoding="utf-8").read()
alloc_sql = [p for p in sql.split(";") if "alloc_result" in p][0]
# 그룹별 Greedy 결과를 얻기 위해 마지막 SELECT만 바꿔 실행
greedy_sql = alloc_sql[:alloc_sql.rfind("SELECT SUM(SETS)")] + \
    "SELECT a.GROUP_ID, a.SETS, p.TARGET, p.PRIO FROM alloc_result a JOIN priority p USING (GROUP_ID) ORDER BY p.PRIO"
greedy = con.execute(greedy_sql).fetchall()
gids = [g[0] for g in greedy]; target = {g[0]: g[2] for g in greedy}
g_sets = {g[0]: g[1] for g in greedy}; prio = {g[0]: g[3] for g in greedy}

bom_sql = alloc_sql[:alloc_sql.rfind("SELECT SUM(SETS)")] + "SELECT GROUP_ID, PN, USAGE FROM grp_bom"
bom = con.execute(bom_sql).fetchall()
stock = dict(con.execute("""SELECT p.PN, SUM(i.QTY) FROM M_PN p JOIN T_INVENTORY i ON i.S_ID=p.S_ID
                            WHERE i.SNAPSHOT_DATE='2026-07-01' GROUP BY p.PN""").fetchall())
pns = sorted({b[1] for b in bom})
A = np.zeros((len(pns), len(gids)))
for g, pn, u in bom: A[pns.index(pn), gids.index(g)] = u
res = milp(c=-np.ones(len(gids)),                             # 세트 합 최대화
           constraints=LinearConstraint(A, -np.inf, [stock[p] for p in pns]),
           bounds=Bounds(0, [target[g] for g in gids]),
           integrality=np.ones(len(gids)))
m_sets = {g: int(round(x)) for g, x in zip(gids, res.x)}

gt, mt = sum(g_sets.values()), sum(m_sets.values())
print(f"GREEDY {gt} sets / {sum(1 for v in g_sets.values() if v>0)} groups")
print(f"MILP   {mt} sets / {sum(1 for v in m_sets.values() if v>0)} groups")
print(f"GAP    +{mt-gt} sets (+{(mt-gt)/gt*100:.1f}%)")
diff = sorted(((m_sets[g]-g_sets[g], g) for g in gids), reverse=True)[:5]
print("TOP GAP GROUPS (gap, group, prio, target):")
for d, g in diff: print(f"  +{d:4d}  G{g:02d}  prio {prio[g]:2d}  target {target[g]}")
