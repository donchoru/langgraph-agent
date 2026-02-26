# 예시 8: 특정 Lot 상세 조회 — 명확한 질문, 단일 Tool 패턴

> **학습 목표**: LOT ID가 명시된 **명확한 질문**에서 FM이 단일 Tool(`get_lot_detail`)만 호출하는 패턴.
> 예시 7(모호한 질문 → 2개 Tool)과 대비하여, 질문의 명확성에 따라 Tool 선택 전략이 달라지는 것을 학습한다.

---

## 입력

```
LOT-005 지금 어디야?
```

> **명확**: LOT ID가 명시적 → `get_lot_detail` 단일 호출 예상.

---

## Step 1: IntentAgent (의도분석)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human**:
```
LOT-005 지금 어디야?
```

### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "lot_query",
  "detail": {
    "equipment_type": "",
    "line": "",
    "zone": "",
    "equipment_id": "",
    "lot_id": "LOT-005",
    "hours": 0,
    "keyword": ""
  },
  "reasoning": "LOT ID가 명시적으로 주어졌으므로 lot_query 의도로 분류함"
}
```

> **포인트**: `lot_id: "LOT-005"`가 추출됨. `equipment_id`는 비어있음 → 설비 기준이 아닌 Lot 기준 조회.
> 프롬프트의 "LOT-xxx 어디야? → lot_query (lot_id 추출)" 매핑 규칙 적용.

---

## Step 2: InfoAgent (정보조회, 첫 호출)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Human**:
```
사용자 질문: LOT-005 지금 어디야?
의도: lot_query
상세: {"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "lot_id": "LOT-005", "hours": 0, "keyword": ""}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

### 🔶 FM 출력 (← Gemini) → **Tool 1개만 호출**
- `get_lot_detail({'lot_id': 'LOT-005'})`

> **핵심**: 예시 7과 달리 **단일 Tool만 호출**.
> 도구 선택 가이드: "특정 LOT ID 언급 시 → get_lot_detail" 규칙 적용.
> 모호성 해소가 필요 없음 — LOT ID가 명확하므로 해당 Lot의 전체 정보를 한번에 조회.

---

## Step 2.5: ToolNode (SQL 실행)

```sql
-- Lot 기본 정보
SELECT * FROM lot WHERE lot_id = 'LOT-005'

-- Lot 스케줄 이력 (설비 정보 포함)
SELECT ls.*, e.equipment_type, e.line, e.zone
FROM lot_schedule ls
JOIN equipment e ON ls.equipment_id = e.equipment_id
WHERE ls.lot_id = 'LOT-005'
ORDER BY ls.scheduled_start
```

### Tool 결과
```json
{
  "lot": [{
    "lot_id": "LOT-005",
    "product_type": "LCD_C",
    "quantity": 137,
    "status": "IN_TRANSIT",
    "current_equipment_id": "AGV-L1-CELL-01",
    "created_at": "2026-02-26 19:08:59",
    "updated_at": "2026-02-26 21:14:59"
  }],
  "schedules": [
    {"equipment_id": "SRT-L1-MODULE-01", "equipment_type": "SORTER", "line": "L1", "zone": "MODULE",
     "scheduled_start": "2026-02-26 21:08:59", "actual_start": null},
    {"equipment_id": "CVR-L1-TFT-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT",
     "scheduled_start": "2026-02-26 23:08:59", "actual_start": null},
    {"equipment_id": "SHT-L3-PACK-01", "equipment_type": "SHUTTLE", "line": "L3", "zone": "PACK",
     "scheduled_start": "2026-02-27 03:08:59", "actual_start": null}
  ]
}
```

> **포인트**: LOT-005는 현재 `AGV-L1-CELL-01`에서 이동 중(IN_TRANSIT).
> 스케줄은 3개 설비를 순차적으로 거치는 경로: SORTER → CONVEYOR → SHUTTLE.

---

## Step 2 재진입: InfoAgent (Tool 결과 수신)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 재진입)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Messages**: 2건
  - `AIMessage`: (tool_calls: get_lot_detail)
  - `ToolMessage`: {"lot": [...], "schedules": [3건]}

### 🔶 FM 출력 (← Gemini) → 텍스트 응답
```
LOT-005 상세 정보입니다.

### Lot 정보
| 속성 | 값 |
|---|---|
| Lot ID | LOT-005 |
| 제품 유형 | LCD_C |
| 수량 | 137 |
| 상태 | 이동 중(IN_TRANSIT) |
| 현재 위치 | AGV-L1-CELL-01 |
| 생성 시간 | 2026-02-26 19:08:59 |
| 업데이트 시간 | 2026-02-26 21:14:59 |

### 스케줄
| 설비 ID | 설비 유형 | 라인 | 구간 | 예정 시작 | 예정 종료 |
|---|---|---|---|---|---|
| SRT-L1-MODULE-01 | SORTER | L1 | MODULE | 2026-02-26 21:08:59 | 2026-02-27 07:08:59 |
| CVR-L1-TFT-01 | CONVEYOR | L1 | TFT | 2026-02-26 23:08:59 | 2026-02-27 03:08:59 |
| SHT-L3-PACK-01 | SHUTTLE | L3 | PACK | 2026-02-27 03:08:59 | 2026-02-27 07:08:59 |
```

> **포인트**: FM이 `IN_TRANSIT` 상태를 "이동 중"으로 한국어 변환.
> 스케줄에서 Lot의 이동 경로가 드러남: SORTER(L1) → CONVEYOR(L1) → SHUTTLE(L3).

---

## Step 3: ResponseAgent (응답생성)

최종 응답: 위 Lot 정보 + 스케줄 표 추출.

---

## 예시 7 vs 예시 8 비교: 모호 vs 명확

| 구분 | 예시 7 (모호) | 예시 8 (명확) |
|------|---------------|---------------|
| 입력 | "CVR-L1-TFT-01에 Lot 뭐 있어?" | "LOT-005 지금 어디야?" |
| 기준 | **설비** 기준 | **Lot** 기준 |
| 모호성 | 물리적? 스케줄? → 모호 | LOT ID 명확 |
| **Tool 수** | **2개** 동시 호출 | **1개** 호출 |
| Tool | get_lots_on_equipment + get_lots_scheduled_for_equipment | get_lot_detail |
| 결과 구분 | 📍 물리적 + 📅 스케줄 분리 | Lot 정보 + 스케줄 경로 |

---

## 학습 포인트

1. **명확한 질문 → 단일 Tool**: LOT ID가 명시적이면 모호성 해소 불필요. FM이 `get_lot_detail` 하나로 Lot 정보 + 스케줄을 모두 조회.
2. **설비 기준 vs Lot 기준**: 예시 7은 설비 기준(어떤 Lot이 이 설비에?), 예시 8은 Lot 기준(이 Lot이 어디에?). 같은 `lot_query` 의도에서 조회 방향이 다름.
3. **Lot 이동 경로 가시화**: FM이 스케줄 데이터에서 Lot의 이동 경로(SORTER → CONVEYOR → SHUTTLE)를 추론하여 표시. 생산 공정 흐름이 드러남.
4. **모호 vs 명확 비교 학습**: 같은 `lot_query` 의도라도 질문의 명확성에 따라 Tool 선택 전략이 달라짐. FM의 프롬프트 규칙("특정 LOT ID 언급 시 → get_lot_detail")이 이를 결정.
