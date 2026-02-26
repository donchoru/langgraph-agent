# Agent Trace Log (멀티턴)
- **시간**: 2026-02-26 21:59:01
- **시나리오**: followup
- **턴 번호**: 3
- **사용자 입력**: CVR-L1-CELL-01 상세 정보 알려줘
- **최종 의도**: equipment_status
- **대화 이력**: 2턴

---
## Step 1: IntentAgent (의도분석)
### State BEFORE
### State Snapshot
- **user_input**: `CVR-L1-CELL-01 상세 정보 알려줘`
- **intent**: ``
- **intent_detail**: ``
- **final_answer**: ``
- **conversation_history** (2턴):
  - Q: `과부하 장비 있어?` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
  - Q: `그 중에서 L1 라인만 보여줘` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
- **messages** (0건):
### LLM 호출
- input: `CVR-L1-CELL-01 상세 정보 알려줘`
### LLM 출력
- intent: `equipment_status`
- detail: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "equipment_id": "CVR-L1-CELL-01", "lot_id": "", "hours": 0, "keyword": "상세 정보"}`
- reasoning: 특정 장비 ID에 대한 상세 정보 요청이므로 장비 상태 조회 의도로 판단함. 이전 대화에서 라인 정보가 주어졌으므로 함께 활용함.
### State AFTER
### State Snapshot
- **user_input**: `CVR-L1-CELL-01 상세 정보 알려줘`
- **intent**: `equipment_status`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "equipment_id": "CVR-L1-CELL-01", "lot_id": "", "hours": 0, "keyword": "상세 정보"}`
- **final_answer**: ``
- **conversation_history** (2턴):
  - Q: `과부하 장비 있어?` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
  - Q: `그 중에서 L1 라인만 보여줘` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
- **messages** (0건):

---
## Step 2: InfoAgent (정보조회)
### State BEFORE
### State Snapshot
- **user_input**: `CVR-L1-CELL-01 상세 정보 알려줘`
- **intent**: `equipment_status`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "equipment_id": "CVR-L1-CELL-01", "lot_id": "", "hours": 0, "keyword": "상세 정보"}`
- **final_answer**: ``
- **conversation_history** (2턴):
  - Q: `과부하 장비 있어?` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
  - Q: `그 중에서 L1 라인만 보여줘` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
- **messages** (0건):
### LLM 호출 (첫 호출)
### LLM 출력 → Tool 호출 요청
- `get_equipment_detail({'equipment_id': 'CVR-L1-CELL-01'})`
### 다음: ToolNode로 이동
### State AFTER
### State Snapshot
- **user_input**: `CVR-L1-CELL-01 상세 정보 알려줘`
- **intent**: `equipment_status`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "equipment_id": "CVR-L1-CELL-01", "lot_id": "", "hours": 0, "keyword": "상세 정보"}`
- **final_answer**: ``
- **conversation_history** (2턴):
  - Q: `과부하 장비 있어?` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
  - Q: `그 중에서 L1 라인만 보여줘` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
- **messages** (1건):
  - **AIMessage** [tool_calls]: `get_equipment_detail({'equipment_id': 'CVR-L1-CELL-01'})`

