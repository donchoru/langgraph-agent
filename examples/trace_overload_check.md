# 예시 1: 과부하 장비 조회 (overload_check)

> **학습 목표**: 가장 대표적인 Tool 호출 플로우. 의도분석 → Tool 선택 → SQL 실행 → 결과 정리까지 전 과정을 추적한다.

---

## 사용자 입력

```
과부하 장비 있어?
```

## 에이전트 처리 흐름

```
사용자: "과부하 장비 있어?"
  │
  ▼
[Step 1] IntentAgent ─── Gemini LLM 호출
  │  intent: "overload_check"
  │  detail: {"equipment_type":"","line":"","zone":"","equipment_id":"","hours":0,"keyword":""}
  │  reasoning: "과부하 장비 확인 요청"
  │
  ▼  intent ≠ "general_chat" → InfoAgent로 라우팅
[Step 2] InfoAgent ─── Tool 바인딩된 Gemini LLM 호출
  │  LLM 판단: overload_check → get_overloaded_equipment 호출
  │  tool_calls: [get_overloaded_equipment({})]
  │
  ▼  tool_calls 존재 → ToolNode로
[Step 2.5] ToolNode ─── SQL 실행
  │  get_overloaded_equipment({})
  │  → 3-way JOIN: load_rate + equipment + alert_threshold
  │  → 결과: 과부하 장비 데이터 JSON 반환
  │
  ▼  ToolNode → InfoAgent 재진입
[Step 2 재진입] InfoAgent ─── Tool 결과 포함 LLM 호출
  │  messages: [AIMessage(tool_calls), ToolMessage(결과)]
  │  LLM이 JSON 데이터를 마크다운 표로 정리
  │  tool_calls 없음 → 텍스트 응답
  │
  ▼  tool_calls 없음 → ResponseAgent로
[Step 3] ResponseAgent
  │  messages에서 마지막 AIMessage 텍스트 추출
  │  → final_answer에 설정
  │
  ▼
사용자에게 응답 출력 + traces/ 에 트레이스 파일 저장
```

---

## 핵심 설계 포인트

### 1. IntentAgent의 파라미터 추출

```json
{
  "intent": "overload_check",
  "detail": {
    "equipment_type": "",  // 특정 유형 지정 안 함 → 전체 장비 대상
    "line": "",            // 라인 필터 없음
    "zone": "",
    "equipment_id": "",
    "hours": 0,
    "keyword": ""
  },
  "reasoning": "과부하 장비 확인 요청"
}
```

**포인트**: `detail`의 모든 필드가 비어있다 = "전체 장비에서 과부하인 것을 찾아라"는 의미.
만약 `"L1 컨베이어 과부하 있어?"`라면 `equipment_type: "CONVEYOR"`, `line: "L1"`이 채워진다.

### 2. InfoAgent의 Tool 선택 과정

시스템 프롬프트(`INFO_SYSTEM_PROMPT`)에 도구 선택 가이드가 명시되어 있음:

```
overload_check 의도 → get_overloaded_equipment
```

LLM은 이 가이드를 따라 `get_overloaded_equipment({})`를 호출.
파라미터 없음 = 장비 유형별 기본 임계값(`alert_threshold` 테이블) 기준으로 조회.

### 3. 실행된 SQL (get_overloaded_equipment 내부)

```sql
SELECT e.equipment_id, e.equipment_type, e.line, e.zone, e.status,
       lr.recorded_at, lr.load_rate_pct, at.warning_pct, at.critical_pct
FROM load_rate lr
JOIN equipment e ON lr.equipment_id = e.equipment_id
JOIN alert_threshold at ON e.equipment_type = at.equipment_type
WHERE lr.load_rate_pct >= at.warning_pct
  AND lr.recorded_at >= datetime('now', 'localtime', '-1 hours')
ORDER BY lr.load_rate_pct DESC
```

**3-way JOIN의 의미**:
- `load_rate`: 실시간 부하율 데이터
- `equipment`: 장비 메타정보 (유형, 라인, 구간, 상태)
- `alert_threshold`: 장비 유형별 경고/임계 기준값

**핵심**: `threshold_pct` 파라미터가 없으면 장비 유형별로 다른 임계값이 적용됨.
CONVEYOR는 80%, AGV는 75%, CRANE은 70% 등 — 장비 특성에 맞는 기준.

### 4. ToolNode → InfoAgent 재진입 (Tool 루프)

```
messages 히스토리:
  [0] AIMessage(tool_calls=[get_overloaded_equipment({})])   ← 1차 호출
  [1] ToolMessage(content="[{과부하장비JSON}]")              ← SQL 결과
  [2] AIMessage(content="과부하 장비 목록입니다.\n| ...")     ← 2차 호출 (정리)
```

LangGraph의 조건부 엣지(`should_continue`)가 `tool_calls` 존재 여부로 분기:
- `tool_calls` 있음 → ToolNode → InfoAgent 재진입 (루프)
- `tool_calls` 없음 → ResponseAgent (탈출)

이 패턴 덕분에 InfoAgent가 **여러 Tool을 연쇄 호출**할 수도 있다.

### 5. ResponseAgent의 역할

