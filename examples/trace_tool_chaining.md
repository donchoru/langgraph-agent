# 예시 12: 도구 체이닝 — 순차 호출 패턴

> **학습 목표**: 1차 도구 결과에서 ID를 추출하여 2차 도구를 추가 호출하는
> **도구 체이닝(순차 실행)** 패턴의 전체 흐름을 FM I/O 관점에서 추적한다.

---

## 입력

```
L1 라인에 과부하 장비 있어? 있으면 그 장비 상세도 보여줘
```

---

## Step 1: IntentAgent (의도분석)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash)
- **System**: INTENT_SYSTEM_PROMPT (의도 6개 + JSON형식 + 매핑규칙)
- **Human**:
```
L1 라인에 과부하 장비 있어? 있으면 그 장비 상세도 보여줘
```

### 🔶 FM 출력 (← Gemini)
```json
{
  "intent": "overload_check",
  "detail": {
    "equipment_type": "",
    "line": "L1",
    "zone": "",
    "equipment_id": "",
    "lot_id": "",
    "hours": 0,
    "keyword": "상세"
  },
  "reasoning": "L1 라인 과부하 장비 확인 + 상세 정보 요청"
}
```

---

## Step 2: InfoAgent (정보조회, 첫 호출)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 첫 호출)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 체이닝 규칙)
- **Human**:
```
사용자 질문: L1 라인에 과부하 장비 있어? 있으면 그 장비 상세도 보여줘
의도: overload_check
상세: {"equipment_type": "", "line": "L1", ...}

위 의도에 맞는 도구를 호출하여 정보를 조회하세요.
```

### 🔶 FM 출력 (← Gemini) → Tool 호출 요청 (Round 1)
- `get_overloaded_equipment({"line": "L1"})`

> **포인트**: 1차로 과부하 장비 목록 조회. 체이닝 규칙에 따라 결과에서 ID 추출 후 2차 호출 예정.

---

## Step 2.5: ToolNode (SQL 실행) (Round 1)

### Tool 결과
```
ToolMessage (get_overloaded_equipment):
[{"equipment_id": "CVR-L1-001", "equipment_type": "CONVEYOR", "line": "L1",
  "zone": "TFT", "load_rate_pct": 92.3, "warning_pct": 80, "critical_pct": 95}]
```

---

## Step 2 재진입: InfoAgent (Tool 결과 수신, Round 1)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 재진입 Round 1)
- **System**: INFO_SYSTEM_PROMPT (도구 10개 + 체이닝 규칙)
- **Messages**: 메시지 히스토리 (AI tool_call + ToolMessage)
- **Guide**: "도구 실행 결과를 분석하세요. 사용자의 질문에 완전히 답하기 위해 추가 조회가 필요하면 도구를 더 호출하고, 충분한 정보가 모였으면 최종 응답을 생성하세요."

### 🔶 FM 출력 (← Gemini) → Tool 호출 요청 (Round 2)
- `get_equipment_detail({"equipment_id": "CVR-L1-001"})`

> **포인트**: FM이 1차 결과에서 `CVR-L1-001`을 추출하여 2차 도구 호출.
> 가이드 메시지가 "추가 조회 가능"을 안내했기 때문에 체이닝이 발생.

---

## Step 2.5: ToolNode (SQL 실행) (Round 2)

### Tool 결과
```
ToolMessage (get_equipment_detail):
{"equipment_id": "CVR-L1-001", "equipment_type": "CONVEYOR", "line": "L1",
 "zone": "TFT", "status": "RUNNING", "installed_date": "2024-01-15",
 "recent_loads": [{"load_rate_pct": 92.3, "recorded_at": "..."},
                  {"load_rate_pct": 88.7, "recorded_at": "..."}],
 "recent_alerts": [...]}
```

---

## Step 2 재진입: InfoAgent (Tool 결과 수신, Round 2)

### 🔷 FM 입력 (→ Gemini gemini-2.0-flash, 재진입 Round 2)
- **System**: INFO_SYSTEM_PROMPT
- **Messages**: 메시지 히스토리 4건 (AI+Tool+AI+Tool)
- **Guide**: "도구 실행 결과를 분석하세요. ..."

### 🔶 FM 출력 (← Gemini) → 텍스트 응답
```
## L1 라인 과부하 장비

| 장비 ID | 유형 | 구간 | 부하율 | 상태 |
|---------|------|------|--------|------|
| CVR-L1-001 | CONVEYOR | TFT | 92.3% ⚠️ | RUNNING |

### CVR-L1-001 상세

- **설치일**: 2024-01-15
- **현재 부하율**: 92.3% (경고 임계 80% 초과)
- **최근 추이**: 88.7% → 92.3% (상승 중)
- **알림**: 최근 경고 알림 발생

⚠️ 부하율이 임계치(95%)에 근접하고 있어 주의가 필요합니다.
```

> **포인트**: 2차 결과까지 종합하여 과부하 목록 + 장비 상세를 하나의 응답으로 생성.

---

## Step 3: ResponseAgent (응답생성)

최종 응답 추출 (InfoAgent 재진입에서 생성된 텍스트).

---

## FM 호출 요약

| 단계 | FM 역할 | 입력 | 출력 |
|------|---------|------|------|
| IntentAgent | 의도 분류 | System + Human(질문) | JSON: `overload_check` |
| InfoAgent 1차 | Tool 선택 | System + Human(질문+의도) | tool_call: `get_overloaded_equipment` |
| InfoAgent Round 1 | **체이닝 판단** | System + Messages + Guide | tool_call: `get_equipment_detail` |
| InfoAgent Round 2 | 응답 생성 | System + Messages + Guide | 텍스트: 종합 응답 |

**총 FM 호출: 4회** (IntentAgent 1 + InfoAgent 3)
**도구 호출: 2회** (Round 1 + Round 2)

---

## 학습 포인트

1. **도구 체이닝**: 1차 결과(과부하 목록)에서 장비 ID를 추출하여 2차 도구(장비 상세)를 자동 호출. 기존 `info_agent → tools → info_agent` 루프를 그대로 활용.
2. **가이드 메시지**: 재진입 시 "추가 조회 가능" 안내가 FM의 체이닝 판단을 유도. `MAX_TOOL_ROUNDS=3`으로 무한 루프 방지.
3. **기존 단일 호출과의 호환**: 체이닝이 불필요한 질문(예: "컨베이어 부하율 알려줘")은 재진입 시 바로 텍스트 응답을 생성하여 기존과 동일하게 동작.
4. **그래프 구조 변경 없음**: 노드/엣지 추가 없이 `tool_call_round` 상태값과 가이드 메시지만으로 체이닝 구현.
