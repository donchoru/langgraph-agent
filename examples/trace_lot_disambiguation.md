# 예시 7: Lot 의미 모호성 해소 (lot_query — Disambiguation)

> **학습 목표**: "설비에 Lot 뭐 있어?"라는 모호한 질문을 LLM이 **물리적 위치**와 **스케줄**로 구분하여 2개 Tool을 동시 호출하는 패턴. DB 조회 기반 AI에서 가장 빈번한 실무 문제인 **의미 모호성 해소(Semantic Disambiguation)** 를 다룬다.

---

## 사용자 입력

```
CVR-L1-TFT-01에 Lot 뭐 있어?
```

## 왜 이 질문이 모호한가?

"설비에 Lot 뭐 있어?"는 **최소 2가지 의미**로 해석 가능:

| 해석 | SQL 매핑 | 의미 |
|------|----------|------|
| (A) 물리적 위치 | `lot.current_equipment_id = 'CVR-L1-TFT-01'` | 지금 설비 위에 물리적으로 있는 Lot |
| (B) 생산 스케줄 | `lot_schedule.equipment_id = 'CVR-L1-TFT-01'` | 앞으로 이 설비에서 처리 예정인 Lot |

**사람은 맥락으로 구분하지만, LLM은 명시적 가이드 없이는 하나만 선택하거나 혼동한다.**

---

## 에이전트 처리 흐름

```
사용자: "CVR-L1-TFT-01에 Lot 뭐 있어?"
  │
  ▼
[Step 1] IntentAgent
  │  intent: "lot_query"
  │  detail: {"equipment_id": "CVR-L1-TFT-01", "lot_id": ""}
  │  reasoning: "특정 설비의 Lot 조회 요청"
  │
  ▼  intent ≠ "general_chat" → InfoAgent로
[Step 2] InfoAgent ─── ⚡ 핵심: 2개 Tool 동시 호출
  │  LLM 판단: 모호한 질문 → 두 Tool 모두 필요
  │  tool_calls: [
  │    get_lots_on_equipment({"equipment_id": "CVR-L1-TFT-01"}),
  │    get_lots_scheduled_for_equipment({"equipment_id": "CVR-L1-TFT-01"})
  │  ]
  │
  ▼  tool_calls 존재 → ToolNode로
[Step 2.5] ToolNode ─── 2개 SQL 병렬 실행
  │  Tool 1: get_lots_on_equipment → 물리적 위치 Lot 2건
  │  Tool 2: get_lots_scheduled_for_equipment → 스케줄 Lot 6건
  │
  ▼  ToolNode → InfoAgent 재진입
[Step 2 재진입] InfoAgent ─── 결과 구분하여 응답 생성
  │  📍 물리적으로 있는 Lot / 📅 스케줄된 Lot 구분
  │  ⚡ 이동 중(current ≠ scheduled) Lot 별도 표시
  │
  ▼
[Step 3] ResponseAgent → final_answer
```

---

## 핵심 설계 포인트

### 1. 프롬프트 기반 모호성 해소

`INFO_SYSTEM_PROMPT`에 명시적 disambiguation 규칙:

```
## ⚠ 의미 모호성 해소 (Disambiguation) 규칙

### "설비에 있는 Lot" 질문 시 — 반드시 2가지 의미를 구분:
| 사용자 표현 | 의미 | 사용할 Tool |
|---|---|---|
| "설비에 지금 있는 Lot" | 물리적 현재 위치 | get_lots_on_equipment |
| "설비에 예정된 Lot" | 스케줄 | get_lots_scheduled_for_equipment |
| "설비 Lot 알려줘" (모호) | **두 Tool 모두 호출** | 둘 다 |
```

**포인트**: LLM에게 "모호하면 둘 다 호출하라"는 명시적 fallback 규칙을 줌.
코드 변경 없이 프롬프트만으로 disambiguation을 구현하는 패턴.

### 2. Tool 함수 docstring으로 의미 구분 강화

```python
@tool
def get_lots_on_equipment(equipment_id: str) -> str:
    """설비에 현재 물리적으로 위치한 Lot 조회.
    ⚠ '설비의 Lot'이라는 질문에서 '현재 물리적으로 있는 Lot'을 의미할 때 사용.
    스케줄(예정)된 Lot을 보려면 get_lots_scheduled_for_equipment를 사용하세요."""
```

**포인트**: docstring에 "언제 이 Tool을 쓰고, 언제 다른 Tool을 써야 하는지"를 명시.
Gemini Function Calling은 docstring을 Tool 설명으로 사용하므로, 여기에 disambiguation 힌트를 넣는 것이 효과적.

### 3. 실행된 SQL — 같은 테이블, 다른 WHERE

**Tool 1: get_lots_on_equipment** (물리적 위치)
```sql
SELECT l.lot_id, l.product_type, l.quantity, l.status,
       l.current_equipment_id, l.created_at, l.updated_at
FROM lot l
WHERE l.current_equipment_id = 'CVR-L1-TFT-01'
  AND l.status IN ('IN_TRANSIT', 'IN_PROCESS')
```

**Tool 2: get_lots_scheduled_for_equipment** (스케줄)
```sql
SELECT ls.lot_id, l.product_type, l.quantity, l.status,
       l.current_equipment_id,
       ls.equipment_id AS scheduled_equipment_id,
       ls.scheduled_start, ls.scheduled_end,
       ls.actual_start, ls.actual_end
FROM lot_schedule ls
JOIN lot l ON ls.lot_id = l.lot_id
WHERE ls.equipment_id = 'CVR-L1-TFT-01'
  AND ls.actual_end IS NULL
```

