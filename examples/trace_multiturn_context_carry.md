# 예시 11: 멀티턴 문맥 이어가기 — "그럼 B설비는?" (대명사 해소)

> **학습 목표**: "A설비에 스케줄된 Lot 뭐야?" 다음 "그럼 B설비는?"처럼 **대명사/생략**으로 이전 문맥을 참조하는 패턴.
> IntentAgent가 `conversation_history`에서 이전 질문의 구조를 읽어 "B설비의 스케줄된 Lot"으로 해석하는 과정을 추적한다.

---

## 대화 흐름

```
Turn 1: "CVR-L1-TFT-01에 스케줄된 Lot 뭐야?"       ← 명확한 질문
Turn 2: "그럼 SRT-L1-MODULE-01은?"                  ← "그럼 ~은?" = 이전 질문과 같은 구조
```

**핵심**: Turn 2의 "그럼 SRT-L1-MODULE-01은?"은 그 자체로는 의미가 불완전.
이전 턴의 "스케줄된 Lot"이라는 문맥이 있어야 "SRT-L1-MODULE-01에 스케줄된 Lot 뭐야?"로 해석됨.

---

## Turn 1: CVR-L1-TFT-01에 스케줄된 Lot 뭐야?

### IntentAgent

```
State BEFORE:
  user_input: "CVR-L1-TFT-01에 스케줄된 Lot 뭐야?"
  conversation_history: 0턴
  intent: ""

LLM 출력:
  intent: "lot_query"
  detail: {
    "equipment_type": "CONVEYOR",
    "line": "L1",
    "zone": "TFT",
    "equipment_id": "CVR-L1-TFT-01",
    "lot_id": "",
    "hours": 0,
    "keyword": "스케줄"              ← "스케줄된" 키워드 추출
  }
  reasoning: "특정 설비에 스케줄된 Lot 조회 요청"
```

### InfoAgent

```
1차 호출:
  LLM 판단: "스케줄된" 키워드 → get_lots_scheduled_for_equipment 단일 호출
  tool_calls: [get_lots_scheduled_for_equipment({"equipment_id":"CVR-L1-TFT-01"})]
                                                 ↑ 명확한 질문 → 1개 Tool만
```

**포인트**: "스케줄된"이 명시되어 있으므로 disambiguation 불필요. `get_lots_on_equipment` 호출 안 함.

### ToolNode

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

```
ToolMessage 결과 (6건):
  LOT-020 | OLED_B | 206 | IN_PROCESS | 현재=CVR-L1-TFT-01 (가동 중)
  LOT-023 | OLED_A | 289 | IN_PROCESS | 현재=CVR-L1-TFT-01 (가동 중)
  LOT-005 | LCD_C  | 137 | IN_TRANSIT | 현재=AGV-L1-CELL-01 (⚡ 이동 중)
  LOT-018 | OLED_B | 289 | SCHEDULED  | 현재=NULL (미배정)
  LOT-029 | LCD_C  | 349 | IN_TRANSIT | 현재=AGV-L3-PACK-02 (⚡ 이동 중)
  LOT-009 | OLED_B | 196 | SCHEDULED  | 현재=NULL (미배정)
```

### ResponseAgent

```
final_answer:
  📅 CVR-L1-TFT-01 설비에 예정된 Lot:
  | Lot ID  | 제품   | 수량 | 예정 시작          | 현재 위치                    | 상태       |
  | LOT-020 | OLED_B | 206  | 2026-02-26 20:57  | CVR-L1-TFT-01               | 가동 중    |
  | LOT-023 | OLED_A | 289  | 2026-02-26 21:57  | CVR-L1-TFT-01               | 가동 중    |
  | LOT-005 | LCD_C  | 137  | 2026-02-26 22:57  | ⚡ 이동 중 (AGV-L1-CELL-01)  | IN_TRANSIT |
  | LOT-018 | OLED_B | 289  | 2026-02-26 23:57  |                              | SCHEDULED  |
  | ...
```

### 대화 이력 저장

```python
conversation_history = [
    {"user": "CVR-L1-TFT-01에 스케줄된 Lot 뭐야?",
     "intent": "lot_query",
     "answer": "📅 CVR-L1-TFT-01 설비에 예정된 Lot..."}
]
```

---

## Turn 2: 그럼 SRT-L1-MODULE-01은?

### IntentAgent — ⚡ 핵심: 대명사 + 생략 해소

```
State BEFORE:
  user_input: "그럼 SRT-L1-MODULE-01은?"
  conversation_history: 1턴
    - Q: "CVR-L1-TFT-01에 스케줄된 Lot 뭐야?" → lot_query

LLM 입력 (conversation_history 포함):
  [이전 대화 이력]
  사용자: CVR-L1-TFT-01에 스케줄된 Lot 뭐야?
  의도: lot_query
  응답 요약: 📅 CVR-L1-TFT-01 설비에 예정된 Lot...

  [현재 질문]
  그럼 SRT-L1-MODULE-01은?

  위 대화 이력을 참고하여 현재 질문의 의도를 분석하세요.
  '그럼', '거기', '그 설비' 등 대명사는 이전 대화에서 언급된 대상을 참조합니다.

LLM 출력:
  intent: "lot_query"                                  ← 이전과 같은 의도!
  detail: {
    "equipment_type": "SORTER",
    "line": "L1",
    "zone": "MODULE",
    "equipment_id": "SRT-L1-MODULE-01",                ← 새 설비 ID 추출
    "lot_id": "",
    "hours": 0,
    "keyword": ""
  }
  reasoning: "이전 대화에서 설비의 스케줄된 Lot을 질문했고,
              다른 설비(SRT-L1-MODULE-01)에 대해 같은 질문"
```

