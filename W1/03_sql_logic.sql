-- ============================================================
-- W1 · 03_sql_logic
-- 공유 부품 재고로 실제로 몇 세트를 출고할 수 있는가
-- 기준: 재고 스냅숏 2026-07-01, 판매 3개월 평균
-- ============================================================

-- ------------------------------------------------------------
-- [A] Baseline · 개별 상한
-- 각 ALC가 재고를 혼자 쓴다고 가정했을 때의 출고 가능 세트
-- (공유 부품을 ALC마다 중복으로 센다 → 장부상 숫자)
-- ------------------------------------------------------------
WITH stock AS (
    SELECT p.PN, SUM(i.QTY) AS STOCK
    FROM M_PN p JOIN T_INVENTORY i ON i.S_ID = p.S_ID
    WHERE i.SNAPSHOT_DATE = '2026-07-01'
    GROUP BY p.PN
),
alc_target AS (                            -- ALC별 월평균 판매 = 목표 세트
    SELECT ALC_CODE, CAST(ROUND(SUM(QTY) / 3.0) AS INTEGER) AS TARGET
    FROM T_SALES GROUP BY ALC_CODE
),
alc_cap AS (                               -- 병목 부품이 만들 수 있는 최대 세트
    SELECT b.ALC_CODE, MIN(s.STOCK / b.USAGE) AS CAP
    FROM M_ALC_BOM b JOIN stock s ON s.PN = b.PN
    GROUP BY b.ALC_CODE
)
SELECT SUM(MIN(c.CAP, t.TARGET)) AS INDIVIDUAL_CAP_TOTAL
FROM alc_cap c JOIN alc_target t ON t.ALC_CODE = c.ALC_CODE;


-- ------------------------------------------------------------
-- [B] Allocation · 공유 재고 배분 (Greedy, 규칙 기반)
-- 1) BOM이 같은 ALC를 하나의 그룹으로 접는다
-- 2) 많이 팔리는 그룹부터 우선순위를 준다
-- 3) 부품마다 우선순위대로 재고를 누적 차감한다
-- 4) 그룹별 병목 부품이 실제 출고 세트를 정한다
-- ------------------------------------------------------------
WITH fingerprint AS (                      -- ALC별 BOM 지문 (품번:사용량 정렬 연결)
    SELECT ALC_CODE, GROUP_CONCAT(PN || ':' || USAGE, '|' ORDER BY PN) AS FP
    FROM M_ALC_BOM GROUP BY ALC_CODE
),
grp AS (                                   -- 같은 지문 = 같은 그룹 (번호표는 DENSE_RANK)
    SELECT ALC_CODE, DENSE_RANK() OVER (ORDER BY FP) AS GROUP_ID
    FROM fingerprint
),
raw_sales AS (                             -- 사실은 ALC 단위로 보존
    SELECT ALC_CODE, SUM(QTY) / 3.0 AS AVG_SALES
    FROM T_SALES GROUP BY ALC_CODE
),
grp_sales AS (                             -- 집계는 그룹 단위로 올림
    SELECT g.GROUP_ID, CAST(ROUND(SUM(r.AVG_SALES)) AS INTEGER) AS TARGET
    FROM grp g LEFT JOIN raw_sales r ON r.ALC_CODE = g.ALC_CODE
    GROUP BY g.GROUP_ID
),
stock AS (                                 -- 저장위치 재고 → 품번 재고 (S_ID 다리)
    SELECT p.PN, SUM(i.QTY) AS STOCK
    FROM M_PN p JOIN T_INVENTORY i ON i.S_ID = p.S_ID
    WHERE i.SNAPSHOT_DATE = '2026-07-01'
    GROUP BY p.PN
),
grp_bom AS (
    SELECT DISTINCT g.GROUP_ID, b.PN, b.USAGE
    FROM grp g JOIN M_ALC_BOM b ON b.ALC_CODE = g.ALC_CODE
),
priority AS (                              -- 줄세우기는 ROW_NUMBER (동점 없이 순서 확정)
    SELECT GROUP_ID, TARGET,
           ROW_NUMBER() OVER (ORDER BY TARGET DESC, GROUP_ID) AS PRIO
    FROM grp_sales
),
demand_base AS (
    SELECT gb.GROUP_ID, gb.PN, gb.USAGE, p.PRIO,
           p.TARGET * gb.USAGE AS NEEDED, s.STOCK
    FROM grp_bom gb
    JOIN priority p ON p.GROUP_ID = gb.GROUP_ID
    JOIN stock    s ON s.PN = gb.PN
),
demand AS (                                -- ★ 핵심: 부품마다 우선순위대로 누적 필요량 vs 재고
    SELECT *,
           SUM(NEEDED) OVER (PARTITION BY PN ORDER BY PRIO
                             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS CUM_NEED
    FROM demand_base
),
allocated AS (
    SELECT GROUP_ID, PN, USAGE, PRIO,
           CASE
             WHEN CUM_NEED <= STOCK          THEN NEEDED                     -- 다 받음
             WHEN CUM_NEED - NEEDED < STOCK  THEN STOCK - (CUM_NEED - NEEDED) -- 남은 만큼만
             ELSE 0                                                          -- 못 받음
           END AS ALLOC
    FROM demand
),
alloc_result AS (                          -- 그룹의 병목 부품이 출고 세트를 결정
    SELECT GROUP_ID, MIN(ALLOC / USAGE) AS SETS
    FROM allocated GROUP BY GROUP_ID
)
SELECT SUM(SETS)                              AS ALLOCATED_TOTAL,
       COUNT(*)                               AS GROUPS,
       SUM(CASE WHEN SETS = 0 THEN 1 ELSE 0 END) AS ZERO_GROUPS
FROM alloc_result;
