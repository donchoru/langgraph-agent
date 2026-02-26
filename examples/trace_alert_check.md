# Agent Trace Log
- **시간**: 2026-02-26 14:58:26
- **사용자 입력**: 최근 알림 이력 보여줘
- **최종 의도**: alert_check

---
## Step 1: IntentAgent (의도분석)
### State BEFORE
### State Snapshot
- **user_input**: `최근 알림 이력 보여줘`
- **intent**: ``
- **intent_detail**: ``
- **final_answer**: ``
- **messages** (0건):
### LLM 호출
- input: `최근 알림 이력 보여줘`
### LLM 출력
- intent: `alert_check`
- detail: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- reasoning: 알림 이력 확인 요청이므로 alert_check 의도로 분류함
### State AFTER
### State Snapshot
- **user_input**: `최근 알림 이력 보여줘`
- **intent**: `alert_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (0건):

---
## Step 2: InfoAgent (정보조회)
### State BEFORE
### State Snapshot
- **user_input**: `최근 알림 이력 보여줘`
- **intent**: `alert_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (0건):
### LLM 호출 (첫 호출)
### LLM 출력 → Tool 호출 요청
- `get_recent_alerts({})`
### 다음: ToolNode로 이동
### State AFTER
### State Snapshot
- **user_input**: `최근 알림 이력 보여줘`
- **intent**: `alert_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (1건):
  - **AIMessage** [tool_calls]: `get_recent_alerts({})`

---
## Step 2.5: ToolNode (SQL 실행)
### State BEFORE
### State Snapshot
- **user_input**: `최근 알림 이력 보여줘`
- **intent**: `alert_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (1건):
  - **AIMessage** [tool_calls]: `get_recent_alerts({})`
### 실행할 Tool
- `get_recent_alerts({})`
### Tool 실행 결과
- **ToolMessage** (tool=`get_recent_alerts`):
  ```
  [{"id": 1250, "equipment_id": "SHT-L3-TFT-02", "alert_type": "WARNING", "load_rate_pct": 90.1, "threshold_pct": 78.0, "triggered_at": "2026-02-26 14:57:01", "resolved_at": null, "message": "SHT-L3-TFT-02 부하율 90.1% — 경고 78.0% 초과", "equipment_type": "SHUTTLE", "line": "L3", "zone": "TFT"}, {"id": 1226, "equipment_id": "CVR-L1-CELL-01", "alert_type": "CRITICAL", "load_rate_pct": 98.3, "threshold_pct": 95.0, "triggered_at": "2026-02-26 14:57:01", "resolved_at": null, "message": "CVR-L1-CELL-01 부하율 9...
  ```
