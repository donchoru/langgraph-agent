# 개발 가이드 — LangGraph 물류 장비 부하율 관리

이 문서는 프로젝트의 내부 동작 원리, 확장 방법, 디버깅 방법을 설명합니다.

## 목차

- [아키텍처 심층 분석](#아키텍처-심층-분석)
- [그래프 구조 상세](#그래프-구조-상세)
- [확장 가이드](#확장-가이드)
  - [새 SQL Tool 추가](#새-sql-tool-추가)
  - [새 의도 추가](#새-의도-추가)
  - [새 DB 테이블 추가](#새-db-테이블-추가)
  - [LLM 백엔드 변경](#llm-백엔드-변경)
- [Jinja2 SQL 템플릿 작성법](#jinja2-sql-템플릿-작성법)
- [커넥션 풀 운영](#커넥션-풀-운영)
- [ReAct Agent 동작 원리](#react-agent-동작-원리)
- [메시지 트리밍 상세](#메시지-트리밍-상세)
- [디버깅 가이드](#디버깅-가이드)
- [성능 튜닝](#성능-튜닝)
- [코드 패턴 레퍼런스](#코드-패턴-레퍼런스)

---

## 아키텍처 심층 분석

### 계층 구조

```
┌──────────────────────────────────────────────────────────┐
│  Presentation Layer                                       │
│  main.py — 대화형 CLI, 트레이스 저장                       │
├──────────────────────────────────────────────────────────┤
│  Orchestration Layer                                      │
│  graph/workflow.py — StateGraph, 노드 연결, 라우팅         │
├──────────────────────────────────────────────────────────┤
│  Agent Layer                                              │
│  agents/intent_agent.py — 키워드+LLM 의도분석              │
│  agents/info_agent.py   — ReAct Agent 래퍼 + ResponseNode │
│  agents/prompts.py      — 시스템 프롬프트                  │
│  agents/message_trimmer.py — 3계층 토큰 관리               │
├──────────────────────────────────────────────────────────┤
│  Tool Layer                                               │
│  tools/sql_tools.py      — 10개 @tool 함수                │
│  tools/template_engine.py — Jinja2 SQL 렌더러             │
│  templates/*.sql          — SQL 템플릿 14개               │
├──────────────────────────────────────────────────────────┤
│  Data Layer                                               │
│  db/connection.py — 커넥션 풀                              │
│  db/schema.sql    — 테이블 스키마                          │
│  db/seed.py       — 샘플 데이터 생성                       │
├──────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                     │
│  config.py       — 환경변수, 경로                          │
│  llm_factory.py  — Gemini / OpenAI 호환 LLM 팩토리        │
└──────────────────────────────────────────────────────────┘
```

### 데이터 흐름

```
사용자 입력 "L1 과부하 장비 보여줘"
    │
    ▼ [main.py]
    │  state = { user_input: "...", messages: [], intent: "", ... }
    │
    ▼ [workflow.py → intent_agent]
    │  1. 키워드 매칭: "과부하" → ["overload_check"]
    │  2. LLM 판단: "overload_check"
    │  → state.intent = "overload_check"
    │
    ▼ [workflow.py → route_by_intent]
    │  intent != "general_chat" → "react_agent" 노드로
    │
    ▼ [info_agent.py → react_agent_node]
    │  프롬프트 구성 → react_agent.invoke()
    │  ┌───────────────────────────────────────┐
    │  │ [create_react_agent 내부]              │
    │  │ LLM: "get_overloaded_equipment 호출"  │
    │  │ Tool: SQL 실행 → JSON 결과             │
    │  │ LLM: "과부하 장비 목록입니다..."        │
    │  └───────────────────────────────────────┘
    │  → state.messages = [...전체 메시지...]
    │
    ▼ [workflow.py → respond_node]
    │  마지막 AIMessage 텍스트 추출
    │  → state.final_answer = "과부하 장비 목록입니다..."
    │
    ▼ [main.py]
       응답 출력 + 트레이스 저장 + 대화 이력 갱신
```

---

## 그래프 구조 상세

### 노드 3개

```python
# graph/workflow.py
graph.add_node("intent_agent", intent_node)      # 의도 분류
graph.add_node("react_agent", react_agent_node)   # ReAct Agent (Tool 루프 내장)
graph.add_node("respond", respond_node)           # 최종 응답 추출
```

### 엣지 구성

```python
graph.set_entry_point("intent_agent")
graph.add_conditional_edges("intent_agent", route_by_intent, {
    "react_agent": "react_agent",  # 도메인 질문
    "respond": "respond",          # 일반 대화
})
graph.add_edge("react_agent", "respond")
graph.add_edge("respond", END)
```

### 라우팅 함수

```python
def route_by_intent(state: AgentState) -> str:
    if state["intent"] == "general_chat":
        return "respond"    # InfoAgent 스킵
    return "react_agent"    # Tool 호출 경로
```

---

## 확장 가이드

### 새 SQL Tool 추가

**예시**: 장비 가동 시간 조회 Tool 추가

#### Step 1: SQL 템플릿 작성

```sql
-- templates/equipment_uptime.sql
SELECT e.equipment_id, e.equipment_type, e.line, e.zone,
       COUNT(*) as total_records,
       SUM(CASE WHEN e.status = 'RUNNING' THEN 1 ELSE 0 END) as running_count,
       ROUND(SUM(CASE WHEN e.status = 'RUNNING' THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 1) as uptime_pct
FROM load_rate lr
JOIN equipment e ON lr.equipment_id = e.equipment_id
WHERE lr.recorded_at >= datetime('now', 'localtime', '-{{ hours }} hours')
{% if equipment_type %}
AND e.equipment_type = :equipment_type
{% endif %}
{% if line %}
AND e.line = :line
{% endif %}
GROUP BY e.equipment_id
ORDER BY uptime_pct DESC
```

#### Step 2: Tool 함수 작성

```python
# tools/sql_tools.py에 추가

@tool
def get_equipment_uptime(equipment_type: Optional[str] = None, line: Optional[str] = None, hours: int = 24) -> str:
    """장비 가동률 조회 — 최근 N시간 동안의 가동률(%). 유형/라인 필터 가능."""
    sql, params = render_sql("equipment_uptime.sql",
                             hours=int(hours),
                             equipment_type=equipment_type and equipment_type.upper(),
                             line=line and line.upper())
    rows = query(sql, params)
    return json.dumps(rows, ensure_ascii=False)
```

#### Step 3: ALL_TOOLS에 등록

```python
ALL_TOOLS = [
    # ... 기존 10개 ...
    get_equipment_uptime,   # 추가
]
```

#### Step 4: 시스템 프롬프트에 가이드 추가

```python
# agents/prompts.py의 INFO_SYSTEM_PROMPT에 추가

## 사용 가능한 도구
# ...
# 11. get_equipment_uptime — 장비 가동률 조회 (최근 N시간)

## 도구 선택 가이드
# - 가동률/uptime 관련 질문 → get_equipment_uptime
```

> **참고**: `create_react_agent`에 전달되는 `ALL_TOOLS`가 자동으로 LLM에 바인딩되므로,
> 함수의 docstring만 잘 작성하면 Tool 등록은 완료됩니다.
> 시스템 프롬프트 가이드는 선택/정확도 향상을 위한 추가 조치입니다.

---

### 새 의도 추가

**예시**: `maintenance_schedule` 의도 추가

#### Step 1: 키워드 매핑 추가

```python
# agents/intent_agent.py
INTENT_KEYWORDS = {
    # ... 기존 ...
    "maintenance_schedule": ["정비", "유지보수", "점검", "maintenance", "예방정비"],
}
```

#### Step 2: 유효 의도 목록에 추가

```python
VALID_INTENTS = {
    # ... 기존 ...
    "maintenance_schedule",
}
```

#### Step 3: 시스템 프롬프트 업데이트

```python
# agents/prompts.py의 INTENT_SYSTEM_PROMPT에 추가

## 의도 목록
# ...
# - maintenance_schedule: 정비/유지보수 스케줄 조회
```

#### Step 4: 라우팅 확인

`route_by_intent()`는 `general_chat`이 아닌 모든 의도를 `react_agent`로 보내므로,
새 의도는 자동으로 ReAct Agent에서 처리됩니다. 별도 라우팅 변경 불필요.

---

### 새 DB 테이블 추가

#### Step 1: 스키마 정의

```sql
-- db/schema.sql에 추가
CREATE TABLE IF NOT EXISTS maintenance_plan (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id    TEXT NOT NULL REFERENCES equipment(equipment_id),
    scheduled_date  TEXT NOT NULL,
    maintenance_type TEXT NOT NULL,  -- PREVENTIVE, CORRECTIVE, INSPECTION
    description     TEXT,
    completed       INTEGER DEFAULT 0
);
```

#### Step 2: seed 데이터 추가

```python
# db/seed.py에 추가
maintenance_plans = [
    ("CVR-L1-TFT-01", "2026-03-15", "PREVENTIVE", "3개월 정기 점검"),
    # ...
]
for plan in maintenance_plans:
    execute("INSERT INTO maintenance_plan ...")
```

#### Step 3: SQL 템플릿 + Tool 함수 작성

위 [새 SQL Tool 추가](#새-sql-tool-추가) 절차를 따릅니다.

---

### LLM 백엔드 변경

#### Gemini (기본)

```bash
# .env
GEMINI_API_KEY=your-key-here
# 또는
LLM_TYPE=gemini
LLM_MODEL=gemini-2.0-flash
LLM_API_KEY=your-key-here
```

#### Ollama (로컬)

```bash
LLM_TYPE=openai
LLM_MODEL=qwen2.5:14b
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
```

#### OpenAI

```bash
LLM_TYPE=openai
LLM_MODEL=gpt-4o
LLM_API_KEY=sk-...
```

#### 사내 LLM (OpenAI 호환 API)

```bash
LLM_TYPE=openai
LLM_MODEL=your-model-name
LLM_API_KEY=your-key
LLM_BASE_URL=https://your-internal-api.com/v1
```

> **주의**: `create_react_agent`가 Function Calling을 사용하므로,
> Tool Calling을 지원하는 모델이어야 합니다.

---

## Jinja2 SQL 템플릿 작성법

### 기본 규칙

1. **SQL 구조** (WHERE, JOIN, 컬럼 선택)는 Jinja2로 제어
2. **값**은 반드시 `:named_param`으로 바인딩 (SQL Injection 방지)
3. 정수 파라미터(hours 등)는 Python에서 `int()` 캐스팅 후 Jinja2 직접 렌더링 가능

### 패턴별 예시

#### 조건부 WHERE

```sql
SELECT * FROM equipment
WHERE 1=1
{% if equipment_type %}
AND equipment_type = :equipment_type
{% endif %}
{% if line %}
AND line = :line
{% endif %}
ORDER BY equipment_id
```

- `WHERE 1=1`을 사용하면 모든 조건을 `AND`로 시작할 수 있어 편리
- 파라미터가 없으면(`None` 또는 `""`) 해당 조건이 생략됨

#### 조건부 JOIN

```sql
SELECT e.*, lr.load_rate_pct
{% if include_alerts %}
       , at.warning_pct
{% endif %}
FROM equipment e
JOIN load_rate lr ON e.equipment_id = lr.equipment_id
{% if include_alerts %}
JOIN alert_threshold at ON e.equipment_type = at.equipment_type
{% endif %}
```

#### 조건부 컬럼 선택

```sql
SELECT e.equipment_id, e.equipment_type
{% if not use_threshold %}
       , at.warning_pct, at.critical_pct
{% endif %}
FROM ...
```

#### 시간 범위 (정수 렌더링)

```sql
WHERE lr.recorded_at >= datetime('now', 'localtime', '-{{ hours }} hours')
```

> `hours`는 Python에서 `int()` 캐스팅된 정수이므로 안전합니다.

### 렌더링 함수

```python
from tools.template_engine import render_sql

sql, params = render_sql("template_name.sql",
                         equipment_type="CONVEYOR",  # str → :equipment_type
                         line=None,                  # None → 조건 생략
                         hours=3)                    # int → {{ hours }}
# sql: "SELECT ... WHERE ... AND equipment_type = :equipment_type ..."
# params: {"equipment_type": "CONVEYOR"}  (None 제외됨)
```

### 새 템플릿 추가 시 체크리스트

- [ ] `templates/` 디렉토리에 `.sql` 파일 생성
- [ ] 문자열 값은 `:named_param` 사용
- [ ] 정수 값은 `{{ var }}` 사용 (Python에서 int 캐스팅 확인)
- [ ] `WHERE 1=1` 패턴으로 조건부 AND 처리
- [ ] `render_sql()`로 테스트: 필터 없을 때 / 전부 있을 때

---

## 커넥션 풀 운영

### 구현 상세

```python
# db/connection.py

_pool: queue.Queue[sqlite3.Connection] = queue.Queue(maxsize=POOL_SIZE)

def _create_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _init_pool() -> None:
    """최초 1회만 실행 (thread-safe)."""
    global _pool_initialized
    with _pool_lock:
        if _pool_initialized:
            return
        for _ in range(POOL_SIZE):
            _pool.put(_create_connection())
        _pool_initialized = True
```

### 사용 패턴

모든 `query()`, `execute()` 함수가 자동으로 풀에서 꺼내고 반환합니다.
직접 `get_connection()` / `release_connection()`을 사용할 필요 없습니다.

```python
# 이렇게 사용하면 됩니다 (기존과 동일한 인터페이스)
from db.connection import query
rows = query("SELECT * FROM equipment WHERE line = :line", {"line": "L1"})
```

### 풀 크기 조정

```bash
# 단일 사용자 CLI → 기본값 5로 충분
python main.py

# 멀티스레드 서버 (FastAPI 등) → 더 크게
DB_POOL_SIZE=20 python -m uvicorn server:app
```

### 주의사항

- SQLite는 파일 기반이므로 **쓰기 동시성**에 제한 있음 (WAL 모드 고려)
- `check_same_thread=False`는 **읽기 위주**에서 안전
- 커넥션이 풀로 반환될 때 트랜잭션이 남아있지 않도록 주의

---

## ReAct Agent 동작 원리

### create_react_agent 내부

```
┌─────────────────────────────────────────────┐
│ create_react_agent(llm, tools, prompt=fn)    │
│                                              │
│   ┌──────────┐     ┌──────────┐              │
│   │ agent    │────▶│  tools   │              │
│   │ (LLM)   │◀────│ (ToolNode)│              │
│   └──────────┘     └──────────┘              │
│        │                                     │
│        ▼ (tool_calls 없으면)                  │
│   [최종 텍스트 응답]                           │
└─────────────────────────────────────────────┘
```

1. **agent 노드**: `prompt` callable로 메시지 전처리 → LLM 호출
2. LLM이 `tool_calls` 반환 → **tools 노드**로 이동
3. **tools 노드**: Tool 함수 실행 → 결과를 ToolMessage로 추가
4. 다시 **agent 노드**로 → LLM이 추가 Tool 필요 여부 판단
5. `tool_calls` 없으면 → 텍스트 응답 반환

### prompt callable의 역할

```python
def _prompt(state):
    messages = state["messages"]
    trimmed = prepare_messages(list(messages))
    return [SystemMessage(content=INFO_SYSTEM_PROMPT)] + trimmed
```

**매 LLM 호출 시** 호출되어:
1. 시스템 프롬프트를 맨 앞에 주입
2. 메시지 히스토리를 트리밍 (토큰 초과 방지)
3. 결과 메시지 리스트를 LLM에 전달

### recursion_limit

```python
result = react_agent.invoke(
    {"messages": [HumanMessage(content=prompt)]},
    config={"recursion_limit": 10},
)
```

- 각 Tool 라운드 = 2 스텝 (agent + tools)
- `recursion_limit=10` → 최대 4~5 Tool 라운드
- 기본값은 25 (충분히 여유 있음)

---

## 메시지 트리밍 상세

### 왜 필요한가

ReAct Agent의 Tool 루프가 반복되면 메시지가 누적됩니다:
- `HumanMessage` → `AIMessage(tool_calls)` → `ToolMessage(결과)` → `AIMessage(tool_calls)` → ...
- ToolMessage에 JSON 수백~수천 행이 포함되면 토큰 한도 초과

### 3계층 파이프라인

```python
def prepare_messages(messages):
    trimmed = trim_tool_messages(messages)   # Layer 1: 개별 트리밍
    windowed = trim_history(trimmed)         # Layer 2 + 3: 윈도우 + 총량
    return windowed
```

#### Layer 1: ToolMessage 개별 트리밍

```python
MAX_TOOL_RESULT_CHARS = 3000
```

각 ToolMessage의 content가 3,000자를 초과하면 잘라내고 마커 추가:
```
[...truncated: 원본 8,523자 중 3,000자만 표시]
```

#### Layer 2: 메시지 수 윈도우

```python
MAX_MESSAGES = 12
```

12건 초과 시 오래된 것부터 제거. 단, 첫 AIMessage(tool_calls)는 보존.

#### Layer 3: 총 문자 수 제한

```python
MAX_TOTAL_CHARS = 30000
```

30,000자 초과 시 가장 긴 ToolMessage부터 절반으로 축소 (반복).

---

## 디버깅 가이드

### 트레이스 파일 활용

```bash
# 최근 트레이스 확인
ls -lt traces/ | head -5

# 트레이스 내용 확인 (Markdown이므로 IDE에서 프리뷰 권장)
cat traces/trace_20260312_143001.md
```

트레이스 파일에서 확인할 수 있는 것:
- **Step 1**: 키워드 매칭 결과 + LLM 의도 판단
- **Step 2**: ReAct Agent가 호출한 Tool + 결과 + 최종 응답
- **Step 3**: ResponseNode에서 추출한 final_answer
- **State Snapshot**: 각 단계의 전체 상태

### 의도 분류 오류 디버깅

```
🔧 질문> [질문 입력]

# 트레이스에서 확인:
## Step 1: IntentAgent (키워드+LLM 의도분석)
### 키워드 매칭
- 매칭된 힌트: ['...']   ← 키워드가 맞는지 확인
### 🔶 FM 출력
- raw: `load_rate_query`  ← LLM이 뭘로 판단했는지 확인
```

**해결 방법**:
1. `INTENT_KEYWORDS`에 누락된 키워드 추가
2. `INTENT_SYSTEM_PROMPT`에 의도 설명 보강
3. 키워드가 여러 의도에 겹치면 LLM이 문맥으로 판단 (프롬프트 조정)

### Tool 선택 오류 디버깅

```
## Step 2: ReAct Agent (정보조회 + 도구 호출)
### ReAct Agent 실행 로그
- **AIMessage** [tool_calls]: `get_load_rates(...)`  ← 맞는 Tool인지 확인
```

**해결 방법**:
1. Tool 함수의 docstring을 더 명확하게 작성 (LLM이 docstring을 읽음)
2. `INFO_SYSTEM_PROMPT`의 도구 선택 가이드 보강
3. disambiguation 규칙 추가

### SQL 오류 디버깅

```python
# 템플릿 렌더링 결과 확인
from tools.template_engine import render_sql
sql, params = render_sql("template_name.sql", equipment_type="CONVEYOR")
print(sql)
print(params)

# 직접 쿼리 실행
from db.connection import query
rows = query(sql, params)
print(rows)
```

### ReAct Agent 무한 루프

`recursion_limit=10`으로 제한되어 있지만, Tool이 계속 호출되는 경우:
1. `INFO_SYSTEM_PROMPT`에 "충분한 정보가 모이면 즉시 응답" 규칙 확인
2. Tool 결과가 비어있으면 LLM이 계속 시도할 수 있음 → "데이터 없음" 메시지 명시
3. `recursion_limit`을 낮춰서 강제 중단

---

## 성능 튜닝

### LLM 호출 최적화

| 설정 | 기본값 | 조정 방향 |
|------|--------|-----------|
| `LLM_TEMPERATURE` | 0 | 의도분석/Tool 선택은 0 유지, 일반대화는 0.7 |
| `recursion_limit` | 10 | 단순 질문이 많으면 낮추기 (5~7) |
| `MAX_TOOL_RESULT_CHARS` | 3000 | 데이터가 크면 올리기 (5000), 비용 절감하려면 낮추기 |

### 커넥션 풀 최적화

| 설정 | 기본값 | 조정 방향 |
|------|--------|-----------|
| `DB_POOL_SIZE` | 5 | CLI: 2~3, 서버: 10~20 |

### 응답 속도 개선

1. **Gemini 모델 선택**: `gemini-2.0-flash`는 속도/비용 최적 (Lite는 Tool Calling 미지원 주의)
2. **키워드 매칭**: 명확한 키워드면 LLM 확인만 하므로 빠름
3. **트리밍**: ToolMessage가 크면 트리밍으로 LLM 입력 토큰 절약

---

## 코드 패턴 레퍼런스

### Tool 함수 기본 패턴

```python
@tool
def get_something(param1: Optional[str] = None, param2: int = 24) -> str:
    """Tool 설명 — LLM이 이 docstring을 읽고 Tool을 선택합니다."""
    sql, params = render_sql("something.sql",
                             param1=param1 and param1.upper(),
                             param2=int(param2))
    rows = query(sql, params)
    return json.dumps(rows, ensure_ascii=False)
```

### 다중 쿼리 Tool 패턴

```python
@tool
def get_detail(item_id: str) -> str:
    """상세 정보 — 기본 정보 + 이력 + 관련 데이터."""
    iid = item_id.upper()
    params = {"item_id": iid}

    sql_i, _ = render_sql("item_info.sql", item_id=iid)
    sql_h, _ = render_sql("item_history.sql", item_id=iid)

    info = query(sql_i, params)
    history = query(sql_h, params)
    return json.dumps({"info": info, "history": history}, ensure_ascii=False)
```

### 키워드 매칭 패턴

```python
INTENT_KEYWORDS = {
    "intent_name": ["한글키워드", "영문키워드", "동의어"],
}

def _match_keywords(user_input: str) -> list[str]:
    text = user_input.upper()
    return [intent for intent, keywords in INTENT_KEYWORDS.items()
            if any(kw.upper() in text for kw in keywords)]
```

### Jinja2 조건부 렌더링 패턴

```sql
-- 값 바인딩 (문자열)
{% if param %}
AND column = :param
{% endif %}

-- 직접 렌더링 (정수)
WHERE time >= datetime('now', '-{{ hours }} hours')

-- 조건부 JOIN
{% if include_extra %}
JOIN extra_table et ON main.id = et.main_id
{% endif %}

-- 조건부 컬럼
SELECT a.col1
{% if show_extra %}, b.col2{% endif %}
FROM ...
```
