# 예시 8: Lot 특정 조회 — 명확한 질문 vs 모호한 질문 (lot_query)

> **학습 목표**: "LOT-005 지금 어디야?"처럼 **명확한 질문**은 단일 Tool 호출로 처리되는 반면, 모호한 질문(예시 7)은 2개 Tool을 동시 호출하는 차이를 비교한다. 같은 `lot_query` 의도에서 Tool 선택이 어떻게 달라지는지 학습.

---

## 사용자 입력

```
LOT-005 지금 어디야?
```

## 예시 7과의 차이

| 구분 | 예시 7 (모호한 질문) | 예시 8 (명확한 질문) |
|------|---------------------|---------------------|
| 입력 | "CVR-L1-TFT-01에 Lot 뭐 있어?" | "LOT-005 지금 어디야?" |
| 키 | equipment_id | lot_id |
| Tool 호출 | 2개 (물리+스케줄) | 1개 (get_lot_detail) |
| 모호성 | 있음 (물리 vs 스케줄) | 없음 (특정 Lot 상세) |

**핵심**: 같은 `lot_query` 의도이지만, 질문의 명확성에 따라 Tool 선택이 달라짐.

---

## 에이전트 처리 흐름

```
사용자: "LOT-005 지금 어디야?"
  │
  ▼
[Step 1] IntentAgent
  │  intent: "lot_query"
  │  detail: {"lot_id": "LOT-005", "equipment_id": ""}
  │  reasoning: "특정 LOT ID의 위치 조회"
  │
  ▼
[Step 2] InfoAgent ─── 단일 Tool 호출
  │  LLM 판단: LOT ID 명시 → get_lot_detail 하나면 충분
  │  tool_calls: [get_lot_detail({"lot_id": "LOT-005"})]
  │
  ▼
[Step 2.5] ToolNode
  │  get_lot_detail → lot JOIN lot_schedule
  │  결과: Lot 현재 상태 + 스케줄 이력 전부 포함
  │
  ▼
[Step 2 재진입] InfoAgent ─── 결과 정리
  │  현재 위치(AGV 이동 중) + 스케줄 3건 표로 정리
  │
  ▼
[Step 3] ResponseAgent → final_answer
```

---

## 핵심 설계 포인트

### 1. IntentAgent의 파라미터 추출 차이

**예시 7** (설비 기준):
```json
{"equipment_id": "CVR-L1-TFT-01", "lot_id": ""}
```

**예시 8** (Lot 기준):
```json
{"equipment_id": "", "lot_id": "LOT-005"}
```

IntentAgent가 `lot_id` 필드를 채우면 → InfoAgent는 `get_lot_detail` 하나로 처리.
`equipment_id`만 있고 `lot_id`가 비어있으면 → 모호성 해소 규칙 적용.

### 2. get_lot_detail — 하나의 Tool로 전체 그림 제공

```sql
-- Lot 기본 정보
SELECT * FROM lot WHERE lot_id = 'LOT-005'

-- 스케줄 이력 (설비 정보 포함)
SELECT ls.*, e.equipment_type, e.line, e.zone
FROM lot_schedule ls
JOIN equipment e ON ls.equipment_id = e.equipment_id
WHERE ls.lot_id = 'LOT-005'
ORDER BY ls.scheduled_start
```

**결과**:
```json
{
  "lot": [{
    "lot_id": "LOT-005",
    "product_type": "LCD_C",
    "quantity": 137,
    "status": "IN_TRANSIT",
    "current_equipment_id": "AGV-L1-CELL-01"
  }],
  "schedules": [
    {"equipment_id": "SRT-L1-MODULE-01", "equipment_type": "SORTER", "line": "L1", "zone": "MODULE"},
    {"equipment_id": "CVR-L1-TFT-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT"},
    {"equipment_id": "SHT-L3-PACK-01", "equipment_type": "SHUTTLE", "line": "L3", "zone": "PACK"}
  ]
}
```

**포인트**: `get_lot_detail`은 **현재 위치 + 스케줄 이력**을 한 번에 반환.
`current_equipment_id`(AGV)와 `schedules[].equipment_id`(SORTER, CONVEYOR, SHUTTLE)가 모두 다른 것을 LLM이 "이동 중"으로 해석.

### 3. LLM의 비즈니스 맥락 이해

LLM 응답에서:
- `status: IN_TRANSIT` + `current: AGV` → "현재 이동 중"
- 스케줄 3건이 모두 `actual_start: null` → "아직 시작 안 한 예정 작업"
- SORTER → CONVEYOR → SHUTTLE 순서 → 생산 공정 흐름

프롬프트의 **비즈니스 용어 사전**이 이 해석을 가능하게 함:
```
| 이동 중 Lot | lot.status='IN_TRANSIT' | 설비로 이동 중인 Lot |
```

---

## 최종 응답 (final_answer)

```
LOT-005의 상세 정보입니다.

📍 현재 위치
- 설비: AGV-L1-CELL-01 (현재 이동 중)
- 수량: 137
- 상태: 이동 중

📅 스케줄

| 설비ID            | 설비 타입  | 라인 | 구간   | 스케줄 시작          | 스케줄 종료          |
|-------------------|-----------|------|--------|---------------------|---------------------|
| SRT-L1-MODULE-01  | SORTER    | L1   | MODULE | 2026-02-26 18:22    | 2026-02-27 04:22    |
| CVR-L1-TFT-01    | CONVEYOR  | L1   | TFT    | 2026-02-26 20:22    | 2026-02-27 00:22    |
| SHT-L3-PACK-01   | SHUTTLE   | L3   | PACK   | 2026-02-27 00:22    | 2026-02-27 04:22    |
```

---

## State 변화 요약

| 단계 | intent | messages | final_answer |
|------|--------|----------|--------------|
| 초기 | `""` | `[]` | `""` |
| IntentAgent 후 | `"lot_query"` | `[]` | `""` |
| InfoAgent 1차 후 | `"lot_query"` | `[AIMessage(tool_calls×1)]` | `""` |
| ToolNode 후 | `"lot_query"` | `[AIMessage, ToolMessage]` | `""` |
| InfoAgent 2차 후 | `"lot_query"` | `[AI, Tool, AIMessage]` | `""` |
| ResponseAgent 후 | `"lot_query"` | `[AI, Tool, AIMessage]` | `"LOT-005의..."` |

---

## 학습 포인트

1. **명확 vs 모호 = Tool 수의 차이**: 같은 `lot_query` 의도에서 질문 명확성에 따라 1개(get_lot_detail) vs 2개(get_lots_on_equipment + get_lots_scheduled_for_equipment) Tool이 선택됨. LLM이 프롬프트 규칙을 따라 스스로 판단.
2. **설계 원칙 — 큰 Tool vs 작은 Tool**: `get_lot_detail`은 Lot 중심의 "전체 그림" Tool. `get_lots_on_equipment`/`get_lots_scheduled_for_equipment`는 설비 중심의 "단면" Tool. 용도에 따라 적절한 granularity를 선택.
3. **detail.lot_id가 핵심 분기점**: IntentAgent가 `lot_id`를 추출하면 → `get_lot_detail`, `equipment_id`만 있으면 → disambiguation 규칙 적용. 이 분기는 코드가 아닌 프롬프트에서 일어남.
4. **이 예시와 예시 7을 비교 학습**: 두 예시를 나란히 놓고 "어디서 플로우가 갈라지는가?"를 추적하면 LLM 기반 시스템의 의사결정 구조를 이해할 수 있다.
