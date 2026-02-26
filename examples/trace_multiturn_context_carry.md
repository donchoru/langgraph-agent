# 예시 11: 멀티턴 문맥 이어가기 — "그럼 B설비는?" (대명사 해소)

> **학습 목표**: "A설비에 스케줄된 Lot 뭐야?" 다음 "그럼 B설비는?"처럼 **대명사/생략**으로 이전 문맥을 참조하는 패턴.
> FM이 `conversation_history`에서 이전 질문의 구조를 읽어 "B설비의 스케줄된 Lot"으로 해석하는 FM I/O를 추적한다.

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

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human**:
```
CVR-L1-TFT-01에 스케줄된 Lot 뭐야?
```
> conversation_history: 0턴 → 이력 없이 질문만 전달

#### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "lot_query",
  "detail": {
    "equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT",
    "equipment_id": "CVR-L1-TFT-01", "lot_id": "",
    "hours": 0, "keyword": "스케줄"
  },
  "reasoning": "특정 설비에 스케줄된 Lot 조회 요청"
}
```

> **포인트**: `keyword: "스케줄"` 추출 — "스케줄된"이라는 명시적 표현 감지.

### InfoAgent (첫 호출)

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Human**:
```
사용자 질문: CVR-L1-TFT-01에 스케줄된 Lot 뭐야?
의도: lot_query
상세: {..., "keyword": "스케줄"}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

#### 🔶 FM 출력 (← Gemini) → **Tool 1개만 호출**
- `get_lots_scheduled_for_equipment({'equipment_id': 'CVR-L1-TFT-01'})`

> **핵심**: "스케줄된"이 명시 → 모호성 없음 → `get_lots_scheduled_for_equipment` 단일 호출.
> 예시 7("Lot 뭐 있어?" — 모호)과 달리 2개 Tool 호출이 아님.

### ToolNode

```
ToolMessage (get_lots_scheduled_for_equipment): 6건
  LOT-020 | OLED_B | 206 | IN_PROCESS | 현재=CVR-L1-TFT-01 (가동 중)
  LOT-023 | OLED_A | 289 | IN_PROCESS | 현재=CVR-L1-TFT-01 (가동 중)
  LOT-005 | LCD_C  | 137 | IN_TRANSIT | 현재=AGV-L1-CELL-01 (⚡ 이동 중)
  LOT-018 | OLED_B | 289 | SCHEDULED  | 현재=NULL (미배정)
  LOT-029 | LCD_C  | 349 | IN_TRANSIT | 현재=AGV-L3-PACK-02 (⚡ 이동 중)
  LOT-009 | OLED_B | 196 | SCHEDULED  | 현재=NULL (미배정)
```

### ResponseAgent
```
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

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human** (conversation_history 포함):
```
[이전 대화 이력]
사용자: CVR-L1-TFT-01에 스케줄된 Lot 뭐야?
의도: lot_query
응답 요약: 📅 CVR-L1-TFT-01 설비에 예정된 Lot...

[현재 질문]
그럼 SRT-L1-MODULE-01은?

위 대화 이력을 참고하여 현재 질문의 의도를 분석하세요.
'그럼', '거기', '그 설비' 등 대명사는 이전 대화에서 언급된 대상을 참조합니다.
```

> **핵심**: 이 FM 입력이 대명사 해소의 전부. FM이 이 텍스트를 읽고:
> 1. "그럼" → 이전 대화 참조 신호
> 2. "SRT-L1-MODULE-01은?" → 새 설비 ID (주어 교체)
> 3. 생략된 부분: "에 스케줄된 Lot 뭐야?" → 이전 턴에서 유추

#### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "lot_query",
  "detail": {
    "equipment_type": "SORTER", "line": "L1", "zone": "MODULE",
    "equipment_id": "SRT-L1-MODULE-01", "lot_id": "",
    "hours": 0, "keyword": ""
  },
  "reasoning": "이전 대화에서 설비의 스케줄된 Lot을 질문했고, 다른 설비에 대해 같은 질문"
}
```

> **주의**: `keyword: ""` — Turn 1에서는 "스케줄"이 있었지만 Turn 2에서는 생략됨.
> 이것이 InfoAgent의 Tool 선택에 영향을 미침.

### InfoAgent (첫 호출)

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Human** (대화 이력 포함):
```
[이전 대화 이력]
- Q: CVR-L1-TFT-01에 스케줄된 Lot 뭐야? → intent: lot_query, 응답: 📅 CVR-L1-TFT-01에...

사용자 질문: 그럼 SRT-L1-MODULE-01은?
의도: lot_query
상세: {..., "equipment_id": "SRT-L1-MODULE-01", "keyword": ""}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

#### 🔶 FM 출력 (← Gemini) → **Tool 2개 동시 호출**
- `get_lots_on_equipment({'equipment_id': 'SRT-L1-MODULE-01'})`
- `get_lots_scheduled_for_equipment({'equipment_id': 'SRT-L1-MODULE-01'})`

> **흥미로운 점**: Turn 1은 "스케줄된"이 명시되어 **1개 Tool**만 호출했지만,
> Turn 2는 "그럼 ~은?"으로 키워드가 생략되어 `keyword: ""` → **모호한 질문으로 판단 → 2개 Tool 호출**.
> 같은 의도인데도 질문의 명시성에 따라 FM의 Tool 선택 전략이 달라짐.

### ToolNode (2개 병렬)

```
ToolMessage 1 (get_lots_on_equipment):
  []    ← 현재 SRT-L1-MODULE-01에 물리적으로 있는 Lot 없음

