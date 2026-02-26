# 예시 10: 멀티턴 토픽 전환 — Lot 질문 후 장비 상태 질문 (intent 완전 변경)

> **학습 목표**: 멀티턴 대화에서 **완전히 다른 주제**로 전환했을 때 FM이 어떻게 반응하는지.
> `conversation_history`에 이전 토픽이 남아있지만, FM이 현재 질문의 의도를 독립적으로 판단하는 FM I/O를 추적한다.

---

## 대화 흐름

```
Turn 1: "CVR-L1-TFT-01에 Lot 뭐 있어?"    ← lot_query
Turn 2: "L2 장비 상태 어때?"                ← equipment_status (완전 토픽 전환)
```

---

## Turn 1: CVR-L1-TFT-01에 Lot 뭐 있어?

### IntentAgent

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human**:
```
CVR-L1-TFT-01에 Lot 뭐 있어?
```

#### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "lot_query",
  "detail": {"equipment_id": "CVR-L1-TFT-01", "lot_id": ""},
  "reasoning": "특정 장비에 Lot이 있는지 확인하는 질문"
}
```

### InfoAgent → ToolNode (2개 Tool 동시 호출 — 모호한 질문)

#### 🔶 FM 출력 (← Gemini) → Tool 2개 동시 호출
- `get_lots_on_equipment({'equipment_id': 'CVR-L1-TFT-01'})`
- `get_lots_scheduled_for_equipment({'equipment_id': 'CVR-L1-TFT-01'})`

### ResponseAgent
```
📍 CVR-L1-TFT-01에 현재 물리적으로 있는 Lot:
| LOT-020 | OLED_B | 206 | IN_PROCESS |
| LOT-023 | OLED_A | 289 | IN_PROCESS |

📅 CVR-L1-TFT-01에 예정된 Lot:
| LOT-020 | ... | CVR-L1-TFT-01 |
| LOT-005 | ... | ⚡ 이동 중 (AGV-L1-CELL-01) |
| ...
```

---

## Turn 2: L2 장비 상태 어때?

### IntentAgent — ⚡ 핵심: 토픽 전환 감지

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human** (conversation_history 포함):
```
[이전 대화 이력]
사용자: CVR-L1-TFT-01에 Lot 뭐 있어?
의도: lot_query
응답 요약: 📍 CVR-L1-TFT-01에 현재 물리적으로 있는 Lot...

[현재 질문]
L2 장비 상태 어때?

위 대화 이력을 참고하여 현재 질문의 의도를 분석하세요.
'그럼', '거기', '그 설비' 등 대명사는 이전 대화에서 언급된 대상을 참조합니다.
```

> **핵심**: conversation_history에 `lot_query`가 있지만, 현재 질문은 "L2 장비 상태" → 완전히 다른 주제.

#### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "equipment_status",
  "detail": {"line": "L2"},
  "reasoning": "L2 라인의 장비 상태를 요청하고 있음"
}
```

> **포인트**: FM이 `lot_query` → `equipment_status` 전환!
> conversation_history에 이전 토픽이 있지만 **현재 질문의 의도를 독립적으로 판단**.
> 프롬프트: "이전 대화를 **참고**하되, 현재 질문의 의도를 분석하세요" → "참고"이지 "따르기"가 아님.

### InfoAgent

#### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Human** (대화 이력 포함):
```
[이전 대화 이력]
- Q: CVR-L1-TFT-01에 Lot 뭐 있어? → intent: lot_query, 응답: 📍 CVR-L1-TFT-01에...

사용자 질문: L2 장비 상태 어때?
의도: equipment_status
상세: {"line": "L2"}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

#### 🔶 FM 출력 (← Gemini) → Tool 호출
- `get_equipment_status({'line': 'L2'})`

> **포인트**: 이전 턴의 Lot Tool이 아닌 장비 상태 Tool. 현재 의도(equipment_status)에 맞는 Tool만 호출.

### ToolNode → InfoAgent 재진입

#### 🔶 FM 출력 (← Gemini)
```
L2 라인의 장비 상태:
| 상태    | 대수 |
| RUNNING | 4    |

| 장비 ID         | 유형     | 구간   | 상태    |
| CRN-L2-PACK-01  | CRANE    | PACK   | RUNNING |
| CVR-L2-CELL-01  | CONVEYOR | CELL   | RUNNING |
| SHT-L2-TFT-01   | SHUTTLE  | TFT    | RUNNING |
| STK-L2-TFT-01   | STACKER  | TFT    | RUNNING |
```

---

## FM 호출 비교 (Turn 1 vs Turn 2)

| 구분 | Turn 1 | Turn 2 |
|------|--------|--------|
| FM Human 입력 | "CVR-L1-TFT-01에 Lot 뭐 있어?" | history + "L2 장비 상태 어때?" |
| **history 포함** | X (0턴) | **O (1턴 — lot_query)** |
| FM 출력 intent | `lot_query` | `equipment_status` |
| InfoAgent Tool | Lot Tool 2개 | 장비 상태 Tool 1개 |

---

## 학습 포인트

1. **토픽 전환 시 intent 독립 판단**: conversation_history에 이전 토픽(lot_query)이 있지만, FM이 현재 질문만으로 `equipment_status`를 정확히 분류. 이전 문맥에 "오염"되지 않음.
2. **이력은 참고용, 결정은 현재 질문 기준**: 프롬프트 설계에서 "이전 대화를 **참고**하되, 현재 질문의 의도를 분석하세요"라고 지시한 것이 핵심.
3. **Tool 선택도 완전 전환**: Turn 1은 Lot Tool 2개, Turn 2는 장비 Tool 1개. 이전 턴의 Tool과 무관하게 현재 의도에 맞는 Tool만 호출.
4. **messages는 턴마다 리셋**: Turn 2의 messages는 빈 상태에서 시작. Turn 1의 Tool 결과(Lot 데이터)가 Turn 2로 유출되지 않음. conversation_history만 요약 형태로 전달.
5. **FM 입력 토큰 증가**: Turn 2에서 FM의 Human 메시지에 이전 턴 이력이 포함되어 Turn 1보다 입력이 길어짐. 이것이 멀티턴의 토큰 비용.
