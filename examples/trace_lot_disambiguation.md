# 예시 7: Lot 의미 모호성 해소 — 두 Tool 동시 호출 패턴

> **학습 목표**: "설비에 Lot 뭐 있어?"라는 **모호한 질문**에서 FM이
> 물리적 위치(`get_lots_on_equipment`)와 스케줄(`get_lots_scheduled_for_equipment`) 두 Tool을 **동시에** 호출하는 패턴.
> 같은 자연어가 서로 다른 SQL로 매핑되어야 하는 의미 모호성을 FM이 해소하는 과정을 추적한다.

---

## 입력

```
CVR-L1-TFT-01에 Lot 뭐 있어?
```

> **모호성**: "Lot 뭐 있어?" = 물리적으로 있는 Lot? 스케줄된 Lot? 둘 다?

---

## Step 1: IntentAgent (의도분석)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human**:
```
CVR-L1-TFT-01에 Lot 뭐 있어?
```

### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "lot_query",
  "detail": {
    "equipment_type": "CONVEYOR",
    "line": "L1",
    "zone": "TFT",
    "equipment_id": "CVR-L1-TFT-01",
    "lot_id": "",
    "hours": 0,
    "keyword": ""
  },
  "reasoning": "특정 장비에 Lot이 있는지 확인하는 질문이므로 lot_query 의도이며, 장비 ID를 통해 장비 유형, 라인, 구간을 파악할 수 있음"
}
```

> **포인트**: FM이 "Lot 뭐 있어?"를 `lot_query`로 분류하고, 장비 ID에서 유형/라인/구간을 역파싱.
> `keyword`가 비어있음 → "현재" 또는 "예정" 등 명시적 표현이 없으므로 **모호한 질문**.

---

## Step 2: InfoAgent (정보조회, 첫 호출)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + **모호성 해소 규칙**, 1781자)
- **Human**:
```
사용자 질문: CVR-L1-TFT-01에 Lot 뭐 있어?
의도: lot_query
상세: {"equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "equipment_id": "CVR-L1-TFT-01", "lot_id": "", "hours": 0, "keyword": ""}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

> **핵심**: System 프롬프트에 아래 규칙이 있음:
> ```
> | "설비 Lot 알려줘" (모호) | 모호함 → 두 Tool 모두 호출 |
> ```
> FM이 이 규칙 + `keyword: ""`(비어있음)을 보고 모호한 질문으로 판단.

### 🔶 FM 출력 (← Gemini) → **Tool 2개 동시 호출**
- `get_lots_on_equipment({'equipment_id': 'CVR-L1-TFT-01'})`
- `get_lots_scheduled_for_equipment({'equipment_id': 'CVR-L1-TFT-01'})`

> **핵심**: FM이 **2개 Tool을 동시에** 호출 (Gemini Function Calling의 parallel tool calls).
> 하나의 사용자 질문이 **2개의 서로 다른 SQL**로 매핑됨.

---

## Step 2.5: ToolNode (SQL 실행 — 2개 병렬)

### Tool 1: get_lots_on_equipment (물리적 위치)
```sql
SELECT l.lot_id, l.product_type, l.quantity, l.status,
       l.current_equipment_id, l.created_at, l.updated_at
FROM lot l
WHERE l.current_equipment_id = 'CVR-L1-TFT-01'
  AND l.status IN ('IN_TRANSIT', 'IN_PROCESS')
```

```json
[
  {"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01"},
  {"lot_id": "LOT-023", "product_type": "OLED_A", "quantity": 289, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01"}
]
```

### Tool 2: get_lots_scheduled_for_equipment (스케줄)
```sql
SELECT ls.lot_id, l.product_type, l.quantity, l.status,
       l.current_equipment_id, ls.equipment_id AS scheduled_equipment_id,
       ls.scheduled_start, ls.scheduled_end, ls.actual_start, ls.actual_end
FROM lot_schedule ls
JOIN lot l ON ls.lot_id = l.lot_id
WHERE ls.equipment_id = 'CVR-L1-TFT-01'
  AND ls.actual_end IS NULL
ORDER BY ls.scheduled_start
```

```json
[
  {"lot_id": "LOT-020", "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "scheduled_equipment_id": "CVR-L1-TFT-01", "scheduled_start": "2026-02-26 21:08:59"},
  {"lot_id": "LOT-023", "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", ...},
  {"lot_id": "LOT-005", "status": "IN_TRANSIT", "current_equipment_id": "AGV-L1-CELL-01", "scheduled_equipment_id": "CVR-L1-TFT-01", ...},
  {"lot_id": "LOT-018", "status": "SCHEDULED", "current_equipment_id": null, ...},
  {"lot_id": "LOT-029", "status": "IN_TRANSIT", "current_equipment_id": "AGV-L3-PACK-02", ...},
  {"lot_id": "LOT-009", "status": "SCHEDULED", "current_equipment_id": null, ...}
]
```

> **의미 모호성 실체**:
> - Tool 1 결과: LOT-020, LOT-023 (물리적으로 설비에 있는 2건)
> - Tool 2 결과: 6건 (스케줄된 Lot — 물리적 위치와 다른 것들 포함)
> - LOT-005: `current=AGV-L1-CELL-01`(이동 중) + `scheduled=CVR-L1-TFT-01`(목적지) → **⚡ 이동 중**
> - LOT-018: `current=null`(미배정) + `scheduled=CVR-L1-TFT-01` → **대기 중**

---

## Step 2 재진입: InfoAgent (Tool 결과 수신)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 재진입)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Messages**: 메시지 히스토리 3건 포함
  - `AIMessage`: (tool_calls: 2개)
  - `ToolMessage` 1: [LOT-020, LOT-023] (물리적 위치)
  - `ToolMessage` 2: [LOT-020, LOT-023, LOT-005, LOT-018, LOT-029, LOT-009] (스케줄)

> **핵심**: FM이 2개 Tool의 결과를 **동시에** 받고, 프롬프트 규칙에 따라 구분하여 응답.

### 🔶 FM 출력 (← Gemini) → 텍스트 응답
```
📍 현재 CVR-L1-TFT-01 설비에 물리적으로 위치한 Lot:
| Lot ID  | 제품 유형 | 수량 | 상태       |
|---------|-----------|------|------------|
| LOT-020 | OLED_B    | 206  | IN_PROCESS |
| LOT-023 | OLED_A    | 289  | IN_PROCESS |

📅 CVR-L1-TFT-01 설비에 예정된 Lot:
| Lot ID  | 제품 유형 | 수량 | 상태                         | 스케줄 시작          |
|---------|-----------|------|------------------------------|----------------------|
| LOT-020 | OLED_B    | 206  | IN_PROCESS                   | 2026-02-26 21:08:59  |
| LOT-023 | OLED_A    | 289  | IN_PROCESS                   | 2026-02-26 22:08:59  |
| LOT-005 | LCD_C     | 137  | ⚡ 이동 중 (AGV-L1-CELL-01)  | 2026-02-26 23:08:59  |
| LOT-018 | OLED_B    | 289  | SCHEDULED                    | 2026-02-27 00:08:59  |
| LOT-029 | LCD_C     | 349  | ⚡ 이동 중 (AGV-L3-PACK-02)  | 2026-02-27 04:08:59  |
| LOT-009 | OLED_B    | 196  | SCHEDULED                    | 2026-02-27 06:08:59  |
```

> **포인트**: FM이 프롬프트 규칙 적용:
> 1. 📍/📅 아이콘으로 물리적 위치 vs 스케줄 **구분 표시**
> 2. `current_equipment_id ≠ scheduled_equipment_id` → **"⚡ 이동 중"** 표시
> 3. `current=null` → 상태만 표시 (SCHEDULED)

---

## Step 3: ResponseAgent (응답생성)

최종 응답: 위 📍/📅 구분 표 그대로 추출.

---

## FM 호출 요약

| 단계 | FM 역할 | 핵심 판단 |
|------|---------|----------|
| IntentAgent | 의도 분류 | "Lot 뭐 있어?" → `lot_query`, keyword 비어있음 |
| InfoAgent 1차 | **모호성 해소** | keyword 없음 + 모호성 규칙 → **2개 Tool 동시 호출** |
| InfoAgent 재진입 | 구분 응답 | 2개 Tool 결과 → 📍물리적 + 📅스케줄 **분리 표시** |

**총 FM 호출: 3회** — InfoAgent 1차에서 2개 Tool 동시 호출이 핵심

---

## 학습 포인트

1. **의미 모호성 해소**: "Lot 뭐 있어?"는 물리적 위치와 스케줄 두 가지 의미. FM이 System 프롬프트의 모호성 해소 규칙을 적용하여 2개 Tool을 동시 호출.
2. **Parallel Tool Calls**: Gemini Function Calling은 1회 호출에서 여러 Tool을 동시에 호출할 수 있음. 이는 순차 호출 대비 지연시간 절약.
3. **같은 자연어, 다른 SQL**: 하나의 "Lot 뭐 있어?" 질문이 `lot.current_equipment_id = ?` 와 `lot_schedule.equipment_id = ?` 두 개의 다른 SQL로 매핑.
4. **⚡ 이동 중 표시**: `current_equipment_id ≠ scheduled_equipment_id`인 경우를 FM이 감지하고 "이동 중" 마커를 추가. 프롬프트 규칙: "current_equipment_id ≠ schedule.equipment_id인 경우 ⚡ 이동 중 표시".
5. **모호 vs 명확 비교**: 예시 8에서 "예정된 Lot 보여줘"처럼 명확한 질문은 단일 Tool만 호출됨.
