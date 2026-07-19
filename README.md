# manufacturing-scm-data-portfolio
Manufacturing SCM × Data Modeling — synthetic data portfolio
# Manufacturing SCM × Data Modeling

제조 SCM(생산계획·시퀀싱·정합 특화) × 데이터 설계 포트폴리오.
**All data is synthetic.** 회사 실데이터 미포함.

## Weapons

### W1 — ALC BOM 역전개 / 대분재고 (Allocation) ✅
공유재고 배분으로 실제 출고가능량 산출.
- 개별상한 **2,499** → 공유배분 **848** (허수 1,651 / −66%)
- 핵심 로직: 공유부품 순차배분 (SUM OVER PARTITION BY)
- 4종 세트: 01_problem · 02_data_model · 03_sql_logic · 04_business_impact

### W2 — 지역군 실적 정합 — 예정
### W3 — 서열 버팀 검증 — 예정