**핵심 분석**:
1. "그럼" → 이전 대화 참조 신호
2. "SRT-L1-MODULE-01은?" → 새 설비 ID (주어 교체)
3. 생략된 부분: "에 스케줄된 Lot 뭐야?" → 이전 턴에서 유추
4. IntentAgent가 이 모든 것을 `conversation_history` 문맥으로 해소

### InfoAgent

```
1차 호출:
  프롬프트에 대화 이력 포함:
    [이전 대화 이력]
    - Q: CVR-L1-TFT-01에 스케줄된 Lot 뭐야? → intent: lot_query

  LLM 판단: 이전 턴에서 스케줄된 Lot을 물었지만,
            detail에 keyword가 비어있고 equipment_id만 있음
            → disambiguation 규칙 적용 → 모호하므로 두 Tool 호출

  tool_calls: [
    get_lots_on_equipment({"equipment_id":"SRT-L1-MODULE-01"}),
    get_lots_scheduled_for_equipment({"equipment_id":"SRT-L1-MODULE-01"})
  ]
```

**흥미로운 점**: Turn 1은 "스케줄된"이 명시되어 1개 Tool만 호출했지만,
Turn 2는 "그럼 ~은?"으로 키워드가 생략되어 **모호한 질문으로 판단 → 2개 Tool 호출**.
같은 의도인데도 질문의 명시성에 따라 Tool 선택 전략이 달라짐.

### ToolNode

```
ToolMessage 1 (get_lots_on_equipment):
  []    ← 현재 SRT-L1-MODULE-01에 물리적으로 있는 Lot 없음

ToolMessage 2 (get_lots_scheduled_for_equipment):
  [
    {"lot_id":"LOT-004","product_type":"OLED_B","quantity":388,
     "current_equipment_id":"AGV-L3-PACK-02",
     "scheduled_equipment_id":"SRT-L1-MODULE-01",
     "status":"IN_TRANSIT"},                              ← 이동 중
    {"lot_id":"LOT-005","product_type":"LCD_C","quantity":137,
     "current_equipment_id":"AGV-L1-CELL-01",
     "scheduled_equipment_id":"SRT-L1-MODULE-01",
     "status":"IN_TRANSIT"},                              ← 이동 중
    {"lot_id":"LOT-025",...,"status":"IN_PROCESS"},
    ...
  ]
```

### ResponseAgent

```
final_answer:
  📍 현재 SRT-L1-MODULE-01 설비에 물리적으로 위치한 Lot은 없습니다.

  📅 SRT-L1-MODULE-01 설비에 예정된 Lot:
  | Lot ID  | 제품   | 수량 | 스케줄 시작          | 현재 위치                    | 상태       |
  | LOT-004 | OLED_B | 388  | 2026-02-26 19:57    | ⚡ 이동 중 (AGV-L3-PACK-02)  | IN_TRANSIT |
  | LOT-005 | LCD_C  | 137  | 2026-02-26 20:57    | ⚡ 이동 중 (AGV-L1-CELL-01)  | IN_TRANSIT |
  | LOT-025 | OLED_B | 470  | ...                  | ...                          | ...        |
```

---

## Turn 1 vs Turn 2 비교

| 구분 | Turn 1 | Turn 2 |
|------|--------|--------|
| 입력 | "CVR-L1-TFT-01에 스케줄된 Lot 뭐야?" | "그럼 SRT-L1-MODULE-01은?" |
| 완전한 문장? | O | X (생략 있음) |
| history | 0턴 | 1턴 |
| intent | `lot_query` | `lot_query` (이전 턴 참조) |
| equipment_id | CVR-L1-TFT-01 | SRT-L1-MODULE-01 |
| keyword | "스케줄" | "" (생략) |
| Tool 수 | **1개** (명확) | **2개** (모호) |
| 물리적 Lot | 2건 있음 | 0건 |
| 스케줄 Lot | 6건 | 3건+ |

---

## 학습 포인트

1. **대명사/생략 해소 = conversation_history + LLM 추론**: "그럼 ~은?"이라는 불완전한 질문을 이전 턴의 "스케줄된 Lot 뭐야?"와 결합하여 완전한 의도로 복원. 규칙 기반 파싱이 아닌 LLM의 문맥 이해력에 의존.
2. **프롬프트의 명시적 대명사 해소 지시**: IntentAgent 프롬프트에 `"'그럼', '거기', '그 설비' 등 대명사는 이전 대화에서 언급된 대상을 참조합니다"` 라는 한 줄이 핵심. 이 지시가 없으면 LLM이 "그럼 SRT..."를 독립 질문으로 해석할 수 있음.
3. **명확 → 생략 시 Tool 전략 변화**: Turn 1은 "스케줄된"이 명시 → 1개 Tool. Turn 2는 키워드 생략 → 모호 판단 → 2개 Tool. **같은 의도라도 질문의 완전성에 따라 disambiguation 전략이 달라짐**.
4. **messages 리셋의 효과**: Turn 2의 messages는 빈 상태에서 시작. Turn 1의 ToolMessage(CVR-L1-TFT-01 데이터)가 Turn 2로 유출되지 않음. 덕분에 SRT-L1-MODULE-01 데이터만 깔끔하게 조회.
5. **실무 확장**: 이 패턴은 "그럼 어제는?", "다른 라인은?", "WARNING만 보여줘" 등 모든 후속 질문에 적용됨. `conversation_history`에 이전 턴의 의도/파라미터가 저장되어 있으므로 LLM이 생략된 부분을 복원할 수 있음.