---
## Step 2.5: ToolNode (SQL 실행)
### State BEFORE
### State Snapshot
- **user_input**: `CVR-L1-CELL-01 상세 정보 알려줘`
- **intent**: `equipment_status`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "equipment_id": "CVR-L1-CELL-01", "lot_id": "", "hours": 0, "keyword": "상세 정보"}`
- **final_answer**: ``
- **conversation_history** (2턴):
  - Q: `과부하 장비 있어?` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
  - Q: `그 중에서 L1 라인만 보여줘` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
- **messages** (1건):
  - **AIMessage** [tool_calls]: `get_equipment_detail({'equipment_id': 'CVR-L1-CELL-01'})`
### 실행할 Tool
- `get_equipment_detail({'equipment_id': 'CVR-L1-CELL-01'})`
### Tool 실행 결과
- **ToolMessage** (tool=`get_equipment_detail`):
  ```
  {"equipment": [{"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "installed_date": "2024-11-21", "description": "CONVEYOR L1-CELL"}], "load_history": [{"recorded_at": "2026-02-26 21:57:54", "load_rate_pct": 98.3, "throughput": 84, "queue_length": 17}, {"recorded_at": "2026-02-26 21:47:54", "load_rate_pct": 96.9, "throughput": 97, "queue_length": 2}, {"recorded_at": "2026-02-26 21:37:54", "load_rate_pct": 84.6, "throughput": 69, "que...
  ```
### State AFTER
### State Snapshot
- **user_input**: `CVR-L1-CELL-01 상세 정보 알려줘`
- **intent**: `equipment_status`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "equipment_id": "CVR-L1-CELL-01", "lot_id": "", "hours": 0, "keyword": "상세 정보"}`
- **final_answer**: ``
- **conversation_history** (2턴):
  - Q: `과부하 장비 있어?` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
  - Q: `그 중에서 L1 라인만 보여줘` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
- **messages** (2건):
  - **AIMessage** [tool_calls]: `get_equipment_detail({'equipment_id': 'CVR-L1-CELL-01'})`
  - **ToolMessage** (tool=`get_equipment_detail`): `{"equipment": [{"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "installed_date": "2024-11-21", "description": "CONVEYOR L1-CELL"}], "load_history": [{"recorded_at": "2026-02-26 21:57:54", "load_rate_pct": 98.3, "throughput": 84, "queu...`

---
## Step 2: InfoAgent 재진입 (Tool 결과 수신)
### State BEFORE
### State Snapshot
- **user_input**: `CVR-L1-CELL-01 상세 정보 알려줘`
- **intent**: `equipment_status`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "equipment_id": "CVR-L1-CELL-01", "lot_id": "", "hours": 0, "keyword": "상세 정보"}`
- **final_answer**: ``
- **conversation_history** (2턴):
  - Q: `과부하 장비 있어?` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
  - Q: `그 중에서 L1 라인만 보여줘` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
- **messages** (2건):
  - **AIMessage** [tool_calls]: `get_equipment_detail({'equipment_id': 'CVR-L1-CELL-01'})`
  - **ToolMessage** (tool=`get_equipment_detail`): `{"equipment": [{"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "installed_date": "2024-11-21", "description": "CONVEYOR L1-CELL"}], "load_history": [{"recorded_at": "2026-02-26 21:57:54", "load_rate_pct": 98.3, "throughput": 84, "queu...`
### LLM 호출 (메시지 히스토리 2건 포함)
### LLM 출력 → 텍스트 응답
```


 장비 ID CVR-L1-CELL-01 상세 정보입니다.
 

 ```
 설비 정보:
 * 장비 ID: CVR-L1-CELL-01
 * 장비 유형: CONVEYOR
 * 라인: L1
 * 구간: CELL
 * 상태: ERROR
 * 설치 일자: 2024-11-21
 * 설명: CONVEYOR L1-CELL
 

 최근 24시간 부하율 이력:
 | 시간 | 부하율(%) | 처리량 | 대기열 길이 |
 |---|---|---|---|
 | 2026-02-26 21:57:54 | 98.3 | 84 | 17 |
 | 2026-02-26 21:47:54 | 96.9 | 97 | 2 |
 | 2026-02-26 21:37:54 | 84.6 | 69 | 8 |
 | 2026-02-26 21:27:54 | 86.3 | 89 | 5 |
 | 2026-02-26 21:17:54 | 99.8 | 102 | 7 |
 | 2026-02-26 21:07:54 | 86.1 | 72 | 4 |
 | 2026
```
### 다음: ResponseAgent로 이동
### State AFTER
### State Snapshot
- **user_input**: `CVR-L1-CELL-01 상세 정보 알려줘`
- **intent**: `equipment_status`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "equipment_id": "CVR-L1-CELL-01", "lot_id": "", "hours": 0, "keyword": "상세 정보"}`
- **final_answer**: ``
- **conversation_history** (2턴):
  - Q: `과부하 장비 있어?` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
  - Q: `그 중에서 L1 라인만 보여줘` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
- **messages** (3건):
  - **AIMessage** [tool_calls]: `get_equipment_detail({'equipment_id': 'CVR-L1-CELL-01'})`
  - **ToolMessage** (tool=`get_equipment_detail`): `{"equipment": [{"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "installed_date": "2024-11-21", "description": "CONVEYOR L1-CELL"}], "load_history": [{"recorded_at": "2026-02-26 21:57:54", "load_rate_pct": 98.3, "throughput": 84, "queu...`
  - **AIMessage**: 

 장비 ID CVR-L1-CELL-01 상세 정보입니다.
 

 ```
 설비 정보:
 * 장비 ID: CVR-L1-CELL-01
 * 장비 유형: CONVEYOR
 * 라인: L1
 * 구간: CELL
 * 상태: ERROR
 * 설치 일자: 2024-11-21
 * 설명: CONVEYOR L1-CELL
 

 최근 24시간 부하율 이력:
 | 시간 | 부하율(%) | 처리량 | 대기열 길이 |
 |---|---|---|---|
 | 2026-02-26 21:57:54 | 98.3 | 84 | 17 |
 | 2026-02-26...

---
## Step 3: ResponseAgent (응답생성)
### State BEFORE
### State Snapshot
- **user_input**: `CVR-L1-CELL-01 상세 정보 알려줘`
- **intent**: `equipment_status`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "equipment_id": "CVR-L1-CELL-01", "lot_id": "", "hours": 0, "keyword": "상세 정보"}`
- **final_answer**: ``
- **conversation_history** (2턴):
  - Q: `과부하 장비 있어?` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
  - Q: `그 중에서 L1 라인만 보여줘` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
- **messages** (3건):
  - **AIMessage** [tool_calls]: `get_equipment_detail({'equipment_id': 'CVR-L1-CELL-01'})`
  - **ToolMessage** (tool=`get_equipment_detail`): `{"equipment": [{"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "installed_date": "2024-11-21", "description": "CONVEYOR L1-CELL"}], "load_history": [{"recorded_at": "2026-02-26 21:57:54", "load_rate_pct": 98.3, "throughput": 84, "queu...`
  - **AIMessage**: 

 장비 ID CVR-L1-CELL-01 상세 정보입니다.
 

 ```
 설비 정보:
 * 장비 ID: CVR-L1-CELL-01
 * 장비 유형: CONVEYOR
 * 라인: L1
 * 구간: CELL
 * 상태: ERROR
 * 설치 일자: 2024-11-21
 * 설명: CONVEYOR L1-CELL
 

 최근 24시간 부하율 이력:
 | 시간 | 부하율(%) | 처리량 | 대기열 길이 |
 |---|---|---|---|
 | 2026-02-26 21:57:54 | 98.3 | 84 | 17 |
 | 2026-02-26...
### 처리: 메시지 히스토리에서 최종 AI 응답 추출
### 최종 응답 (final_answer)
```


 장비 ID CVR-L1-CELL-01 상세 정보입니다.
 

 ```
 설비 정보:
 * 장비 ID: CVR-L1-CELL-01
 * 장비 유형: CONVEYOR
 * 라인: L1
 * 구간: CELL
 * 상태: ERROR
 * 설치 일자: 2024-11-21
 * 설명: CONVEYOR L1-CELL
 

 최근 24시간 부하율 이력:
 | 시간 | 부하율(%) | 처리량 | 대기열 길이 |
 |---|---|---|---|
 | 2026-02-26 21:57:54 | 98.3 | 84 | 17 |
 | 2026-02-26 21:47:54 | 96.9 | 97 | 2 |
 | 2026-02-26 21:37:54 | 84.6 | 69 | 8 |
 | 2026-02-26 21:27:54 | 86.3 | 89 | 5 |
 | 2026-02-26 21:17:54 | 99.8 | 102 | 7 |
 | 2026-02-26 21:07:54 | 86.1 | 72 | 4 |
 | 2026-02-26 20:57:54 | 97.2 | 101 | 11 |
 | 2026-02-26 20:47:54 | 90.2 | 88 | 8 |
 | 2026-02-26 20:37:54 | 93.0 | 87 | 4 |
 | 2026-02-26 20:27:54 | 90.5 | 73 | 0 |
 | 2026-02-26 20:17:54 | 86.1 | 78 | 4 |
 | 2026-02-26 20:07:54 | 88.6 | 71 | 1 |
 | 2026-02-26 19:57:54 | 93.6 | 106 | 11 |
 | 2026-02-26 19:47:54 | 93.3 | 76 | 4 |
 | 2026-02-26 19:37:54 | 90.3 | 88 | 3 |
 | 2026-02-26 19:27:54 | 98.1 | 97 | 1 |
 | 2026-02-26 19:17:54 | 86.5 | 103 | 6 |
 | 2026-02-26 19:07:54 | 98.9 | 107 | 3 |
 | 2026-02-26 18:57:54 | 99.4 | 115 | 16 |
 | 2026-02-26 18:47:54 | 99.1 | 113 | 8 |
 | 2026-02-26 18:37:54 | 91.2 | 78 | 0 |
 | 2026-02-26 18:27:54 | 85.7 | 76 | 1 |
 | 2026-02-26 18:17:54 | 90.4 | 99 | 7 |
 | 2026-02-26 18:07:54 | 89.1 | 106 | 5 |
 

 최근 알림 이력:
 | 발생 시간 | 알림 유형 | 부하율(%) | 임계값(%) | 메시지 |
 |---|---|---|---|---|
 | 2026-02-26 21:57:54 | CRITICAL | 98.3 | 95.0 | CVR-L1-CELL-01 부하율 98.3% — 임계값 95.0% 초과 |
 | 2026-02-26 21:47:54 | CRITICAL | 96.9 | 95.0 | CVR-L1-CELL-01 부하율 96.9% — 임계값 95.0% 초과 |
 | 2026-02-26 21:37:54 | WARNING | 84.6 | 95.0 | CVR-L1-CELL-01 부하율 84.6% — 임계값 95.0% 미만 |
 | 2026-02-26 21:27:54 | WARNING | 86.3 | 95.0 | CVR-L1-CELL-01 부하율 86.3% — 임계값 95.0% 미만 |
 | 2026-02-26 21:17:54 | CRITICAL | 99.8 | 95.0 | CVR-L1-CELL-01 부하율 99.8% — 임계값 95.0% 초과 |
 | 2026-02-26 21:07:54 | WARNING | 86.1 | 95.0 | CVR-L1-CELL-01 부하율 86.1% — 임계값 95.0% 미만 |
 | 2026-02-26 20:57:54 | CRITICAL | 97.2 | 95.0 | CVR-L1-CELL-01 부하율 97.2% — 임계값 95.0% 초과 |
 | 2026-02-26 20:47:54 | WARNING | 90.2 | 95.0 | CVR-L1-CELL-01 부하율 90.2% — 임계값 95.0% 미만 |
 | 2026-02-26 20:37:54 | WARNING | 93.0 | 95.0 | CVR-L1-CELL-01 부하율 93.0% — 임계값 95.0% 미만 |
 | 2026-02-26 20:27:54 | WARNING | 90.5 | 95.0 | CVR-L1-CELL-01 부하율 90.5% — 임계값 95.0% 미만 |
 | 2026-02-26 20:17:54 | WARNING | 86.1 | 95.0 | CVR-L1-CELL-01 부하율 86.1% — 임계값 95.0% 미만 |
 | 2026-02-26 20:07:54 | WARNING | 88.6 | 95.0 | CVR-L1-CELL-01 부하율 88.6% — 임계값 95.0% 미만 |
 | 2026-02-26 19:57:54 | WARNING | 93.6 | 95.0 | CVR-L1-CELL-01 부하율 93.6% — 임계값 95.0% 미만 |
 | 2026-02-26 19:47:54 | WARNING | 93.3 | 95.0 | CVR-L1-CELL-01 부하율 93.3% — 임계값 95.0% 미만 |
 | 2026-02-26 19:37:54 | WARNING | 90.3 | 95.0 | CVR-L1-CELL-01 부하율 90.3% — 임계값 95.0% 미만 |
 | 2026-02-26 19:27:54 | CRITICAL | 98.1 | 95.0 | CVR-L1-CELL-01 부하율 98.1% — 임계값 95.0% 초과 |
 | 2026-02-26 19:17:54 | WARNING | 86.5 | 95.0 | CVR-L1-CELL-01 부하율 86.5% — 임계값 95.0% 미만 |
 | 2026-02-26 19:07:54 | CRITICAL | 98.9 | 95.0 | CVR-L1-CELL-01 부하율 98.9% — 임계값 95.0% 초과 |
 | 2026-02-26 18:57:54 | CRITICAL | 99.4 | 95.0 | CVR-L1-CELL-01 부하율 99.4% — 임계값 95.0% 초과 |
 | 2026-02-26 18:47:54 | CRITICAL | 99.1 | 95.0 | CVR-L1-CELL-01 부하율 99.1% — 임계값 95.0% 초과 |
 | 2026-02-26 18:37:54 | WARNING | 91.2 | 95.0 | CVR-L1-CELL-01 부하율 91.2% — 임계값 95.0% 미만 |
 | 2026-02-26 18:27:54 | WARNING | 85.7 | 95.0 | CVR-L1-CELL-01 부하율 85.7% — 임계값 95.0% 미만 |
 | 2026-02-26 18:17:54 | WARNING | 90.4 | 95.0 | CVR-L1-CELL-01 부하율 90.4% — 임계값 95.0% 미만 |
 | 2026-02-26 18:07:54 | WARNING | 89.1 | 95.0 | CVR-L1-CELL-01 부하율 89.1% — 임계값 95.0% 미만 |
 ```
```
### State AFTER
### State Snapshot
- **user_input**: `CVR-L1-CELL-01 상세 정보 알려줘`
- **intent**: `equipment_status`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "equipment_id": "CVR-L1-CELL-01", "lot_id": "", "hours": 0, "keyword": "상세 정보"}`
- **final_answer**: `

 장비 ID CVR-L1-CELL-01 상세 정보입니다.
 

 ```
 설비 정보:
 * 장비 ID: CVR-L1-CELL-01
 * 장비 유형: CONVEYOR
 * 라인: L1
 * 구간: CELL
 * 상태: ERROR
 * 설치 일자: 2024-11-21
 * 설명: CONVEYOR L1-CELL
 

 최근 24시간 부하율 이력:
 | 시간 `
- **conversation_history** (2턴):
  - Q: `과부하 장비 있어?` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
  - Q: `그 중에서 L1 라인만 보여줘` → A: `🚨 최근 1시간 동안 과부하 상태인 장비 목록입니다.

| 장비 ID        | 유형      | 라인 | 구간   | 상태  | 부하율(...` (overload_check)
- **messages** (3건):
  - **AIMessage** [tool_calls]: `get_equipment_detail({'equipment_id': 'CVR-L1-CELL-01'})`
  - **ToolMessage** (tool=`get_equipment_detail`): `{"equipment": [{"equipment_id": "CVR-L1-CELL-01", "equipment_type": "CONVEYOR", "line": "L1", "zone": "CELL", "status": "ERROR", "installed_date": "2024-11-21", "description": "CONVEYOR L1-CELL"}], "load_history": [{"recorded_at": "2026-02-26 21:57:54", "load_rate_pct": 98.3, "throughput": 84, "queu...`
  - **AIMessage**: 

 장비 ID CVR-L1-CELL-01 상세 정보입니다.
 

 ```
 설비 정보:
 * 장비 ID: CVR-L1-CELL-01
 * 장비 유형: CONVEYOR
 * 라인: L1
 * 구간: CELL
 * 상태: ERROR
 * 설치 일자: 2024-11-21
 * 설명: CONVEYOR L1-CELL
 

 최근 24시간 부하율 이력:
 | 시간 | 부하율(%) | 처리량 | 대기열 길이 |
 |---|---|---|---|
 | 2026-02-26 21:57:54 | 98.3 | 84 | 17 |
 | 2026-02-26...