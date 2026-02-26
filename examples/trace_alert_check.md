# 예시 4: 알림 이력 조회 — 대량 데이터 처리 패턴

> **학습 목표**: 대량의 알림 데이터(20건)가 Tool에서 반환되었을 때 FM이 이를 정리된 표 형식으로 변환하는 과정.
> FM의 입력 토큰이 많아지는 "재진입" 단계의 I/O를 추적한다.

---

## 입력

```
최근 알림 이력 보여줘
```

---

## Step 1: IntentAgent (의도분석)

### FM 입력 (-> Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙, 984자)
- **Human**:
```
최근 알림 이력 보여줘
```

### FM 출력 (<- Gemini)
```json
{
  "intent": "alert_check",
  "detail": {
    "equipment_type": "",
    "line": "",
    "zone": "",
    "equipment_id": "",
    "lot_id": "",
    "hours": 0,
    "keyword": ""
  },
  "reasoning": "최근 알림 이력 확인 요청은 alert_check에 해당함"
}
```

### 파싱 결과
- intent: `alert_check`
- detail: 필터 없음 (전체 알림 조회)

---

## Step 2: InfoAgent (정보조회, 첫 호출)

### FM 입력 (-> Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Human**:
```
사용자 질문: 최근 알림 이력 보여줘
의도: alert_check
상세: {"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "lot_id": "", "hours": 0, "keyword": ""}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

### FM 출력 (<- Gemini) -> Tool 호출 요청
- `get_recent_alerts({})`

> **포인트**: 도구 선택 가이드 "alert_check 의도 -> get_recent_alerts" 규칙 적용. 단일 Tool 호출.

---

## Step 2.5: ToolNode (SQL 실행)

```sql
SELECT ah.id, ah.equipment_id, ah.alert_type, ah.load_rate_pct,
       ah.threshold_pct, ah.triggered_at, ah.resolved_at, ah.message,
       e.equipment_type, e.line, e.zone
FROM alert_history ah
JOIN equipment e ON ah.equipment_id = e.equipment_id
ORDER BY ah.triggered_at DESC
LIMIT 20
```

### Tool 결과 (20건 -- 발췌)
```json
[
  {"id": 2500, "equipment_id": "SHT-L3-TFT-02", "alert_type": "WARNING",
   "load_rate_pct": 90.1, "threshold_pct": 78.0,
   "triggered_at": "2026-02-26 22:08:59", "resolved_at": null,
   "message": "SHT-L3-TFT-02 부하율 90.1% — 경고 78.0% 초과"},
  {"id": 2476, "equipment_id": "CVR-L1-CELL-01", "alert_type": "CRITICAL",
   "load_rate_pct": 98.3, "threshold_pct": 95.0, ...},
  ...
]
```

> **포인트**: 20건의 JSON 배열이 ToolMessage로 반환됨.
> 이 대량 데이터가 InfoAgent 재진입 시 FM의 입력으로 들어감 -> 토큰 소비 증가.

---

## Step 2 재진입: InfoAgent (Tool 결과 수신)

### FM 입력 (-> Gemini gemini-2.0-flash, 재진입)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 모호성 해소 규칙, 1781자)
- **Messages**: 메시지 히스토리 2건 포함
  - `AIMessage`: (tool_calls: get_recent_alerts)
  - `ToolMessage`: [{"id": 2500, "equipment_id": "SHT-L3-TFT-02", ...}, ...] (20건, 약 4000자)

> **핵심**: FM이 20건의 알림 JSON을 한꺼번에 입력받음. 이것이 "대량 데이터 처리" 패턴.

### FM 출력 (<- Gemini) -> 텍스트 응답 (마크다운 표)
```
최근 24시간 알림 이력입니다.

| ID   | 설비 ID          | 유형     | 라인 | 구간   | 부하율(%) | 임계값(%) | 발생 시각            | 메세지                                     |
|------|------------------|----------|------|--------|-----------|-----------|----------------------|--------------------------------------------|
| 2500 | SHT-L3-TFT-02   | SHUTTLE  | L3   | TFT    | 90.1      | 78.0      | 2026-02-26 22:08:59  | 부하율 90.1% — 경고 78.0% 초과             |
| 2476 | CVR-L1-CELL-01   | CONVEYOR | L1   | CELL   | 98.3      | 95.0      | 2026-02-26 22:08:59  | 부하율 98.3% — 임계값 95.0% 초과           |
| 2444 | SHT-L3-MODULE-01 | SHUTTLE  | L3   | MODULE | 91.2      | 78.0      | 2026-02-26 22:08:59  | 부하율 91.2% — 경고 78.0% 초과             |
| ...  | ...              | ...      | ...  | ...    | ...       | ...       | ...                  | ...                                        |
```

> **포인트**: FM이 20건의 JSON -> 마크다운 표 변환을 수행.
> 시스템 프롬프트의 "표 형식 사용 권장" + "이상 수치 강조" 규칙 적용.

---

## Step 3: ResponseAgent (응답생성)

최종 응답: InfoAgent 재진입에서 생성된 마크다운 표 그대로 추출.

---

## FM 호출 요약

| 단계 | FM 역할 | 입력 크기 | 출력 |
|------|---------|-----------|------|
| IntentAgent | 의도 분류 | ~1000자 | JSON: `alert_check` |
| InfoAgent 1차 | Tool 선택 | ~2000자 | tool_call: `get_recent_alerts` |
| InfoAgent 재진입 | **대량 데이터 -> 표 변환** | **~6000자** (Tool 결과 포함) | 마크다운 표 |

**총 FM 호출: 3회** — 재진입 시 입력 토큰이 가장 많음

---

## 학습 포인트

1. **대량 데이터의 FM 변환**: 20건의 JSON 배열을 FM이 읽기 쉬운 마크다운 표로 변환. 이는 단순 포맷팅이 아니라 필드 선택, 정렬, 한국어 라벨링까지 포함.
2. **재진입 시 토큰 폭발**: Tool 결과가 클수록 재진입 시 FM 입력 토큰이 증가. `message_trimmer`가 이를 관리 (ToolMessage 단위 트리밍).
3. **시스템 프롬프트 규칙 적용**: "표 형식 사용", "수치는 소수점 1자리", "이상 수치 강조" 등의 규칙이 FM 출력 품질을 좌우.