### State AFTER
### State Snapshot
- **user_input**: `최근 알림 이력 보여줘`
- **intent**: `alert_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (2건):
  - **AIMessage** [tool_calls]: `get_recent_alerts({})`
  - **ToolMessage** (tool=`get_recent_alerts`): `[{"id": 1250, "equipment_id": "SHT-L3-TFT-02", "alert_type": "WARNING", "load_rate_pct": 90.1, "threshold_pct": 78.0, "triggered_at": "2026-02-26 14:57:01", "resolved_at": null, "message": "SHT-L3-TFT-02 부하율 90.1% — 경고 78.0% 초과", "equipment_type": "SHUTTLE", "line": "L3", "zone": "TFT"}, {"id": 1226...`

---
## Step 2: InfoAgent 재진입 (Tool 결과 수신)
### State BEFORE
### State Snapshot
- **user_input**: `최근 알림 이력 보여줘`
- **intent**: `alert_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (2건):
  - **AIMessage** [tool_calls]: `get_recent_alerts({})`
  - **ToolMessage** (tool=`get_recent_alerts`): `[{"id": 1250, "equipment_id": "SHT-L3-TFT-02", "alert_type": "WARNING", "load_rate_pct": 90.1, "threshold_pct": 78.0, "triggered_at": "2026-02-26 14:57:01", "resolved_at": null, "message": "SHT-L3-TFT-02 부하율 90.1% — 경고 78.0% 초과", "equipment_type": "SHUTTLE", "line": "L3", "zone": "TFT"}, {"id": 1226...`
### LLM 호출 (메시지 히스토리 2건 포함)
### LLM 출력 → 텍스트 응답
```
24시간 동안 발생한 알림 이력입니다.

| ID   | 장비 ID        | 장비 유형   | 라인   | 구간     | 부하율(%) | 임계값(%) | 알림 유형   | 발생 시각            | 메시지                               |
| :----- | :------------- | :---------- | :----- | :------- | :------- | :------- | :---------- | :------------------- | :----------------------------------- |
| 1250 | SHT-L3-TFT-02  | SHUTTLE     | L3     | TFT      | 90.1     | 78       | WARNING     | 2026-02-26 14:57:01 | SHT-L3-TFT-02 부하율 90.1% — 경고 78.0% 초과 |
| 1226 | CVR-L1-CELL-01 | 
```
### 다음: ResponseAgent로 이동
### State AFTER
### State Snapshot
- **user_input**: `최근 알림 이력 보여줘`
- **intent**: `alert_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (3건):
  - **AIMessage** [tool_calls]: `get_recent_alerts({})`
  - **ToolMessage** (tool=`get_recent_alerts`): `[{"id": 1250, "equipment_id": "SHT-L3-TFT-02", "alert_type": "WARNING", "load_rate_pct": 90.1, "threshold_pct": 78.0, "triggered_at": "2026-02-26 14:57:01", "resolved_at": null, "message": "SHT-L3-TFT-02 부하율 90.1% — 경고 78.0% 초과", "equipment_type": "SHUTTLE", "line": "L3", "zone": "TFT"}, {"id": 1226...`
  - **AIMessage**: 24시간 동안 발생한 알림 이력입니다.

| ID   | 장비 ID        | 장비 유형   | 라인   | 구간     | 부하율(%) | 임계값(%) | 알림 유형   | 발생 시각            | 메시지                               |
| :----- | :------------- | :---------- | :----- | :------- | :------- | :------- | :---------- | :------------------- | :----------------------...

---
## Step 3: ResponseAgent (응답생성)
### State BEFORE
### State Snapshot
- **user_input**: `최근 알림 이력 보여줘`
- **intent**: `alert_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: ``
- **messages** (3건):
  - **AIMessage** [tool_calls]: `get_recent_alerts({})`
  - **ToolMessage** (tool=`get_recent_alerts`): `[{"id": 1250, "equipment_id": "SHT-L3-TFT-02", "alert_type": "WARNING", "load_rate_pct": 90.1, "threshold_pct": 78.0, "triggered_at": "2026-02-26 14:57:01", "resolved_at": null, "message": "SHT-L3-TFT-02 부하율 90.1% — 경고 78.0% 초과", "equipment_type": "SHUTTLE", "line": "L3", "zone": "TFT"}, {"id": 1226...`
  - **AIMessage**: 24시간 동안 발생한 알림 이력입니다.

| ID   | 장비 ID        | 장비 유형   | 라인   | 구간     | 부하율(%) | 임계값(%) | 알림 유형   | 발생 시각            | 메시지                               |
| :----- | :------------- | :---------- | :----- | :------- | :------- | :------- | :---------- | :------------------- | :----------------------...
### 처리: 메시지 히스토리에서 최종 AI 응답 추출
### 최종 응답 (final_answer)
```
24시간 동안 발생한 알림 이력입니다.

| ID   | 장비 ID        | 장비 유형   | 라인   | 구간     | 부하율(%) | 임계값(%) | 알림 유형   | 발생 시각            | 메시지                               |
| :----- | :------------- | :---------- | :----- | :------- | :------- | :------- | :---------- | :------------------- | :----------------------------------- |
| 1250 | SHT-L3-TFT-02  | SHUTTLE     | L3     | TFT      | 90.1     | 78       | WARNING     | 2026-02-26 14:57:01 | SHT-L3-TFT-02 부하율 90.1% — 경고 78.0% 초과 |
| 1226 | CVR-L1-CELL-01 | CONVEYOR    | L1     | CELL     | 98.3     | 95       | CRITICAL    | 2026-02-26 14:57:01 | CVR-L1-CELL-01 부하율 98.3% — 임계값 95.0% 초과 |
| 1194 | SHT-L3-MODULE-01 | SHUTTLE     | L3     | MODULE   | 91.2     | 78       | WARNING     | 2026-02-26 14:57:01 | SHT-L3-MODULE-01 부하율 91.2% — 경고 78.0% 초과 |
| 1165 | SHT-L3-CELL-01 | SHUTTLE     | L3     | CELL     | 98.1     | 92       | CRITICAL    | 2026-02-26 14:57:01 | SHT-L3-CELL-01 부하율 98.1% — 임계값 92.0% 초과 |
| 1139 | CRN-L1-MODULE-01 | CRANE       | L1     | MODULE   | 88.8     | 85       | CRITICAL    | 2026-02-26 14:57:01 | CRN-L1-MODULE-01 부하율 88.8% — 임계값 85.0% 초과 |
| 1100 | SHT-L1-TFT-02  | SHUTTLE     | L1     | TFT      | 88.8     | 78       | WARNING     | 2026-02-26 14:57:01 | SHT-L1-TFT-02 부하율 88.8% — 경고 78.0% 초과 |
| 1058 | SHT-L3-PACK-01 | SHUTTLE     | L3     | PACK     | 78.6     | 78       | WARNING     | 2026-02-26 14:57:01 | SHT-L3-PACK-01 부하율 78.6% — 경고 78.0% 초과 |
| 1048 | AGV-L1-CELL-01 | AGV         | L1     | CELL     | 94.7     | 90       | CRITICAL    | 2026-02-26 14:57:01 | AGV-L1-CELL-01 부하율 94.7% — 임계값 90.0% 초과 |
| 1024 | SHT-L1-TFT-01  | SHUTTLE     | L1     | TFT      | 87.9     | 78       | WARNING     | 2026-02-26 14:57:01 | SHT-L1-TFT-01 부하율 87.9% — 경고 78.0% 초과 |
| 1249 | SHT-L3-TFT-02  | SHUTTLE     | L3     | TFT      | 91.6     | 78       | WARNING     | 2026-02-26 14:47:01 | SHT-L3-TFT-02 부하율 91.6% — 경고 78.0% 초과 |
| 1225 | CVR-L1-CELL-01 | CONVEYOR    | L1     | CELL     | 96.9     | 95       | CRITICAL    | 2026-02-26 14:47:01 | CVR-L1-CELL-01 부하율 96.9% — 임계값 95.0% 초과 |
| 1193 | SHT-L3-MODULE-01 | SHUTTLE     | L3     | MODULE   | 99.2     | 92       | CRITICAL    | 2026-02-26 14:47:01 | SHT-L3-MODULE-01 부하율 99.2% — 임계값 92.0% 초과 |
| 1169 | CVR-L1-TFT-02  | CONVEYOR    | L1     | TFT      | 82.9     | 80       | WARNING     | 2026-02-26 14:47:01 | CVR-L1-TFT-02 부하율 82.9% — 경고 80.0% 초과 |
| 1164 | SHT-L3-CELL-01 | SHUTTLE     | L3     | CELL     | 93.0     | 92       | CRITICAL    | 2026-02-26 14:47:01 | SHT-L3-CELL-01 부하율 93.0% — 임계값 92.0% 초과 |
| 1138 | CRN-L1-MODULE-01 | CRANE       | L1     | MODULE   | 95.6     | 85       | CRITICAL    | 2026-02-26 14:47:01 | CRN-L1-MODULE-01 부하율 95.6% — 임계값 85.0% 초과 |
| 1115 | CRN-L2-MODULE-01 | CRANE       | L2     | MODULE   | 84.8     | 70       | WARNING     | 2026-02-26 14:47:01 | CRN-L2-MODULE-01 부하율 84.8% — 경고 70.0% 초과 |
| 1109 | CRN-L1-CELL-01 | CRANE       | L1     | CELL     | 71.0     | 70       | WARNING     | 2026-02-26 14:47:01 | CRN-L1-CELL-01 부하율 71.0% — 경고 70.0% 초과 |
| 1099 | SHT-L1-TFT-02  | SHUTTLE     | L1     | TFT      | 95.3     | 92       | CRITICAL    | 2026-02-26 14:47:01 | SHT-L1-TFT-02 부하율 95.3% — 임계값 92.0% 초과 |
| 1047 | AGV-L1-CELL-01 | AGV         | L1     | CELL     | 93.0     | 90       | CRITICAL    | 2026-02-26 14:47:01 | AGV-L1-CELL-01 부하율 93.0% — 임계값 90.0% 초과 |
| 1023 | SHT-L1-TFT-01  | SHUTTLE     | L1     | TFT      | 95.6     | 92       | CRITICAL    | 2026-02-26 14:47:01 | SHT-L1-TFT-01 부하율 95.6% — 임계값 92.0% 초과 |
| 1248 | SHT-L3-TFT-02  | SHUTTLE     | L3     | TFT      | 90.4     | 78       | WARNING     | 2026-02-26 14:37:01 | SHT-L3-TFT-02 부하율 90.4% — 경고 78.0% 초과 |
| 1224 | CVR-L1-CELL-01 | CONVEYOR    | L1     | CELL     | 84.6     | 80       | WARNING     | 2026-02-26 14:37:01 | CVR-L1-CELL-01 부하율 84.6% — 경고 80.0% 초과 |
| 1192 | SHT-L3-MODULE-01 | SHUTTLE     | L3     | MODULE   | 87.8     | 78       | WARNING     | 2026-02-26 14:37:01 | SHT-L3-MODULE-01 부하율 87.8% — 경고 78.0% 초과 |
| 1163 | SHT-L3-CELL-01 | SHUTTLE     | L3     | CELL     | 99.2     | 92       | CRITICAL    | 2026-02-26 14:37:01 | SHT-L3-CELL-01 부하율 99.2% — 임계값 92.0% 초과 |
| 1137 | CRN-L1-MODULE-01 | CRANE       | L1     | MODULE   | 91.2     | 85       | CRITICAL    | 2026-02-26 14:37:01 | CRN-L1-MODULE-01 부하율 91.2% — 임계값 85.0% 초과 |
| 1098 | SHT-L1-TFT-02  | SHUTTLE     | L1     | TFT      | 85.4     | 78       | WARNING     | 2026-02-26 14:37:01 | SHT-L1-TFT-02 부하율 85.4% — 경고 78.0% 초과 |
| 1068 | CVR-L1-PACK-01 | CONVEYOR    | L1     | PACK     | 82.1     | 80       | WARNING     | 2026-02-26 14:37:01 | CVR-L1-PACK-01 부하율 82.1% — 경고 80.0% 초과 |
| 1046 | AGV-L1-CELL-01 | AGV         | L1     | CELL     | 84.6     | 75       | WARNING     | 2026-02-26 14:37:01 | AGV-L1-CELL-01 부하율 84.6% — 경고 75.0% 초과 |
| 1022 | SHT-L1-TFT-01  | SHUTTLE     | L1     | TFT      | 88.5     | 78       | WARNING     | 2026-02-26 14:37:01 | SHT-L1-TFT-01 부하율 88.5% — 경고 78.0% 초과 |
| 1247 | SHT-L3-TFT-02  | SHUTTLE     | L3     | TFT      | 90.5     | 78       | WARNING     | 2026-02-26 14:27:01 | SHT-L3-TFT-02 부하율 90.5% — 경고 78.0% 초과 |
| 1223 | CVR-L1-CELL-01 | CONVEYOR    | L1     | CELL     | 86.3     | 80       | WARNING     | 2026-02-26 14:27:01 | CVR-L1-CELL-01 부하율 86.3% — 경고 80.0% 초과 |
| 1191 | SHT-L3-MODULE-01 | SHUTTLE     | L3     | MODULE   | 94.8     | 92       | CRITICAL    | 2026-02-26 14:27:01 | SHT-L3-MODULE-01 부하율 94.8% — 임계값 92.0% 초과 |
| 1162 | SHT-L3-CELL-01 | SHUTTLE     | L3     | CELL     | 86.4     | 78       | WARNING     | 2026-02-26 14:27:01 | SHT-L3-CELL-01 부하율 86.4% — 경고 78.0% 초과 |
| 1136 | CRN-L1-MODULE-01 | CRANE       | L1     | MODULE   | 91.2     | 85       | CRITICAL    | 2026-02-26 14:27:01 | CRN-L1-MODULE-01 부하율 91.2% — 임계값 85.0% 초과 |
| 1108 | CRN-L1-CELL-01 | CRANE       | L1     | CELL     | 73.1     | 70       | WARNING     | 2026-02-26 14:27:01 | CRN-L1-CELL-01 부하율 73.1% — 경고 70.0% 초과 |
| 1097 | SHT-L1-TFT-02  | SHUTTLE     | L1     | TFT      | 95.0     | 92       | CRITICAL    | 2026-02-26 14:27:01 | SHT-L1-TFT-02 부하율 95.0% — 임계값 92.0% 초과 |
| 1076 | STK-L1-PACK-01 | STACKER     | L1     | PACK     | 83.1     | 75       | WARNING     | 2026-02-26 14:27:01 | STK-L1-PACK-01 부하율 83.1% — 경고 75.0% 초과 |
| 1045 | AGV-L1-CELL-01 | AGV         | L1     | CELL     | 99.1     | 90       | CRITICAL    | 2026-02-26 14:27:01 | AGV-L1-CELL-01 부하율 99.1% — 임계값 90.0% 초과 |
| 1021 | SHT-L1-TFT-01  | SHUTTLE     | L1     | TFT      | 84.5     | 78       | WARNING     | 2026-02-26 14:27:01 | SHT-L1-TFT-01 부하율 84.5% — 경고 78.0% 초과 |
| 1246 | SHT-L3-TFT-02  | SHUTTLE     | L3     | TFT      | 87.1     | 78       | WARNING     | 2026-02-26 14:17:01 | SHT-L3-TFT-02 부하율 87.1% — 경고 78.0% 초과 |
| 1222 | CVR-L1-CELL-01 | CONVEYOR    | L1     | CELL     | 99.8     | 95       | CRITICAL    | 2026-02-26 14:17:01 | CVR-L1-CELL-01 부하율 99.8% — 임계값 95.0% 초과 |
| 1198 | SRT-L3-PACK-01 | SORTER      | L3     | PACK     | 84.0     | 80       | WARNING     | 2026-02-26 14:17:01 | SRT-L3-PACK-01 부하율 84.0% — 경고 80.0% 초과 |
| 1190 | SHT-L3-MODULE-01 | SHUTTLE     | L3     | MODULE   | 86.6     | 78       | WARNING     | 2026-02-26 14:17:01 | SHT-L3-MODULE-01 부하율 86.6% — 경고 78.0% 초과 |
| 1161 | SHT-L3-CELL-01 | SHUTTLE     | L3     | CELL     | 85.6     | 78       | WARNING     | 2026-02-26 14:17:01 | SHT-L3-CELL-01 부하율 85.6% — 경고 78.0% 초과 |
| 1135 | CRN-L1-MODULE-01 | CRANE       | L1     | MODULE   | 90.7     | 85       | CRITICAL    | 2026-02-26 14:17:01 | CRN-L1-MODULE-01 부하율 90.7% — 임계값 85.0% 초과 |
| 1107 | CRN-L1-CELL-01 | CRANE       | L1     | CELL     | 79.2     | 70       | WARNING     | 2026-02-26 14:17:01 | CRN-L1-CELL-01 부하율 79.2% — 경고 70.0% 초과 |
| 1096 | SHT-L1-TFT-02  | SHUTTLE     | L1     | TFT      | 92.7     | 92       | CRITICAL    | 2026-02-26 14:17:01 | SHT-L1-TFT-02 부하율 92.7% — 임계값 92.0% 초과 |
| 1075 | STK-L1-PACK-01 | STACKER     | L1     | PACK     | 84.8     | 75       | WARNING     | 2026-02-26 14:17:01 | STK-L1-PACK-01 부하율 84.8% — 경고 75.0% 초과 |
| 1044 | AGV-L1-CELL-01 | AGV         | L1     | CELL     | 85.1     | 75       | WARNING     | 2026-02-26 14:17:01 | AGV-L1-CELL-01 부하율 85.1% — 경고 75.0% 초과 |
| 1020 | SHT-L1-TFT-01  | SHUTTLE     | L1     | TFT      | 95.3     | 92       | CRITICAL    | 2026-02-26 14:17:01 | SHT-L1-TFT-01 부하율 95.3% — 임계값 92.0% 초과 |
| 1245 | SHT-L3-TFT-02  | SHUTTLE     | L3     | TFT      | 89.4     | 78       | WARNING     | 2026-02-26 14:07:01 | SHT-L3-TFT-02 부하율 89.4% — 경고 78.0% 초과 |
| 1221 | CVR-L1-CELL-01 | CONVEYOR    | L1     | CELL     | 86.1     | 80       | WARNING     | 2026-02-26 14:07:01 | CVR-L1-CELL-01 부하율 86.1% — 경고 80.0% 초과 |
| 1189 | SHT-L3-MODULE-01 | SHUTTLE     | L3     | MODULE   | 90.5     | 78       | WARNING     | 2026-02-26 14:07:01 | SHT-L3-MODULE-01 부하율 90.5% — 경고 78.0% 초과 |
| 1160 | SHT-L3-CELL-01 | SHUTTLE     | L3     | CELL     | 99.3     | 92       | CRITICAL    | 2026-02-26 14:07:01 | SHT-L3-CELL-01 부하율 99.3% — 임계값 92.0% 초과 |
| 1134 | CRN-L1-MODULE-01 | CRANE       | L1     | MODULE   | 84.3     | 70       | WARNING     | 2026-02-26 14:07:01 | CRN-L1-MODULE-01 부하율 84.3% — 경고 70.0% 초과 |
| 1114 | CRN-L2-MODULE-01 | CRANE       | L2     | MODULE   | 81.6     | 70       | WARNING     | 2026-02-26 14:07:01 | CRN-L2-MODULE-01 부하율 81.6% — 경고 70.0% 초과 |
| 1106 | CRN-L1-CELL-01 | CRANE       | L1     | CELL     | 79.6     | 70       | WARNING     | 2026-02-26 14:07:01 | CRN-L1-CELL-01 부하율 79.6% — 경고 70.0% 초과 |
| 1095 | SHT-L1-TFT-02  | SHUTTLE     | L1     | TFT      | 94.0     | 92       | CRITICAL    | 2026-02-26 14:07:01 | SHT-L1-TFT-02 부하율 94.0% — 임계값 92.0% 초과 |
| 1043 | AGV-L1-CELL-01 | AGV         | L1     | CELL     | 92.1     | 90       | CRITICAL    | 2026-02-26 14:07:01 | AGV-L1-CELL-01 부하율 92.1% — 임계값 90.0% 초과 |
| 1019 | SHT-L1-TFT-01  | SHUTTLE     | L1     | TFT      | 92.9     | 92       | CRITICAL    | 2026-02-26 14:07:01 | SHT-L1-TFT-01 부하율 92.9% — 임계값 92.0% 초과 |
| 1244 | SHT-L3-TFT-02  | SHUTTLE     | L3     | TFT      | 94.4     | 92       | CRITICAL    | 2026-02-26 13:57:01 | SHT-L3-TFT-02 부하율 94.4% — 임계값 92.0% 초과 |
| 1220 | CVR-L1-CELL-01 | CONVEYOR    | L1     | CELL     | 97.2     | 95       | CRITICAL    | 2026-02-26 13:57:01 | CVR-L1-CELL-01 부하율 97.2% — 임계값 95.0% 초과 |
| 1188 | SHT-L3-MODULE-01 | SHUTTLE     | L3     | MODULE   | 96.7     | 92       | CRITICAL    | 2026-02-26 13:57:01 | SHT-L3-MODULE-01 부하율 96.7% — 임계값 92.0% 초과 |
| 1159 | SHT-L3-CELL-01 | SHUTTLE     | L3     | CELL     | 87.1     | 78       | WARNING     | 2026-02-26 13:57:01 | SHT-L3-CELL-01 부하율 87.1% — 경고 78.0% 초과 |
| 1133 | CRN-L1-MODULE-01 | CRANE       | L1     | MODULE   | 89.7     | 85       | CRITICAL    | 2026-02-26 13:57:01 | CRN-L1-MODULE-01 부하율 89.7% — 임계값 85.0% 초과 |
| 1105 | CRN-L1-CELL-01 | CRANE       | L1     | CELL     | 76.9     | 70       | WARNING     | 2026-02-26 13:57:01 | CRN-L1-CELL-01 부하율 76.9% — 경고 70.0% 초과 |
| 1094 | SHT-L1-TFT-02  | SHUTTLE     | L1     | TFT      | 94.8     | 92       | CRITICAL    | 2026-02-26 13:57:01 | SHT-L1-TFT-02 부하율 94.8% — 임계값 92.0% 초과 |
| 1042 | AGV-L1-CELL-01 | AGV         | L1     | CELL     | 98.7     | 90       | CRITICAL    | 2026-02-26 13:57:01 | AGV-L1-CELL-01 부하율 98.7% — 임계값 90.0% 초과 |
| 1018 | SHT-L1-TFT-01  | SHUTTLE     | L1     | TFT      | 88.0     | 78       | WARNING     | 2026-02-26 13:57:01 | SHT-L1-TFT-01 부하율 88.0% — 경고 78.0% 초과 |
| 1243 | SHT-L3-TFT-02  | SHUTTLE     | L3     | TFT      | 96.9     | 92       | CRITICAL    | 2026-02-26 13:47:01 | SHT-L3-TFT-02 부하율 96.9% — 임계값 92.0% 초과 |
| 1219 | CVR-L1-CELL-01 | CONVEYOR    | L1     | CELL     | 90.2     | 80       | WARNING     | 2026-02-26 13:47:01 | CVR-L1-CELL-01 부하율 90.2% — 경고 80.0% 초과 |
| 1197 | SRT-L3-PACK-01 | SORTER      | L3     | PACK     | 84.1     | 80       | WARNING     | 2026-02-26 13:47:01 | SRT-L3-PACK-01 부하율 84.1% — 경고 80.0% 초과 |
| 1187 | SHT-L3-MODULE-01 | SHUTTLE     | L3     | MODULE   | 93.8     | 92       | CRITICAL    | 2026-02-26 13:47:01 | SHT-L3-MODULE-01 부하율 93.8% — 임계값 92.0% 초과 |
| 1158 | SHT-L3-CELL-01 | SHUTTLE     | L3     | CELL     | 85.2     | 78       | WARNING     | 2026-02-26 13:47:01 | SHT-L3-CELL-01 부하율 85.2% — 경고 78.0% 초과 |
| 1132 | CRN-L1-MODULE-01 | CRANE       | L1     | MODULE   | 85.8     | 85       | CRITICAL    | 2026-02-26 13:47:01 | CRN-L1-MODULE-01 부하율 85.8% — 임계값 85.0% 초과 |
| 1093 | SHT-L1-TFT-02  | SHUTTLE     | L1     | TFT      | 90.4     | 78       | WARNING     | 2026-02-26 13:47:01 | SHT-L1-TFT-02 부하율 90.4% — 경고 78.0% 초과 |
| 1057 | SHT-L3-PACK-01 | SHUTTLE     | L3     | PACK     | 78.5     | 78       | WARNING     | 2026-02-26 13:47:01 | SHT-L3-PACK-01 부하율 78.5% — 경고 78.0% 초과 |
| 1052 | CVR-L1-TFT-01  | CONVEYOR    | L1     | TFT      | 80.1     | 80       | WARNING     | 2026-02-26 13:47:01 | CVR-L1-TFT-01 부하율 80.1% — 경고 80.0% 초과 |
| 1041 | AGV-L1-CELL-01 | AGV         | L1     | CELL     | 89.0     | 75       | WARNING     | 2026-02-26 13:47:01 | AGV-L1-CELL-01 부하율 89.0% — 경고 75.0% 초과 |
| 1017 | SHT-L1-TFT-01  | SHUTTLE     | L1     | TFT      | 90.0     | 78       | WARNING     | 2026-02-26 13:47:01 | SHT-L1-TFT-01 부하율 90.0% — 경고 78.0% 초과 |
| 1242 | SHT-L3-TFT-02  | SHUTTLE     | L3     | TFT      | 86.1     | 78       | WARNING     | 2026-02-26 13:37:01 | SHT-L3-TFT-02 부하율 86.1% — 경고 78.0% 초과 |
| 1218 | CVR-L1-CELL-01 | CONVEYOR    | L1     | CELL     | 93.0     | 
```
### State AFTER
### State Snapshot
- **user_input**: `최근 알림 이력 보여줘`
- **intent**: `alert_check`
- **intent_detail**: `{"equipment_type": "", "line": "", "zone": "", "equipment_id": "", "hours": 0, "keyword": ""}`
- **final_answer**: `24시간 동안 발생한 알림 이력입니다.

| ID   | 장비 ID        | 장비 유형   | 라인   | 구간     | 부하율(%) | 임계값(%) | 알림 유형   | 발생 시각            | 메시지                               |
| :----- | :------------- | :---------- | :-`
- **messages** (3건):
  - **AIMessage** [tool_calls]: `get_recent_alerts({})`
  - **ToolMessage** (tool=`get_recent_alerts`): `[{"id": 1250, "equipment_id": "SHT-L3-TFT-02", "alert_type": "WARNING", "load_rate_pct": 90.1, "threshold_pct": 78.0, "triggered_at": "2026-02-26 14:57:01", "resolved_at": null, "message": "SHT-L3-TFT-02 부하율 90.1% — 경고 78.0% 초과", "equipment_type": "SHUTTLE", "line": "L3", "zone": "TFT"}, {"id": 1226...`
  - **AIMessage**: 24시간 동안 발생한 알림 이력입니다.

| ID   | 장비 ID        | 장비 유형   | 라인   | 구간     | 부하율(%) | 임계값(%) | 알림 유형   | 발생 시각            | 메시지                               |
| :----- | :------------- | :---------- | :----- | :------- | :------- | :------- | :---------- | :------------------- | :----------------------...