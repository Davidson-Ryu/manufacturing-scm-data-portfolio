"""W1 가상 데이터 생성기.
실무 구조(ALC → BOM → 품번 → 저장위치 → 재고)만 본뜨고, 코드·수량은 모두 난수로 새로 만든다.
실제 회사 데이터는 사용하지 않는다."""
import csv, random
random.seed(20260926)

MODELS = ["A", "B", "C", "D", "E", "F"]           # 가상 차종 6개
parts = []                                         # (PN, S_ID, 설명)
common = {}                                        # 차종 공통 부품
for i, m in enumerate(MODELS):
    common[m] = []
    for k in range(6):
        pn = f"PN-{m}{k+1:02d}0"
        parts.append((pn, f"S-{len(parts)+50001}", f"{m} 공통 커버 {k+1}"))
        common[m].append(pn)
cross = []                                         # 여러 차종이 함께 쓰는 공용 부품
for k in range(8):
    pn = f"PN-X{k+1:02d}0"
    parts.append((pn, f"S-{len(parts)+50001}", f"공용 커버 {k+1}"))
    cross.append(pn)
option = []                                        # 사양(트림) 전용 부품
for k in range(40):
    pn = f"PN-T{k+1:03d}"
    parts.append((pn, f"S-{len(parts)+50001}", f"사양 전용 커버 {k+1}"))
    option.append(pn)

# 고유 BOM 48개 → ALC 72개 (24개는 BOM이 같은 중복 ALC)
groups = []
for g in range(48):
    m = MODELS[g % 6]
    bom = {}
    for pn in random.sample(common[m], 3):
        bom[pn] = random.choice([1, 1, 2])
    for pn in random.sample(cross, random.choice([1, 2])):
        bom[pn] = 1
    for pn in random.sample(option, random.choice([1, 2])):
        bom[pn] = random.choice([1, 2])
    groups.append((m, bom))

alcs = []
for g, (m, bom) in enumerate(groups):
    alcs.append((f"SYN-{m}-{g+1:03d}", m, bom))
for d in range(24):
    g = random.randrange(48)
    m, bom = groups[g]
    alcs.append((f"SYN-{m}-{100+d+1:03d}", m, dict(bom)))
random.shuffle(alcs)

with open("data/M_ALC.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["ALC_CODE", "MODEL"])
    for a, m, _ in alcs: w.writerow([a, m])
with open("data/M_ALC_BOM.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["ALC_CODE", "PN", "USAGE"])
    for a, _, bom in alcs:
        for pn, u in sorted(bom.items()): w.writerow([a, pn, u])
with open("data/M_PN.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["PN", "S_ID", "PN_DESC"])
    for p in parts: w.writerow(p)

# 판매: 인기 사양일수록 많이 팔림 (지수형 분포)
with open("data/T_SALES.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["ALC_CODE", "SALES_MONTH", "QTY"])
    for a, _, _ in alcs:
        base = max(3, int(random.lognormvariate(3.5, 0.55)))
        for mo in ["2026-04", "2026-05", "2026-06"]:
            w.writerow([a, mo, max(0, int(base * random.uniform(0.7, 1.3)))])

# 재고: 한 시점 스냅숏. 저장위치(S_ID) 단위로 흩어져 있음
with open("data/T_INVENTORY.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["S_ID", "SNAPSHOT_DATE", "QTY"])
    for pn, sid, _ in parts:
        if pn.startswith("PN-X"):   q = random.randint(120, 380)
        elif pn.startswith("PN-T"): q = random.randint(200, 600)
        else:                       q = random.randint(300, 800)
        w.writerow([sid, "2026-07-01", q])
print("ALC", len(alcs), "parts", len(parts))
