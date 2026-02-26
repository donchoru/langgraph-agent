# 예시 6: 과부하 원인 분석 — 복합 데이터 분석 패턴

> **학습 목표**: 특정 장비의 과부하 "원인 분석"을 요청했을 때 FM이 장비 상세(부하율 이력 + 알림 이력)를
> 한꺼번에 조회하고 종합 분석하는 패턴. FM이 대량의 시계열 데이터를 읽고 패턴을 찾는 과정을 추적한다.

---

## 입력

```
CVR-L1-CELL-01 과부하 원인 분석해줘
```

---

## Step 1: IntentAgent (의도분석)

### FM 입력 (-> Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human**:
```
CVR-L1-CELL-01 과부하 원인 분석해줘
```

### FM 출력 (<- Gemini)
```json
{
  "intent": "overload_check",
  "detail": {
    "equipment_type": "CONVEYOR",
    "line": "L1",
    "zone": "CELL",
    "equipment_id": "CVR-L1-CELL-01",
    "lot_id": "",
    "hours": 0,
    "keyword": "원인"
  },
  "reasoning": "특정 장비의 과부하 원인 분석 요청이므로 overload_check 의도이며, 장비 ID에서 장비 유형, 라인, 구간을 추출함. '원인' 키워드 추가."
}
```

> **포인트**: FM이 장비 ID `CVR-L1-CELL-01`에서 유형(`CONVEYOR`), 라인(`L1`), 구간(`CELL`)을 역파싱.
> "원인"이라는 키워드도 `keyword` 필드에 추출 -- InfoAgent의 Tool 선택에 영향.

---

## Step 2: InfoAgent (정보조회, 첫 호출)

### FM 입력 (-> Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Human**:
```
사용자 질문: CVR-L1-CELL-01 과부하 원인 분석해줘
의도: overload_check
상세: {"equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "equipment_id": "CVR-L1-CELL-01", "lot_id": "", "hours": 0, "keyword": "원인"}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

### FM 출력 (<- Gemini) -> Tool 호출 요청
- `get_equipment_detail({'equipment_id': 'CVR-L1-CELL-01'})`

> **포인트**: `overload_check` 의도이지만 FM이 `get_overloaded_equipment`가 아닌 `get_equipment_detail`을 선택.
> "원인 분석"에는 과부하 목록이 아닌 **개별 장비의 상세 이력**이 필요하다고 FM이 판단.
> 도구 선택 가이드: "특정 장비 ID 언급 시 -> get_equipment_detail" 규칙 적용.

---

## Step 2.5: ToolNode (SQL 실행)

```sql
-- 장비 기본 정보
SELECT * FROM equipment WHERE equipment_id = 'CVR-L1-CELL-01'

-- 부하율 이력 (최근 24건)
SELECT recorded_at, load_rate_pct, throughput, queue_length
FROM load_rate WHERE equipment_id = 'CVR-L1-CELL-01'
ORDER BY recorded_at DESC LIMIT 24

-- 알림 이력 (최근 10건)
SELECT triggered_at, alert_type, load_rate_pct, threshold_pct, message
FROM alert_history WHERE equipment_id = 'CVR-L1-CELL-01'
ORDER BY triggered_at DESC LIMIT 10
```

### Tool 결과 (발췌)
```json
{
  "equipment": [{"equipment_id": "CVR-L1-CELL-01", "status": "ERROR", ...}],
  "load_history": [
    {"recorded_at": "2026-02-26 22:08:59", "load_rate_pct": 98.3, "throughput": 84, "queue_length": 17},
    {"recorded_at": "2026-02-26 21:58:59", "load_rate_pct": 96.9, "throughput": 97, "queue_length": 2},
    {"recorded_at": "2026-02-26 21:48:59", "load_rate_pct": 84.6, ...},
    ...
  ],
  "alert_history": [
    {"alert_type": "CRITICAL", "load_rate_pct": 98.3, "threshold_pct": 95.0, ...},
    {"alert_type": "CRITICAL", "load_rate_pct": 96.9, ...},
    ...
  ]
}
```

> **포인트**: `get_equipment_detail`은 3개 SQL을 실행하여 장비정보 + 부하율이력 24건 + 알림이력 10건을 한꺼번에 반환.
> 이 대량 데이터가 FM 재진입 시 입력으로 들어감.

---

## Step 2 재진입: InfoAgent (Tool 결과 수신)

### FM 입력 (-> Gemini gemini-2.0-flash, 재진입)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Messages**: 메시지 히스토리 2건 포함
  - `AIMessage`: (tool_calls: get_equipment_detail)
  - `ToolMessage`: {"equipment": [...], "load_history": [24건], "alert_history": [10건]}

> **핵심**: FM이 시계열 부하율 데이터 24건 + 알림 10건을 읽고 종합 분석.

### FM 출력 (<- Gemini) -> 텍스트 응답
```
장비 ID: CVR-L1-CELL-01 상세 정보입니다.

**장비 정보**
| 속성 | 값 |
|---|---|
| 장비 ID | CVR-L1-CELL-01 |
| 유형 | CONVEYOR |
| 라인 | L1 |
| 구간 | CELL |
| 상태 | ERROR |
| 설치일 | 2024-11-21 |

**최근 24시간 부하율 이력**
| 시간 | 부하율 (%) | 처리량 | 큐 길이 |
|---|---|---|---|
| 2026-02-26 22:08:59 | 98.3 | 84 | 17 |
| 2026-02-26 21:58:59 | 96.9 | 97 | 2 |
| 2026-02-26 21:48:59 | 84.6 | 69 | 8 |
| ... | ... | ... | ... |

**최근 알림**
| 시간 | 알림 유형 | 부하율 (%) | 임계값 (%) | 메시지 |
|---|---|---|---|---|
| 2026-02-26 22:08:59 | CRITICAL | 98.3 | 95.0 | 부하율 98.3% — 임계값 95.0% 초과 |
| ... | ... | ... | ... | ... |
```

---

## Step 3: ResponseAgent (응답생성)

최종 응답: InfoAgent 재진입에서 생성된 종합 분석 표 추출.

---

## FM 호출 요약

| 단계 | FM 역할 | 핵심 판단 |
|------|---------|----------|
| IntentAgent | 의도 + ID 파싱 | "CVR-L1-CELL-01" -> `CONVEYOR, L1, CELL` + `keyword: 원인` |
| InfoAgent 1차 | **Tool 선택 판단** | `overload_check`이지만 "원인 분석" -> `get_equipment_detail` 선택 |
| InfoAgent 재진입 | 대량 데이터 종합 | 장비정보 + 부하율 24건 + 알림 10건 -> 마크다운 표 3개 |

**총 FM 호출: 3회**

---

## 학습 포인트

1. **의도 vs Tool 선택 불일치**: `overload_check` 의도인데 `get_overloaded_equipment`가 아닌 `get_equipment_detail`을 FM이 선택. 의도는 분류 기준, Tool 선택은 FM의 맥락 판단.
2. **장비 ID 역파싱**: FM이 `CVR-L1-CELL-01`이라는 ID에서 장비유형-라인-구간 구조를 읽어냄. 프롬프트에 ID 형식 규칙이 없어도 FM이 패턴을 인식.
3. **keyword의 Tool 선택 영향**: `keyword: "원인"`이 FM에게 "단순 목록이 아닌 상세 분석이 필요"라는 신호를 줌.
4. **복합 데이터 분석**: FM이 3개 SQL 결과(장비정보, 부하율 이력, 알림 이력)를 한꺼번에 읽고 구조화된 표 3개로 응답 생성.
