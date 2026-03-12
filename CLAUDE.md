# LangGraph Agent

물류 장비 관리 시스템 AI 에이전트 — LangGraph + Gemini + SQLite.
학습/포트폴리오용 프로젝트 (멀티에이전트, 의미 모호성 해소, FM I/O 트레이싱).

## 기술 스택
- Python 3.13 (3.14 미지원 — pydantic 호환성) / `.venv/`
- LangGraph (StateGraph + `create_react_agent`)
- langchain-google-genai (Gemini 2.0 Flash)
- SQLite (logistics.db — `python -m db.seed`로 재생성)
- Jinja2 (SQL 템플릿 엔진)

## 아키텍처
```
사용자 → IntentNode(키워드+LLM) → ReAct Agent(create_react_agent + Tools) → ResponseNode
                                ↘ general_chat은 직행 → ResponseNode
```

## 구조
```
main.py                     # 대화형 진입점 (멀티턴)
config.py                   # 환경 변수, 모델 설정
llm_factory.py              # Gemini / OpenAI 호환 LLM 팩토리
agents/
  state.py                  # AgentState (conversation_history 포함)
  prompts.py                # System 프롬프트 2종 (Intent + Info)
  intent_agent.py           # 키워드 매칭 + LLM 의도 판단
  info_agent.py             # create_react_agent 래퍼 + ResponseNode
  message_trimmer.py        # 3계층 토큰 관리
graph/
  workflow.py               # StateGraph + 조건부 라우팅
tools/
  sql_tools.py              # @tool 10개 + ALL_TOOLS (Jinja2 기반)
  template_engine.py        # Jinja2 SQL 렌더러
templates/                  # SQL 템플릿 14개
db/
  schema.sql, connection.py (커넥션 풀), seed.py
examples/                   # 학습 예시 12건
snapshots/
  db_dump.py, traces_dump.py
```

## 의도 분류 (키워드 + LLM)
- 키워드 매핑 테이블로 후보 추출 → LLM이 최종 판단
- 6개 의도: equipment_status, load_rate_query, alert_check, overload_check, lot_query, general_chat
- 대화 이력 기반 대명사 해소 유지 (`_build_context`)

## SQL Tools 10개 (Jinja2 템플릿)
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

## DB
- 테이블 6개: equipment(30), load_rate(720), alert_threshold(6), alert_history(~250), lot(40), lot_schedule(58)
- 커넥션 풀: `DB_POOL_SIZE` 환경변수 (기본 5)

## 핵심 패턴
- **create_react_agent**: LangGraph prebuilt — 도구 호출 루프 자동 처리
- **멀티턴**: conversation_history (최근 10턴, `clear`로 초기화)
- **대명사 해소**: `_build_context()`가 이력을 FM 입력에 주입
- **의미 모호성 해소**: "Lot 뭐 있어?" → 2개 Tool 동시 호출
- **FM I/O 트레이싱**: 🔷 FM 입력 / 🔶 FM 출력
- **메시지 토큰 관리**: 3계층 트리밍 (prompt callable로 적용)
- **Jinja2 SQL 템플릿**: SQL 구조는 Jinja2, 값은 :named_param 바인딩

## 실행
```bash
python -m db.seed          # DB 재생성
python main.py             # 대화형 실행
python -m snapshots.db_dump       # DB 스냅샷
python -m snapshots.traces_dump   # 트레이스 스냅샷
```
