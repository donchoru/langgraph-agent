# 예시 4: 알림 이력 조회 (alert_check)

> **학습 목표**: 대량 데이터 반환 시 LLM이 어떻게 응답을 **정리하고 필터링**하는지를 추적한다. 250건의 알림 데이터를 사람이 읽을 수 있는 형태로 변환하는 과정.

---

## 사용자 입력

```
최근 알림 이력 보여줘
```

## 에이전트 처리 흐름

```
사용자: "최근 알림 이력 보여줘"
  │
  ▼
[Step 1] IntentAgent
  │  intent: "alert_check"
  │  detail: {"hours":0, ...}  ← 시간 미지정 → Tool 기본값 24시간 적용
  │
  ▼
[Step 2] InfoAgent (1차)
  │  tool_calls: [get_recent_alerts({})]
  │  ← 파라미터 없음 = 기본 24시간, 전체 유형
  │
  ▼
[Step 2.5] ToolNode
  │  SQL: alert_history JOIN equipment, 24시간 이내, triggered_at DESC
  │  → 결과: ~250건의 알림 데이터 (WARNING + CRITICAL 혼합)
  │
  ▼
[Step 2 재진입] InfoAgent (2차)
  │  250건 전체를 LLM에 전달
  │  LLM이 중요도 순으로 정렬하여 주요 알림만 표로 정리
  │  (전체를 다 보여주면 사용자가 읽을 수 없으므로)
  │
  ▼
[Step 3] ResponseAgent → final_answer 설정
```

---

## 핵심 설계 포인트

### 1. 파라미터 기본값 전략

사용자가 "최근"이라고만 했을 때:

```json
{
  "intent": "alert_check",
  "detail": {
    "equipment_type": "",
    "line": "",
    "zone": "",
    "equipment_id": "",
    "hours": 0,        // 미지정
    "keyword": ""
  }
}
```

`hours: 0` → `get_recent_alerts`의 기본값 24시간 적용:
```python
@tool
def get_recent_alerts(hours: int = 24, alert_type: Optional[str] = None) -> str:
```

**설계 원칙**: Tool 함수에서 합리적인 기본값을 설정해두면, IntentAgent가 명시적으로 추출하지 못한 파라미터도 자연스럽게 처리됨.

### 2. 대량 데이터 처리 — LLM의 요약 능력

Tool 결과: **~250건**의 alert_history 행
LLM 응답: **상위 ~60건**을 시간순 테이블로 정리

```
250건 JSON → LLM 컨텍스트에 전달 → LLM이 판단하여 정리
```

**과제**: Gemini의 컨텍스트 윈도우에 250건 JSON이 다 들어가지만, 응답에 전부 넣으면 사용자 경험이 나빠짐.
**LLM의 판단**: 최근 시간 순으로 정렬하고, CRITICAL을 우선 배치.

### 3. 실행된 SQL (get_recent_alerts 내부)

```sql
SELECT ah.*, e.equipment_type, e.line, e.zone
FROM alert_history ah
JOIN equipment e ON ah.equipment_id = e.equipment_id
WHERE triggered_at >= datetime('now', 'localtime', '-24 hours')
ORDER BY triggered_at DESC
```

**JOIN의 의미**: `alert_history`에는 `equipment_id`만 있고 장비 유형/라인/구간 정보가 없음.
`equipment` 테이블과 JOIN하여 사용자에게 의미 있는 컨텍스트(유형, 라인, 구간) 추가.

### 4. get_recent_alerts의 선택적 필터링

```python
@tool
def get_recent_alerts(hours: int = 24, alert_type: Optional[str] = None) -> str:
```

| 호출 예시 | 결과 |
|-----------|------|
| `get_recent_alerts({})` | 24시간, 전체 유형 |
| `get_recent_alerts({"hours": 6})` | 6시간, 전체 유형 |
| `get_recent_alerts({"alert_type": "CRITICAL"})` | 24시간, CRITICAL만 |
| `get_recent_alerts({"hours": 1, "alert_type": "WARNING"})` | 1시간, WARNING만 |

사용자가 "CRITICAL 알림만 보여줘"라고 하면 IntentAgent가 `keyword: "CRITICAL"`을 추출하고,
InfoAgent LLM이 `alert_type: "CRITICAL"` 파라미터를 전달.

---

## Tool 결과 데이터 (상위 5건)

