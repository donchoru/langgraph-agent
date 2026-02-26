# Agent Trace Log
- **시간**: 2026-02-26 14:16:43
- **사용자 입력**: 과부하 장비 있어?
- **최종 의도**: overload_check

---
## Step 1: IntentAgent (의도분석)
### INPUT
```
과부하 장비 있어?
```
### OUTPUT
- intent: `overload_check`
- detail: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- reasoning: 과부하 장비 확인 요청

---
## Step 2: InfoAgent (정보조회)
### INPUT
- intent: `overload_check`
- detail: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
### TOOL CALLS
- `get_overloaded_equipment({})`

---
## Step 2: InfoAgent (정보조회)
### INPUT
- intent: `overload_check`
- detail: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`

---
## Step 3: ResponseAgent (응답생성)
### OUTPUT
```
1시간 이내 과부하 상태인 장비는 없습니다.
```