**핵심**: 같은 "설비의 Lot"이라는 질문이 **다른 테이블, 다른 WHERE 조건**으로 매핑됨.
- Tool 1: `lot` 테이블의 `current_equipment_id` (물리적 위치)
- Tool 2: `lot_schedule` 테이블의 `equipment_id` (계획)

### 4. 이동 중 Lot 감지 패턴

Tool 2 결과에서 LOT-005:
```json
{
  "lot_id": "LOT-005",
  "status": "IN_TRANSIT",
  "current_equipment_id": "AGV-L1-CELL-01",     // ← 현재 AGV에 있음
  "scheduled_equipment_id": "CVR-L1-TFT-01"     // ← 이 설비에 예정
}
```

`current_equipment_id ≠ scheduled_equipment_id` → LLM이 "⚡ 이동 중" 표시.
프롬프트 규칙: *"current_equipment_id ≠ schedule.equipment_id인 경우 이동 중 표시"*

---

## Tool 결과 데이터

### Tool 1: get_lots_on_equipment (물리적 위치 — 2건)

```json
[
  {"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01"},
  {"lot_id": "LOT-023", "product_type": "OLED_A", "quantity": 289, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01"}
]
```

### Tool 2: get_lots_scheduled_for_equipment (스케줄 — 6건, 상위 3건)

```json
[
  {"lot_id": "LOT-020", "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "scheduled_equipment_id": "CVR-L1-TFT-01"},
  {"lot_id": "LOT-023", "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "scheduled_equipment_id": "CVR-L1-TFT-01"},
  {"lot_id": "LOT-005", "status": "IN_TRANSIT", "current_equipment_id": "AGV-L1-CELL-01", "scheduled_equipment_id": "CVR-L1-TFT-01"}
]
```

**LOT-020, LOT-023**: 물리적 위치 = 스케줄 설비 (정상)
**LOT-005**: 물리적 위치(AGV) ≠ 스케줄 설비(CVR) → 이동 중

---

## 최종 응답 (final_answer)

```
📍 현재 CVR-L1-TFT-01 설비에 물리적으로 위치한 Lot:

| Lot ID | 제품 유형 | 수량 | 상태 |
|---|---|---|---|
| LOT-020 | OLED_B | 206 | IN_PROCESS |
| LOT-023 | OLED_A | 289 | IN_PROCESS |

📅 CVR-L1-TFT-01 설비에 예정된 Lot:

| Lot ID | 제품 유형 | 수량 | 상태 | 현재 위치 |
|---|---|---|---|---|
| LOT-020 | OLED_B | 206 | IN_PROCESS | CVR-L1-TFT-01 |
| LOT-023 | OLED_A | 289 | IN_PROCESS | CVR-L1-TFT-01 |
| LOT-005 | LCD_C | 137 | IN_TRANSIT | ⚡ 이동 중 (AGV-L1-CELL-01) |
| LOT-018 | OLED_B | 289 | SCHEDULED |  |
| LOT-029 | LCD_C | 349 | IN_TRANSIT | ⚡ 이동 중 (AGV-L3-PACK-02) |
| LOT-009 | OLED_B | 196 | SCHEDULED |  |
```

---

## State 변화 요약

| 단계 | intent | messages | final_answer |
|------|--------|----------|--------------|
| 초기 | `""` | `[]` | `""` |
| IntentAgent 후 | `"lot_query"` | `[]` | `""` |
| InfoAgent 1차 후 | `"lot_query"` | `[AIMessage(tool_calls×2)]` | `""` |
| ToolNode 후 | `"lot_query"` | `[AIMessage, ToolMessage×2]` | `""` |
| InfoAgent 2차 후 | `"lot_query"` | `[AI, Tool×2, AIMessage]` | `""` |
| ResponseAgent 후 | `"lot_query"` | `[AI, Tool×2, AIMessage]` | `"📍 현재..."` |

---

## 학습 포인트

1. **의미 모호성 해소 = 프롬프트 + Tool docstring**: 코드 변경(조건 분기, 되묻기 로직) 없이 프롬프트 규칙만으로 disambiguation 구현. LLM이 스스로 판단하여 2개 Tool을 동시 호출.
2. **Parallel Tool Calls**: Gemini Function Calling이 1회 호출에서 2개 Tool을 동시 요청. LangGraph의 ToolNode가 자동으로 병렬 실행.
3. **같은 자연어 → 다른 SQL**: "설비의 Lot"이라는 동일한 자연어가 `lot.current_equipment_id` (물리) vs `lot_schedule.equipment_id` (계획)으로 다르게 매핑됨. 이것이 DB 기반 AI 시스템의 핵심 난제.
4. **current ≠ scheduled 감지**: Lot이 이동 중일 때 물리적 위치와 계획 설비가 다른 것을 LLM이 감지하고 별도 표시. 비즈니스 용어 사전이 이를 가능하게 함.
5. **실무 적용**: 이 패턴은 Lot뿐 아니라 "직원의 부서" (현재 소속 vs 발령 예정), "제품의 창고" (현재 위치 vs 출하 예정) 등 모든 DB 기반 AI에서 반복되는 문제.