```json
[
  {"id": 1250, "equipment_id": "SHT-L3-TFT-02", "alert_type": "WARNING", "load_rate_pct": 90.1, "threshold_pct": 78.0, "triggered_at": "2026-02-26 14:57:01", "resolved_at": null, "message": "SHT-L3-TFT-02 부하율 90.1% — 경고 78.0% 초과", "equipment_type": "SHUTTLE", "line": "L3", "zone": "TFT"},
  {"id": 1226, "equipment_id": "CVR-L1-CELL-01", "alert_type": "CRITICAL", "load_rate_pct": 98.3, "threshold_pct": 95.0, "triggered_at": "2026-02-26 14:57:01", "resolved_at": null, "message": "CVR-L1-CELL-01 부하율 98.3% — 임계값 95.0% 초과", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL"},
  {"id": 1194, "equipment_id": "SHT-L3-MODULE-01", "alert_type": "WARNING", "load_rate_pct": 91.2, "threshold_pct": 78.0, "triggered_at": "2026-02-26 14:57:01", "resolved_at": null, "message": "SHT-L3-MODULE-01 부하율 91.2% — 경고 78.0% 초과", "equipment_type": "SHUTTLE", "line": "L3", "zone": "MODULE"},
  {"id": 1165, "equipment_id": "SHT-L3-CELL-01", "alert_type": "CRITICAL", "load_rate_pct": 98.1, "threshold_pct": 92.0, "triggered_at": "2026-02-26 14:57:01", "resolved_at": null, "message": "SHT-L3-CELL-01 부하율 98.1% — 임계값 92.0% 초과", "equipment_type": "SHUTTLE", "line": "L3", "zone": "CELL"},
  {"id": 1139, "equipment_id": "CRN-L1-MODULE-01", "alert_type": "CRITICAL", "load_rate_pct": 88.8, "threshold_pct": 85.0, "triggered_at": "2026-02-26 14:57:01", "resolved_at": null, "message": "CRN-L1-MODULE-01 부하율 88.8% — 임계값 85.0% 초과", "equipment_type": "CRANE", "line": "L1", "zone": "MODULE"}
]
```

**데이터 구조 포인트**:
- `resolved_at: null` — 아직 해소되지 않은 알림
- `threshold_pct`: 장비 유형별로 다름 (SHUTTLE 78%, CONVEYOR 95%, CRANE 85%)
- `message`: seed 시점에 자동 생성된 알림 메시지

## 최종 응답 (final_answer, 일부)

```
24시간 동안 발생한 알림 이력입니다.

| ID   | 장비 ID          | 장비 유형 | 라인 | 구간   | 부하율(%) | 임계값(%) | 알림 유형 | 발생 시각           |
| :--- | :--------------- | :-------- | :--- | :----- | :-------- | :-------- | :-------- | :------------------ |
| 1250 | SHT-L3-TFT-02   | SHUTTLE   | L3   | TFT    | 90.1      | 78        | WARNING   | 2026-02-26 14:57:01 |
| 1226 | CVR-L1-CELL-01   | CONVEYOR  | L1   | CELL   | 98.3      | 95        | CRITICAL  | 2026-02-26 14:57:01 |
| 1194 | SHT-L3-MODULE-01 | SHUTTLE   | L3   | MODULE | 91.2      | 78        | WARNING   | 2026-02-26 14:57:01 |
| 1165 | SHT-L3-CELL-01   | SHUTTLE   | L3   | CELL   | 98.1      | 92        | CRITICAL  | 2026-02-26 14:57:01 |
| ...  |                  |           |      |        |           |           |           |                     |
```

---

## 알림 시스템 구조

```
[Seed 시점]                      [조회 시점]
 load_rate 데이터 생성              get_recent_alerts()
 → rate >= critical_pct?           → alert_history JOIN equipment
   → alert_history에 CRITICAL 삽입  → 시간순 정렬 반환
 → rate >= warning_pct?
   → alert_history에 WARNING 삽입

alert_threshold 테이블:
 CONVEYOR: warning 80%, critical 95%
 AGV:      warning 75%, critical 90%
 CRANE:    warning 70%, critical 85%
 SORTER:   warning 80%, critical 95%
 STACKER:  warning 75%, critical 90%
 SHUTTLE:  warning 78%, critical 92%
```

---

## 학습 포인트

1. **기본값 설계**: `hours=24`처럼 합리적 기본값이 있으면 사용자가 "최근 알림"이라고만 해도 의미 있는 결과 반환. 모든 파라미터를 사용자가 명시할 필요 없음.
2. **대량 결과 처리**: 250건의 알림을 LLM이 자동으로 정리. Token 비용은 들지만, 사용자에게 의미 있는 형태로 변환하는 것이 LLM의 핵심 가치.
3. **알림 데이터의 이중 기준**: `warning_pct`와 `critical_pct`로 2단계 임계값. 장비 유형별로 다른 기준이 적용되므로 단일 임계값보다 현실적인 운영 가능.
4. **resolved_at 필드**: 알림 해소 추적을 위한 필드. 현재 seed 데이터에서는 모두 null이지만, 실제 시스템에서는 알림 해소 시 timestamp 기록 → "미해결 알림만 조회" 가능.
