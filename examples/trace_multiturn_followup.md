# 예시 9: 멀티턴 연속 대화 — 같은 주제 심화 (overload → L1 필터 → 장비 상세)

> **학습 목표**: 3턴에 걸쳐 같은 주제를 점점 좁혀가는 멀티턴 대화 패턴.
> `conversation_history`가 FM의 입력에 포함되어 문맥을 유지하는 FM I/O를 추적한다.

---

## 대화 흐름

```
Turn 1: "과부하 장비 있어?"
Turn 2: "그 중에서 L1 라인만 보여줘"     ← "그 중에서" = 이전 턴 참조
Turn 3: "CVR-L1-CELL-01 상세 정보 알려줘"  ← Turn2 결과에서 특정 장비 선택
```

---

## Turn 1: 과부하 장비 있어?

### IntentAgent

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human**:
```
과부하 장비 있어?
```
> conversation_history: 0턴 → 이력 없이 질문만 전달

#### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "overload_check",
  "detail": {"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "lot_id": "", "hours": 0, "keyword": ""},
  "reasoning": "과부하 장비 확인 요청"
}
```

### InfoAgent (첫 호출)

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Human**:
```
사용자 질문: 과부하 장비 있어?
의도: overload_check
상세: {"equipment_type": "", "line": "", ...}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

#### 🔶 FM 출력 (← Gemini) → Tool 호출
- `get_overloaded_equipment({})`

### ToolNode → InfoAgent 재진입

#### 🔷 FM 입력 (재진입)
- **Messages**: [AIMessage(tool_calls), ToolMessage(과부하 장비 목록)]

#### 🔶 FM 출력 (← Gemini)
```
🚨 최근 1시간 동안 과부하 상태인 장비 목록:
| 장비 ID         | 유형     | 라인 | 구간   | 부하율(%) | 상태  |
| CVR-L1-CELL-01  | CONVEYOR | L1   | CELL   | 99.8      | ERROR |
| SHT-L3-CELL-01  | SHUTTLE  | L3   | CELL   | 99.3      | ERROR |
| AGV-L1-CELL-01  | AGV      | L1   | CELL   | 99.1      | ERROR |
| ...
```

### 대화 이력 저장
```python
conversation_history = [
    {"user": "과부하 장비 있어?", "intent": "overload_check",
     "answer": "🚨 최근 1시간 동안 과부하 상태인 장비 목록..."}
]
```

---

## Turn 2: 그 중에서 L1 라인만 보여줘

### IntentAgent — ⚡ 핵심: 대화 이력이 FM 입력에 포함

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human** (conversation_history 포함):
```
[이전 대화 이력]
사용자: 과부하 장비 있어?
의도: overload_check
응답 요약: 🚨 최근 1시간 동안 과부하 상태인 장비 목록...

[현재 질문]
그 중에서 L1 라인만 보여줘

위 대화 이력을 참고하여 현재 질문의 의도를 분석하세요.
'그럼', '거기', '그 설비' 등 대명사는 이전 대화에서 언급된 대상을 참조합니다.
```

> **핵심**: `_build_context()` 함수가 conversation_history를 FM 입력에 주입.
> "그 중에서"라는 대명사를 FM이 해소하기 위한 문맥 제공.

#### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "overload_check",
  "detail": {"line": "L1", ...},
  "reasoning": "이전 대화에서 과부하 장비를 조회했고, L1 라인만 필터링 요청"
}
```

> **포인트**: 이전 턴과 같은 `overload_check` 의도. FM이 "그 중에서"를 이전 턴의 과부하 결과로 해석.

### InfoAgent (첫 호출)

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (1781자)
- **Human** (대화 이력 포함):
```
[이전 대화 이력]
- Q: 과부하 장비 있어? → intent: overload_check, 응답: 🚨 최근 1시간...

사용자 질문: 그 중에서 L1 라인만 보여줘
의도: overload_check
상세: {"line": "L1", ...}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

#### 🔶 FM 출력 (← Gemini) → Tool 호출
- `get_overloaded_equipment({})`

> **참고**: Tool 파라미터에 L1 필터가 없음 → FM이 Tool 결과에서 L1만 필터링하여 응답 생성.

### ToolNode → InfoAgent 재진입

#### 🔶 FM 출력 (← Gemini) — L1만 필터링
```
🚨 L1 라인 과부하 장비:
| 장비 ID         | 유형     | 구간 | 부하율(%) |
| CVR-L1-CELL-01  | CONVEYOR | CELL | 99.8      |
| AGV-L1-CELL-01  | AGV      | CELL | 99.1      |
```

---

## Turn 3: CVR-L1-CELL-01 상세 정보 알려줘

### IntentAgent

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (984자)
- **Human** (conversation_history 2턴 포함):
```
[이전 대화 이력]
사용자: 과부하 장비 있어?
의도: overload_check
응답 요약: 🚨 최근 1시간 동안 과부하 상태인 장비 목록...

사용자: 그 중에서 L1 라인만 보여줘
의도: overload_check
응답 요약: 🚨 L1 라인 과부하 장비...

[현재 질문]
CVR-L1-CELL-01 상세 정보 알려줘

위 대화 이력을 참고하여 현재 질문의 의도를 분석하세요.
```

#### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "equipment_status",
  "detail": {"equipment_id": "CVR-L1-CELL-01", ...},
  "reasoning": "특정 장비의 상세 정보 요청"
}
```

> **포인트**: 의도가 `overload_check` → `equipment_status`로 전환!
> 같은 주제(과부하 장비)에서 의도가 자연스럽게 바뀜.

### InfoAgent → ToolNode

#### 🔶 FM 출력 (← Gemini) → Tool 호출
- `get_equipment_detail({'equipment_id': 'CVR-L1-CELL-01'})`

---

## FM 호출 요약 (3턴)

| 턴 | IntentAgent FM 입력 특징 | 의도 | InfoAgent Tool |
|----|--------------------------|------|----------------|
| 1 | history 없음, 질문만 | `overload_check` | `get_overloaded_equipment` |
| 2 | **history 1턴 포함** | `overload_check` | `get_overloaded_equipment` (결과 필터링) |
| 3 | **history 2턴 포함** | `equipment_status` ← 전환! | `get_equipment_detail` |

---

## 학습 포인트

1. **conversation_history가 FM 입력에 포함**: `_build_context()` 함수가 최근 5턴의 이력을 `[이전 대화 이력]` 블록으로 구성하여 FM의 Human 메시지에 주입. 턴이 쌓일수록 FM 입력 토큰이 증가.
2. **대명사 해소는 FM이 수행**: "그 중에서"를 코드로 파싱하지 않음. FM이 conversation_history를 읽고 이전 턴의 과부하 장비 목록을 참조.
3. **같은 주제 내 의도 전환**: Turn 1,2는 `overload_check`, Turn 3은 `equipment_status`. 대화 주제가 같아도 의도는 자유롭게 바뀔 수 있음.
4. **필터링은 FM이 응답 단계에서 처리**: Turn 2에서 `get_overloaded_equipment`는 전체 데이터를 반환하지만, FM이 재진입 시 L1만 필터링하여 응답 생성. Tool 파라미터로 필터하는 것과 FM이 결과를 필터하는 것은 다른 전략.
5. **messages는 턴마다 리셋**: Turn 2의 `messages: []`는 빈 상태에서 시작. Turn 1의 Tool 결과(과부하 데이터)가 Turn 2로 유출되지 않음. `conversation_history`만 요약 형태로 전달.