ToolMessage 2 (get_lots_scheduled_for_equipment):
  LOT-004 | OLED_B | 388 | IN_TRANSIT (AGV-L3-PACK-02)
  LOT-005 | LCD_C  | 137 | IN_TRANSIT (AGV-L1-CELL-01)
  LOT-025 | OLED_B | ... | IN_PROCESS
  ...
```

### InfoAgent 재진입

#### 🔷 FM 입력 (재진입)
- **Messages**: [AIMessage(tool_calls: 2개), ToolMessage([]), ToolMessage([3건+])]

#### 🔶 FM 출력 (← Gemini)
```
📍 현재 SRT-L1-MODULE-01 설비에 물리적으로 위치한 Lot은 없습니다.

📅 SRT-L1-MODULE-01 설비에 예정된 Lot:
| Lot ID  | 제품   | 수량 | 스케줄 시작          | 현재 위치                    | 상태       |
| LOT-004 | OLED_B | 388  | 2026-02-26 19:57    | ⚡ 이동 중 (AGV-L3-PACK-02)  | IN_TRANSIT |
| LOT-005 | LCD_C  | 137  | 2026-02-26 20:57    | ⚡ 이동 중 (AGV-L1-CELL-01)  | IN_TRANSIT |
| ...
```

---

## Turn 1 vs Turn 2 비교

| 구분 | Turn 1 | Turn 2 |
|------|--------|--------|
| 입력 | "CVR-L1-TFT-01에 스케줄된 Lot 뭐야?" | "그럼 SRT-L1-MODULE-01은?" |
| FM Human 입력 | 질문만 (history 0턴) | **history 1턴 + 질문** |
| 완전한 문장? | O | X (생략 있음) |
| FM 출력 intent | `lot_query` | `lot_query` (이전 턴 참조) |
| FM 출력 keyword | `"스케줄"` | `""` (생략) |
| InfoAgent Tool 수 | **1개** (명확) | **2개** (모호) |

---

## FM 호출 요약 (2턴)

| 턴 | FM 호출 | 핵심 |
|----|---------|------|
| Turn 1 IntentAgent | System(984자) + Human("CVR...스케줄된 Lot 뭐야?") | keyword="스케줄" 추출 |
| Turn 1 InfoAgent 1차 | System(1781자) + Human(질문+의도+keyword) | **1개 Tool** (명확) |
| Turn 1 InfoAgent 재진입 | System + Messages(AI+Tool결과 6건) | 📅 스케줄 응답 |
| Turn 2 IntentAgent | System(984자) + **Human(history + "그럼 ~은?")** | 대명사 해소, keyword="" |
| Turn 2 InfoAgent 1차 | System(1781자) + **Human(history + 질문+keyword="")** | **2개 Tool** (모호) |
| Turn 2 InfoAgent 재진입 | System + Messages(AI+Tool결과2개) | 📍+📅 구분 응답 |

**총 FM 호출: Turn 1에서 3회 + Turn 2에서 3회 = 6회**

---

## 학습 포인트

1. **대명사/생략 해소 = conversation_history + FM 추론**: "그럼 ~은?"이라는 불완전한 질문을 이전 턴의 "스케줄된 Lot 뭐야?"와 결합하여 완전한 의도로 복원. 규칙 기반 파싱이 아닌 FM의 문맥 이해력에 의존.
2. **프롬프트의 명시적 대명사 해소 지시**: `_build_context()` 함수가 `"'그럼', '거기', '그 설비' 등 대명사는 이전 대화에서 언급된 대상을 참조합니다"` 라는 한 줄을 FM 입력에 추가. 이 지시가 없으면 FM이 "그럼 SRT..."를 독립 질문으로 해석할 수 있음.
3. **명확 → 생략 시 Tool 전략 변화**: Turn 1은 "스케줄된"이 명시 → keyword 있음 → 1개 Tool. Turn 2는 키워드 생략 → keyword="" → 모호 판단 → 2개 Tool. **같은 의도라도 질문의 완전성에 따라 FM의 Tool 선택이 달라짐**.
4. **messages 리셋의 효과**: Turn 2의 messages는 빈 상태에서 시작. Turn 1의 ToolMessage(CVR-L1-TFT-01 데이터)가 Turn 2로 유출되지 않음. 덕분에 SRT-L1-MODULE-01 데이터만 깔끔하게 조회.
5. **FM 입력 토큰 비교**: Turn 1 IntentAgent = 질문만(~20자), Turn 2 IntentAgent = history(~200자) + 질문(~25자). 멀티턴일수록 FM 입력이 커지는 토큰 비용 트레이드오프.
