# 예시 2: 부하율 조회 — 파라미터 추출 패턴

> **학습 목표**: 자연어에서 FM이 장비유형(`CONVEYOR`)과 라인(`L1`)을 추출하여 Tool 파라미터로 변환하는 과정.
> "L1 컨베이어"라는 표현이 `equipment_type: CONVEYOR, line: L1`으로 매핑되는 FM I/O를 추적한다.

---

## 입력

```
L1 컨베이어 부하율 알려줘
```

---

## Step 1: IntentAgent (의도분석)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human**:
```
L1 컨베이어 부하율 알려줘
```

### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "load_rate_query",
  "detail": {
    "equipment_type": "CONVEYOR",
    "line": "L1",
    "zone": "",
    "equipment_id": "",
    "lot_id": "",
    "hours": 0,
    "keyword": ""
  },
  "reasoning": "L1 컨베이어의 부하율을 묻는 질문이므로 load_rate_query 의도에 해당함"
}
```

> **포인트**: FM이 System 프롬프트의 "장비 유형 매핑: 컨베이어 → CONVEYOR" 규칙을 적용.
> "L1"은 라인 매핑 규칙(L1, L2, L3)에서 인식.

### 파싱 결과
- intent: `load_rate_query`
- detail: `equipment_type=CONVEYOR, line=L1`
- reasoning: L1 컨베이어의 부하율을 묻는 질문이므로 load_rate_query 의도에 해당함

---

## Step 2: InfoAgent (정보조회, 첫 호출)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Human**:
```
사용자 질문: L1 컨베이어 부하율 알려줘
의도: load_rate_query
상세: {"equipment_type": "CONVEYOR", "line": "L1", "zone": "", "equipment_id": "", "lot_id": "", "hours": 0, "keyword": ""}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

### 🔶 FM 출력 (← Gemini) → Tool 호출 요청
- `get_load_rates({'line': 'L1', 'equipment_type': 'CONVEYOR'})`

> **포인트**: FM이 IntentAgent가 추출한 `equipment_type`과 `line`을 그대로 Tool 파라미터로 전달.
> 도구 선택 가이드: "load_rate_query 의도 → get_load_rates" 규칙 적용.

---

## Step 2.5: ToolNode (SQL 실행)

```sql
SELECT e.equipment_id, e.equipment_type, e.line, e.zone,
       lr.load_rate_pct, lr.recorded_at
FROM load_rate lr
JOIN equipment e ON lr.equipment_id = e.equipment_id
WHERE e.line = 'L1' AND e.equipment_type = 'CONVEYOR'
  AND lr.recorded_at >= datetime('now', 'localtime', '-1 hours')
ORDER BY lr.recorded_at DESC
```

### Tool 결과
```
ToolMessage (get_load_rates): []   ← 최근 1시간 내 데이터 없음
```

---

## Step 2 재진입: InfoAgent (Tool 결과 수신)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 재진입)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Messages**: 메시지 히스토리 2건 포함
  - `AIMessage`: (tool_calls: get_load_rates)
  - `ToolMessage`: []

### 🔶 FM 출력 (← Gemini) → 텍스트 응답
```
L1 라인 컨베이어의 부하율 정보가 없습니다.
```

---

## Step 3: ResponseAgent (응답생성)

최종 응답:
```
L1 라인 컨베이어의 부하율 정보가 없습니다.
```

---

## FM 호출 요약

| 단계 | FM 역할 | 핵심 I/O |
|------|---------|---------|
| IntentAgent | 파라미터 추출 | "L1 컨베이어" → `{equipment_type: CONVEYOR, line: L1}` |
| InfoAgent 1차 | Tool 선택 + 파라미터 전달 | intent_detail → `get_load_rates(line=L1, equipment_type=CONVEYOR)` |
| InfoAgent 재진입 | 응답 생성 | `[]` → "부하율 정보가 없습니다" |

**총 FM 호출: 3회**

---

## 학습 포인트

1. **자연어 → 구조화된 파라미터**: "L1 컨베이어"라는 자연어를 FM이 `equipment_type: CONVEYOR, line: L1`로 변환. 이 변환은 System 프롬프트의 "장비 유형 매핑" 테이블에 의존.
2. **IntentAgent → InfoAgent 파라미터 전달**: IntentAgent가 추출한 detail이 InfoAgent의 Human 메시지에 그대로 포함되어 Tool 파라미터로 활용됨.
3. **파라미터가 2개**: FM이 `line`과 `equipment_type` 두 파라미터를 동시에 Tool에 전달. 복합 필터링.
