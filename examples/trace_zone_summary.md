# 예시 3: 구간별 부하율 요약 — 같은 의도, 다른 Tool 선택

> **학습 목표**: 같은 `load_rate_query` 의도라도 FM이 "구간별 요약"이라는 키워드를 보고
> `get_load_rates` 대신 `get_zone_summary`를 선택하는 과정. FM의 Tool 선택 판단력을 추적한다.

---

## 입력

```
L2 구간별 부하율 요약해줘
```

---

## Step 1: IntentAgent (의도분석)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human**:
```
L2 구간별 부하율 요약해줘
```

### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "load_rate_query",
  "detail": {
    "equipment_type": "",
    "line": "L2",
    "zone": "",
    "equipment_id": "",
    "lot_id": "",
    "hours": 0,
    "keyword": "구간별 요약"
  },
  "reasoning": "L2 라인의 구간별 부하율 요약을 요청하는 것으로 판단"
}
```

> **포인트**: 의도는 예시 2와 동일한 `load_rate_query`이지만, `keyword: "구간별 요약"`이 추출됨.
> 이 키워드가 InfoAgent의 Tool 선택에 영향을 미침.

---

## Step 2: InfoAgent (정보조회, 첫 호출)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Human**:
```
사용자 질문: L2 구간별 부하율 요약해줘
의도: load_rate_query
상세: {"equipment_type": "", "line": "L2", "zone": "", "equipment_id": "", "lot_id": "", "hours": 0, "keyword": "구간별 요약"}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

### 🔶 FM 출력 (← Gemini) → Tool 호출 요청
- `get_zone_summary({'line': 'L2'})`

> **핵심**: 같은 `load_rate_query` 의도인데 예시 2에서는 `get_load_rates`, 여기서는 `get_zone_summary`.
> FM이 "구간별 요약"이라는 사용자 질문 + `keyword: "구간별 요약"`을 보고
> 도구 선택 가이드의 "load_rate_query → get_load_rates (+ 필요시 get_zone_summary)" 중 후자를 선택.

---

## Step 2.5: ToolNode (SQL 실행)

```sql
SELECT e.zone,
       ROUND(AVG(lr.load_rate_pct), 1) AS avg_load,
       ROUND(MAX(lr.load_rate_pct), 1) AS max_load,
       COUNT(DISTINCT e.equipment_id) AS equip_count
FROM load_rate lr
JOIN equipment e ON lr.equipment_id = e.equipment_id
WHERE e.line = 'L2'
  AND lr.recorded_at >= datetime('now', 'localtime', '-1 hours')
GROUP BY e.zone
```

### Tool 결과
```
ToolMessage (get_zone_summary): []   ← 최근 1시간 내 데이터 없음
```

---

## Step 2 재진입: InfoAgent (Tool 결과 수신)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 재진입)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Messages**: 2건
  - `AIMessage`: (tool_calls: get_zone_summary)
  - `ToolMessage`: []

### 🔶 FM 출력 (← Gemini) → 텍스트 응답
```
앗, L2 라인에는 구간별 부하율 요약 정보가 아직 없네요. 다른 라인을 선택하거나, 잠시 후에 다시 시도해 주시겠어요?
```

---

## Step 3: ResponseAgent (응답생성)

최종 응답:
```
앗, L2 라인에는 구간별 부하율 요약 정보가 아직 없네요.
다른 라인을 선택하거나, 잠시 후에 다시 시도해 주시겠어요?
```

---

## 예시 2 vs 예시 3 비교: 같은 의도, 다른 Tool

| 구분 | 예시 2 | 예시 3 |
|------|--------|--------|
| 입력 | "L1 컨베이어 부하율 알려줘" | "L2 구간별 부하율 요약해줘" |
| 의도 | `load_rate_query` | `load_rate_query` |
| keyword | (없음) | `구간별 요약` |
| **FM이 선택한 Tool** | `get_load_rates` | `get_zone_summary` |
| 파라미터 | `line=L1, equipment_type=CONVEYOR` | `line=L2` |

---

## 학습 포인트

1. **같은 의도, 다른 Tool 선택**: `load_rate_query`라는 동일 의도에서 FM이 사용자 질문의 뉘앙스("구간별 요약")를 읽고 다른 Tool을 선택. 의도 분류만으로는 Tool이 결정되지 않음.
2. **keyword 필드의 역할**: IntentAgent가 추출한 `keyword: "구간별 요약"`이 InfoAgent의 Human 메시지에 포함되어 Tool 선택 판단의 힌트로 작용.
3. **FM의 Tool 선택은 규칙 + 맥락**: 도구 선택 가이드가 "load_rate_query → get_load_rates (+ 필요시 get_zone_summary)"로 되어 있어, FM이 맥락에 따라 적절한 Tool을 고름.
