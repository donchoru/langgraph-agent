# 예시 1: 과부하 장비 확인 — Tool Loop 패턴

> **학습 목표**: `overload_check` 의도에서 FM(Foundation Model)이 어떤 입력을 받고 어떤 출력을 내는지,
> InfoAgent → ToolNode → InfoAgent 재진입 Tool Loop의 전체 흐름을 FM I/O 관점에서 추적한다.

---

## 입력

```
과부하 장비 있어?
```

---

## Step 1: IntentAgent (의도분석)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human**:
```
과부하 장비 있어?
```

### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "overload_check",
  "detail": {
    "equipment_type": "",
    "line": "",
    "zone": "",
    "equipment_id": "",
    "lot_id": "",
    "hours": 0,
    "keyword": ""
  },
  "reasoning": "과부하 장비 확인 요청은 overload_check에 해당함"
}
```

### 파싱 결과
- intent: `overload_check`
- detail: 필터 없음 (전체 조회)
- reasoning: 과부하 장비 확인 요청은 overload_check에 해당함

---

## Step 2: InfoAgent (정보조회, 첫 호출)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Human**:
```
사용자 질문: 과부하 장비 있어?
의도: overload_check
상세: {"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "lot_id": "", "hours": 0, "keyword": ""}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

### 🔶 FM 출력 (← Gemini) → Tool 호출 요청
- `get_overloaded_equipment({})`

> **포인트**: FM이 `overload_check` 의도 + 도구 선택 가이드를 보고 `get_overloaded_equipment` Tool을 선택.
> 파라미터 없이 전체 과부하 장비 조회.

---

## Step 2.5: ToolNode (SQL 실행)

```sql
SELECT e.equipment_id, e.equipment_type, e.line, e.zone, e.status,
       lr.load_rate_pct, at.warning_pct, at.critical_pct
FROM load_rate lr
JOIN equipment e ON lr.equipment_id = e.equipment_id
JOIN alert_threshold at ON e.equipment_type = at.equipment_type
WHERE lr.load_rate_pct >= at.warning_pct
  AND lr.recorded_at >= datetime('now', 'localtime', '-1 hours')
```

### Tool 결과
```
ToolMessage (get_overloaded_equipment): []   ← 최근 1시간 내 과부하 장비 없음
```

> **참고**: 시드 데이터의 부하율 타임스탬프가 현재 시간과 1시간 이상 차이나면 빈 결과 반환.
> 실제 운영 중에는 실시간 데이터가 있으므로 결과가 채워짐.

---

## Step 2 재진입: InfoAgent (Tool 결과 수신)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 재진입)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Messages**: 메시지 히스토리 2건 포함
  - `AIMessage`: (tool_calls: get_overloaded_equipment)
  - `ToolMessage`: []

### 🔶 FM 출력 (← Gemini) → 텍스트 응답
```
1시간 동안 과부하 상태인 장비는 없습니다.
```

> **포인트**: FM이 빈 배열 `[]`을 받고 "데이터 없음"을 사용자 친화적으로 변환.
> 시스템 프롬프트의 "데이터가 없으면 솔직하게 안내" 규칙 적용.

---

## Step 3: ResponseAgent (응답생성)

최종 응답 추출 (InfoAgent 재진입에서 생성된 텍스트):
```
1시간 동안 과부하 상태인 장비는 없습니다.
```

---

## FM 호출 요약

| 단계 | FM 역할 | 입력 | 출력 |
|------|---------|------|------|
| IntentAgent | 의도 분류 | System(984자) + Human("과부하 장비 있어?") | JSON: `overload_check` |
| InfoAgent 1차 | Tool 선택 | System(1781자) + Human(질문+의도+상세) | tool_call: `get_overloaded_equipment` |
| InfoAgent 재진입 | 응답 생성 | System(1781자) + Messages(AI+Tool결과) | 텍스트: "1시간 동안..." |

**총 FM 호출: 3회** (IntentAgent 1 + InfoAgent 2)

---

## 학습 포인트

1. **FM은 3번 호출됨**: 의도분류 → Tool 선택 → 응답 생성. 각 호출마다 다른 System 프롬프트와 다른 역할.
2. **Tool Loop 패턴**: InfoAgent가 Tool을 호출하면 ToolNode가 실행하고 다시 InfoAgent로 돌아옴. FM이 Tool 결과를 받아 최종 텍스트 응답을 생성.
3. **빈 결과 처리**: FM이 `[]` (빈 배열)을 받으면 "데이터가 없으면 솔직하게 안내" 규칙에 따라 사용자 친화적 메시지 생성.
4. **프롬프트 크기**: IntentAgent(984자)는 의도 분류에 집중, InfoAgent(1781자)는 Tool 선택 + 모호성 해소 규칙까지 포함하여 더 큼.