InfoAgent가 이미 텍스트 응답을 생성했는데 ResponseAgent가 왜 필요한가?

- **일반 대화 경로 처리**: `general_chat`은 InfoAgent를 거치지 않고 바로 ResponseAgent로 감
- **응답 추출 통일**: 어떤 경로든 `final_answer` 필드에 최종 응답을 설정하는 단일 지점
- **트레이스 기록**: 최종 응답 내용을 trace_log에 기록

---

## Tool 결과 데이터 (상위 10건)

```json
[
  {"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "load_rate_pct": 99.8, "warning_pct": 80.0, "critical_pct": 95.0},
  {"equipment_id": "SHT-L3-CELL-01", "equipment_type": "SHUTTLE", "line": "L3", "zone": "CELL", "status": "ERROR", "load_rate_pct": 99.3, "warning_pct": 78.0, "critical_pct": 92.0},
  {"equipment_id": "SHT-L3-MODULE-01", "equipment_type": "SHUTTLE", "line": "L3", "zone": "MODULE", "status": "ERROR", "load_rate_pct": 99.2, "warning_pct": 78.0, "critical_pct": 92.0},
  {"equipment_id": "AGV-L1-CELL-01", "equipment_type": "AGV", "line": "L1", "zone": "CELL", "status": "ERROR", "load_rate_pct": 99.1, "warning_pct": 75.0, "critical_pct": 90.0},
  {"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "load_rate_pct": 98.3, "warning_pct": 80.0, "critical_pct": 95.0},
  {"equipment_id": "SHT-L3-CELL-01", "equipment_type": "SHUTTLE", "line": "L3", "zone": "CELL", "status": "ERROR", "load_rate_pct": 98.1, "warning_pct": 78.0, "critical_pct": 92.0},
  {"equipment_id": "SHT-L1-TFT-01", "equipment_type": "SHUTTLE", "line": "L1", "zone": "TFT", "status": "ERROR", "load_rate_pct": 95.6, "warning_pct": 78.0, "critical_pct": 92.0},
  {"equipment_id": "CRN-L1-MODULE-01", "equipment_type": "CRANE", "line": "L1", "zone": "MODULE", "status": "ERROR", "load_rate_pct": 95.6, "warning_pct": 70.0, "critical_pct": 85.0},
  {"equipment_id": "SHT-L1-TFT-02", "equipment_type": "SHUTTLE", "line": "L1", "zone": "TFT", "status": "ERROR", "load_rate_pct": 95.3, "warning_pct": 78.0, "critical_pct": 92.0},
  {"equipment_id": "SHT-L3-MODULE-01", "equipment_type": "SHUTTLE", "line": "L3", "zone": "MODULE", "status": "ERROR", "load_rate_pct": 94.8, "warning_pct": 78.0, "critical_pct": 92.0}
]
```

## 최종 응답 (final_answer)

```
1시간 내 과부하 상태인 장비 목록입니다.

| 장비 ID          | 유형     | 라인 | 구간   | 부하율(%) | 상태  |
| :--------------- | :------- | :--- | :----- | :-------- | :---- |
| CVR-L1-CELL-01   | CONVEYOR | L1   | CELL   | 99.8      | ERROR |
| SHT-L3-CELL-01   | SHUTTLE  | L3   | CELL   | 99.3      | ERROR |
| SHT-L3-MODULE-01 | SHUTTLE  | L3   | MODULE | 99.2      | ERROR |
| AGV-L1-CELL-01   | AGV      | L1   | CELL   | 99.1      | ERROR |
| ...              |          |      |        |           |       |
```

---

## State 변화 요약

| 단계 | intent | messages | final_answer |
|------|--------|----------|--------------|
| 초기 | `""` | `[]` | `""` |
| IntentAgent 후 | `"overload_check"` | `[]` | `""` |
| InfoAgent 1차 후 | `"overload_check"` | `[AIMessage(tool_calls)]` | `""` |
| ToolNode 후 | `"overload_check"` | `[AIMessage, ToolMessage]` | `""` |
| InfoAgent 2차 후 | `"overload_check"` | `[AIMessage, ToolMessage, AIMessage]` | `""` |
| ResponseAgent 후 | `"overload_check"` | `[AIMessage, ToolMessage, AIMessage]` | `"1시간 내 과부하..."` |

---

## 학습 포인트

1. **Tool 루프 패턴**: InfoAgent ↔ ToolNode 사이의 조건부 루프가 이 시스템의 핵심. `tool_calls` 유무로 루프 탈출 판단.
2. **3-way JOIN**: 단순 부하율뿐 아니라 장비 유형별 차등 임계값을 적용하는 설계. 하드코딩 대신 `alert_threshold` 테이블로 유연하게 관리.
3. **LLM의 이중 역할**: 같은 InfoAgent LLM이 1차에서는 "어떤 Tool을 호출할지" 판단하고, 2차에서는 "Tool 결과를 사람이 읽기 쉽게 정리"하는 역할을 함.
4. **파라미터 전파**: IntentAgent가 추출한 `detail` → InfoAgent의 시스템 프롬프트에 포함 → LLM이 Tool 호출 시 적절한 파라미터 선택.
