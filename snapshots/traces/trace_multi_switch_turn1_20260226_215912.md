# Agent Trace Log (멀티턴)
- **시간**: 2026-02-26 21:59:12
- **시나리오**: switch
- **턴 번호**: 1
- **사용자 입력**: CVR-L1-TFT-01에 Lot 뭐 있어?
- **최종 의도**: lot_query
- **대화 이력**: 0턴

---
## Step 1: IntentAgent (의도분석)
### State BEFORE
### State Snapshot
- **user_input**: `CVR-L1-TFT-01에 Lot 뭐 있어?`
- **intent**: ``
- **intent_detail**: ``
- **final_answer**: ``
- **conversation_history** (0턴):
- **messages** (0건):
### LLM 호출
- input: `CVR-L1-TFT-01에 Lot 뭐 있어?`
### LLM 출력
- intent: `lot_query`
- detail: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "equipment_id": "CVR-L1-TFT-01", "lot_id": "", "hours": 0, "keyword": ""}`
- reasoning: 특정 장비에 Lot이 있는지 확인하는 질문이므로 lot_query 의도이며, 장비 ID를 통해 장비 유형, 라인, 구간을 파악할 수 있음
### State AFTER
### State Snapshot
- **user_input**: `CVR-L1-TFT-01에 Lot 뭐 있어?`
- **intent**: `lot_query`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "equipment_id": "CVR-L1-TFT-01", "lot_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **conversation_history** (0턴):
- **messages** (0건):

---
## Step 2: InfoAgent (정보조회)
### State BEFORE
### State Snapshot
- **user_input**: `CVR-L1-TFT-01에 Lot 뭐 있어?`
- **intent**: `lot_query`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "equipment_id": "CVR-L1-TFT-01", "lot_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **conversation_history** (0턴):
- **messages** (0건):
### LLM 호출 (첫 호출)
### LLM 출력 → Tool 호출 요청
- `get_lots_on_equipment({'equipment_id': 'CVR-L1-TFT-01'})`
- `get_lots_scheduled_for_equipment({'equipment_id': 'CVR-L1-TFT-01'})`
### 다음: ToolNode로 이동
### State AFTER
### State Snapshot
- **user_input**: `CVR-L1-TFT-01에 Lot 뭐 있어?`
- **intent**: `lot_query`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "equipment_id": "CVR-L1-TFT-01", "lot_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **conversation_history** (0턴):
- **messages** (1건):
  - **AIMessage** [tool_calls]: `get_lots_on_equipment({'equipment_id': 'CVR-L1-TFT-01'}), get_lots_scheduled_for_equipment({'equipment_id': 'CVR-L1-TFT-01'})`

---
## Step 2.5: ToolNode (SQL 실행)
### State BEFORE
### State Snapshot
- **user_input**: `CVR-L1-TFT-01에 Lot 뭐 있어?`
- **intent**: `lot_query`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "equipment_id": "CVR-L1-TFT-01", "lot_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **conversation_history** (0턴):
- **messages** (1건):
  - **AIMessage** [tool_calls]: `get_lots_on_equipment({'equipment_id': 'CVR-L1-TFT-01'}), get_lots_scheduled_for_equipment({'equipment_id': 'CVR-L1-TFT-01'})`
### 실행할 Tool
- `get_lots_on_equipment({'equipment_id': 'CVR-L1-TFT-01'})`
- `get_lots_scheduled_for_equipment({'equipment_id': 'CVR-L1-TFT-01'})`
### Tool 실행 결과
- **ToolMessage** (tool=`get_lots_on_equipment`):
  ```
  [{"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "created_at": "2026-02-25 23:57:54", "updated_at": "2026-02-26 21:19:54"}, {"lot_id": "LOT-023", "product_type": "OLED_A", "quantity": 289, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "created_at": "2026-02-26 00:57:54", "updated_at": "2026-02-26 21:05:54"}]
  ```
- **ToolMessage** (tool=`get_lots_scheduled_for_equipment`):
  ```
  [{"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "scheduled_equipment_id": "CVR-L1-TFT-01", "scheduled_start": "2026-02-26 20:57:54", "scheduled_end": "2026-02-27 13:57:54", "actual_start": "2026-02-26 21:32:54", "actual_end": null}, {"lot_id": "LOT-023", "product_type": "OLED_A", "quantity": 289, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "scheduled_equipment_id": "CVR-L1-TFT-01", "scheduled_...
  ```
### State AFTER
### State Snapshot
- **user_input**: `CVR-L1-TFT-01에 Lot 뭐 있어?`
- **intent**: `lot_query`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "equipment_id": "CVR-L1-TFT-01", "lot_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **conversation_history** (0턴):
- **messages** (3건):
  - **AIMessage** [tool_calls]: `get_lots_on_equipment({'equipment_id': 'CVR-L1-TFT-01'}), get_lots_scheduled_for_equipment({'equipment_id': 'CVR-L1-TFT-01'})`
  - **ToolMessage** (tool=`get_lots_on_equipment`): `[{"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "created_at": "2026-02-25 23:57:54", "updated_at": "2026-02-26 21:19:54"}, {"lot_id": "LOT-023", "product_type": "OLED_A", "quantity": 289, "status": "IN_PROCESS", "curr...`
  - **ToolMessage** (tool=`get_lots_scheduled_for_equipment`): `[{"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "scheduled_equipment_id": "CVR-L1-TFT-01", "scheduled_start": "2026-02-26 20:57:54", "scheduled_end": "2026-02-27 13:57:54", "actual_start": "2026-02-26 21:32:54", "actu...`

---
## Step 2: InfoAgent 재진입 (Tool 결과 수신)
### State BEFORE
### State Snapshot
- **user_input**: `CVR-L1-TFT-01에 Lot 뭐 있어?`
- **intent**: `lot_query`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "equipment_id": "CVR-L1-TFT-01", "lot_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **conversation_history** (0턴):
- **messages** (3건):
  - **AIMessage** [tool_calls]: `get_lots_on_equipment({'equipment_id': 'CVR-L1-TFT-01'}), get_lots_scheduled_for_equipment({'equipment_id': 'CVR-L1-TFT-01'})`
  - **ToolMessage** (tool=`get_lots_on_equipment`): `[{"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "created_at": "2026-02-25 23:57:54", "updated_at": "2026-02-26 21:19:54"}, {"lot_id": "LOT-023", "product_type": "OLED_A", "quantity": 289, "status": "IN_PROCESS", "curr...`
  - **ToolMessage** (tool=`get_lots_scheduled_for_equipment`): `[{"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "scheduled_equipment_id": "CVR-L1-TFT-01", "scheduled_start": "2026-02-26 20:57:54", "scheduled_end": "2026-02-27 13:57:54", "actual_start": "2026-02-26 21:32:54", "actu...`
### LLM 호출 (메시지 히스토리 3건 포함)
### LLM 출력 → 텍스트 응답
```
📍 CVR-L1-TFT-01 설비에 현재 물리적으로 있는 Lot은 다음과 같습니다:

| Lot ID | 제품 유형 | 수량 | 상태 |
|---|---|---|---|
| LOT-020 | OLED_B | 206 | 가동 중 |
| LOT-023 | OLED_A | 289 | 가동 중 |

📅 CVR-L1-TFT-01 설비에 예정된 Lot은 다음과 같습니다:

| Lot ID | 제품 유형 | 수량 | 스케줄 시작 | 스케줄 종료 | 상태 |
|---|---|---|---|---|---|
| LOT-020 | OLED_B | 206 | 2026-02-26 20:57:54 | 2026-02-27 13:57:54 | 가동 중 |
| LOT-023 | OLED_A | 289 | 2026-02-26 21:57:54 | 2026-02-27 06:57:54 | 가동 중 |
| LOT-005 | LCD_C | 137 | 2026-02-26 22:57:54 | 2026-02-27 02:57:54
```
### 다음: ResponseAgent로 이동
### State AFTER
### State Snapshot
- **user_input**: `CVR-L1-TFT-01에 Lot 뭐 있어?`
- **intent**: `lot_query`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "equipment_id": "CVR-L1-TFT-01", "lot_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **conversation_history** (0턴):
- **messages** (4건):
  - **AIMessage** [tool_calls]: `get_lots_on_equipment({'equipment_id': 'CVR-L1-TFT-01'}), get_lots_scheduled_for_equipment({'equipment_id': 'CVR-L1-TFT-01'})`
  - **ToolMessage** (tool=`get_lots_on_equipment`): `[{"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "created_at": "2026-02-25 23:57:54", "updated_at": "2026-02-26 21:19:54"}, {"lot_id": "LOT-023", "product_type": "OLED_A", "quantity": 289, "status": "IN_PROCESS", "curr...`
  - **ToolMessage** (tool=`get_lots_scheduled_for_equipment`): `[{"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "scheduled_equipment_id": "CVR-L1-TFT-01", "scheduled_start": "2026-02-26 20:57:54", "scheduled_end": "2026-02-27 13:57:54", "actual_start": "2026-02-26 21:32:54", "actu...`
  - **AIMessage**: 📍 CVR-L1-TFT-01 설비에 현재 물리적으로 있는 Lot은 다음과 같습니다:

| Lot ID | 제품 유형 | 수량 | 상태 |
|---|---|---|---|
| LOT-020 | OLED_B | 206 | 가동 중 |
| LOT-023 | OLED_A | 289 | 가동 중 |

📅 CVR-L1-TFT-01 설비에 예정된 Lot은 다음과 같습니다:

| Lot ID | 제품 유형 | 수량 | 스케줄 시작 | 스케줄 종료 | 상태 |
|---|---|---|---|---|---|
| LOT-020 | OLED_B | 20...

---
## Step 3: ResponseAgent (응답생성)
### State BEFORE
### State Snapshot
- **user_input**: `CVR-L1-TFT-01에 Lot 뭐 있어?`
- **intent**: `lot_query`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "equipment_id": "CVR-L1-TFT-01", "lot_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **conversation_history** (0턴):
- **messages** (4건):
  - **AIMessage** [tool_calls]: `get_lots_on_equipment({'equipment_id': 'CVR-L1-TFT-01'}), get_lots_scheduled_for_equipment({'equipment_id': 'CVR-L1-TFT-01'})`
  - **ToolMessage** (tool=`get_lots_on_equipment`): `[{"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "created_at": "2026-02-25 23:57:54", "updated_at": "2026-02-26 21:19:54"}, {"lot_id": "LOT-023", "product_type": "OLED_A", "quantity": 289, "status": "IN_PROCESS", "curr...`
  - **ToolMessage** (tool=`get_lots_scheduled_for_equipment`): `[{"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "scheduled_equipment_id": "CVR-L1-TFT-01", "scheduled_start": "2026-02-26 20:57:54", "scheduled_end": "2026-02-27 13:57:54", "actual_start": "2026-02-26 21:32:54", "actu...`
  - **AIMessage**: 📍 CVR-L1-TFT-01 설비에 현재 물리적으로 있는 Lot은 다음과 같습니다:

| Lot ID | 제품 유형 | 수량 | 상태 |
|---|---|---|---|
| LOT-020 | OLED_B | 206 | 가동 중 |
| LOT-023 | OLED_A | 289 | 가동 중 |

📅 CVR-L1-TFT-01 설비에 예정된 Lot은 다음과 같습니다:

| Lot ID | 제품 유형 | 수량 | 스케줄 시작 | 스케줄 종료 | 상태 |
|---|---|---|---|---|---|
| LOT-020 | OLED_B | 20...
### 처리: 메시지 히스토리에서 최종 AI 응답 추출
### 최종 응답 (final_answer)
```
📍 CVR-L1-TFT-01 설비에 현재 물리적으로 있는 Lot은 다음과 같습니다:

| Lot ID | 제품 유형 | 수량 | 상태 |
|---|---|---|---|
| LOT-020 | OLED_B | 206 | 가동 중 |
| LOT-023 | OLED_A | 289 | 가동 중 |

📅 CVR-L1-TFT-01 설비에 예정된 Lot은 다음과 같습니다:

| Lot ID | 제품 유형 | 수량 | 스케줄 시작 | 스케줄 종료 | 상태 |
|---|---|---|---|---|---|
| LOT-020 | OLED_B | 206 | 2026-02-26 20:57:54 | 2026-02-27 13:57:54 | 가동 중 |
| LOT-023 | OLED_A | 289 | 2026-02-26 21:57:54 | 2026-02-27 06:57:54 | 가동 중 |
| LOT-005 | LCD_C | 137 | 2026-02-26 22:57:54 | 2026-02-27 02:57:54 | ⚡ 이동 중 |
| LOT-018 | OLED_B | 289 | 2026-02-26 23:57:54 | 2026-02-27 12:57:54 | SCHEDULED |
| LOT-029 | LCD_C | 349 | 2026-02-27 03:57:54 | 2026-02-27 10:57:54 | ⚡ 이동 중 |
| LOT-009 | OLED_B | 196 | 2026-02-27 05:57:54 | 2026-02-27 12:57:54 | SCHEDULED |

⚡ '이동 중' 상태는 Lot의 현재 위치와 스케줄된 설비가 달라 Lot이 이동 중임을 의미합니다.
```
### State AFTER
### State Snapshot
- **user_input**: `CVR-L1-TFT-01에 Lot 뭐 있어?`
- **intent**: `lot_query`
- **intent_detail**: `{"equipment_type": "CONVEYOR", "line": "L1", "zone": "TFT", "equipment_id": "CVR-L1-TFT-01", "lot_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: `📍 CVR-L1-TFT-01 설비에 현재 물리적으로 있는 Lot은 다음과 같습니다:

| Lot ID | 제품 유형 | 수량 | 상태 |
|---|---|---|---|
| LOT-020 | OLED_B | 206 | 가동 중 |
| LOT-023 | OLED_A | 289 | 가동 중 |

📅 CVR-L1-TFT-01 설비에 예정된 Lot은 다음과 같습니`
- **conversation_history** (0턴):
- **messages** (4건):
  - **AIMessage** [tool_calls]: `get_lots_on_equipment({'equipment_id': 'CVR-L1-TFT-01'}), get_lots_scheduled_for_equipment({'equipment_id': 'CVR-L1-TFT-01'})`
  - **ToolMessage** (tool=`get_lots_on_equipment`): `[{"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "created_at": "2026-02-25 23:57:54", "updated_at": "2026-02-26 21:19:54"}, {"lot_id": "LOT-023", "product_type": "OLED_A", "quantity": 289, "status": "IN_PROCESS", "curr...`
  - **ToolMessage** (tool=`get_lots_scheduled_for_equipment`): `[{"lot_id": "LOT-020", "product_type": "OLED_B", "quantity": 206, "status": "IN_PROCESS", "current_equipment_id": "CVR-L1-TFT-01", "scheduled_equipment_id": "CVR-L1-TFT-01", "scheduled_start": "2026-02-26 20:57:54", "scheduled_end": "2026-02-27 13:57:54", "actual_start": "2026-02-26 21:32:54", "actu...`
  - **AIMessage**: 📍 CVR-L1-TFT-01 설비에 현재 물리적으로 있는 Lot은 다음과 같습니다:

| Lot ID | 제품 유형 | 수량 | 상태 |
|---|---|---|---|
| LOT-020 | OLED_B | 206 | 가동 중 |
| LOT-023 | OLED_A | 289 | 가동 중 |

📅 CVR-L1-TFT-01 설비에 예정된 Lot은 다음과 같습니다:

| Lot ID | 제품 유형 | 수량 | 스케줄 시작 | 스케줄 종료 | 상태 |
|---|---|---|---|---|---|
| LOT-020 | OLED_B | 20...