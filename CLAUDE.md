# LangGraph Agent

물류 장비 관리 시스템 AI 에이전트 — LangGraph + Gemini + SQLite.
학습/포트폴리오용 프로젝트 (멀티에이전트, 의미 모호성 해소, FM I/O 트레이싱).

## 기술 스택
- Python 3.13 (3.14 미지원 — pydantic 호환성) / `.venv/`
- LangGraph (StateGraph)
- langchain-google-genai (Gemini 2.0 Flash)
- SQLite (logistics.db — `python -m db.seed`로 재생성)

## 아키텍처
```
사용자 → IntentAgent(의도분류) → InfoAgent(Tool선택) → ToolNode(SQL) → InfoAgent(응답생성) → ResponseAgent
                              ↘ general_chat은 직행 ↗
```

## 구조
```
main.py                     # 대화형 진입점 (멀티턴)
config.py                   # 환경 변수, 모델 설정
agents/
  state.py                  # AgentState (conversation_history 포함)
  prompts.py                # System 프롬프트 3종
  intent_agent.py           # IntentAgent + _build_context() + FM I/O
  info_agent.py             # InfoAgent + ResponseAgent + FM I/O
  message_trimmer.py        # 3계층 토큰 관리
graph/
  workflow.py               # StateGraph + 조건부 라우팅
tools/
  sql_tools.py              # @tool 10개 + ALL_TOOLS
db/
  schema.sql, connection.py, seed.py
examples/                   # 학습 예시 11건
snapshots/
  db_dump.py, traces_dump.py
```

## 의도 6개
equipment_status, load_rate_query, alert_check, overload_check, lot_query, general_chat

## SQL Tools 10개
1. get_equipment_list — 장비 목록
2. get_equipment_status — 장비 상태
3. get_load_rates — 부하율
4. get_overloaded_equipment — 과부하 장비
5. get_equipment_detail — 장비 상세
6. get_recent_alerts — 알림 이력
7. get_zone_summary — 구간별 요약
8. get_lots_on_equipment — 물리적 Lot
9. get_lots_scheduled_for_equipment — 스케줄 Lot
10. get_lot_detail — Lot 상세

## DB 테이블 6개
equipment(30), load_rate(720), alert_threshold(6), alert_history(~250), lot(40), lot_schedule(58)

## 핵심 패턴
- **멀티턴**: conversation_history (최근 10턴, `clear`로 초기화)
- **대명사 해소**: `_build_context()`가 이력을 FM 입력에 주입
- **의미 모호성 해소**: "Lot 뭐 있어?" → 2개 Tool 동시 호출
- **FM I/O 트레이싱**: 🔷 FM 입력 / 🔶 FM 출력
- **메시지 토큰 관리**: 3계층 트리밍

## 실행
```bash
python -m db.seed          # DB 재생성
python main.py             # 대화형 실행
python -m snapshots.db_dump       # DB 스냅샷
python -m snapshots.traces_dump   # 트레이스 스냅샷
```
