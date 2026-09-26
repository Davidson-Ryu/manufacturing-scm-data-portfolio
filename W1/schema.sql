-- W1 데이터 모델 (SQLite)
-- ALC(완성 사양 코드) → BOM → 품번(PN) → 저장위치(S_ID) → 재고
PRAGMA foreign_keys = ON;

CREATE TABLE M_ALC (
    ALC_CODE  TEXT PRIMARY KEY,          -- 완성차 사양 코드 (고객사 발행 키를 본뜬 가상 코드)
    MODEL     TEXT NOT NULL               -- 차종
);

CREATE TABLE M_PN (
    PN        TEXT PRIMARY KEY,           -- 커버링 품번
    S_ID      TEXT NOT NULL UNIQUE,       -- 저장위치·시스템 ID (재고와 품번을 잇는 다리)
    PN_DESC   TEXT
);

CREATE TABLE M_ALC_BOM (
    ALC_CODE  TEXT NOT NULL REFERENCES M_ALC(ALC_CODE),
    PN        TEXT NOT NULL REFERENCES M_PN(PN),
    USAGE     INTEGER NOT NULL CHECK (USAGE > 0),   -- 한 세트에 같은 품번이 두 번 들어가면 2
    PRIMARY KEY (ALC_CODE, PN)
);

CREATE TABLE T_SALES (
    ALC_CODE     TEXT NOT NULL REFERENCES M_ALC(ALC_CODE),
    SALES_MONTH  TEXT NOT NULL,           -- 'YYYY-MM'
    QTY          INTEGER NOT NULL,
    PRIMARY KEY (ALC_CODE, SALES_MONTH)
);

CREATE TABLE T_INVENTORY (
    S_ID           TEXT NOT NULL REFERENCES M_PN(S_ID),
    SNAPSHOT_DATE  TEXT NOT NULL,         -- 재고는 시점 스냅숏. 날짜를 키에 넣어 이력을 남김
    QTY            INTEGER NOT NULL,
    PRIMARY KEY (S_ID, SNAPSHOT_DATE)
);
