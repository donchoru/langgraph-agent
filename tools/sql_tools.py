"""SQL Tool 함수 10개 — @tool 데코레이터 + Jinja2 템플릿."""
import json
from typing import Optional
from langchain_core.tools import tool
from db.connection import query
from tools.template_engine import render_sql


@tool
def get_equipment_list(equipment_type: Optional[str] = None, line: Optional[str] = None, zone: Optional[str] = None) -> str:
    """장비 목록 조회. 유형(CONVEYOR/AGV/CRANE/SORTER/STACKER/SHUTTLE), 라인(L1/L2/L3), 구간(TFT/CELL/MODULE/PACK) 필터 가능."""
    sql, params = render_sql("equipment_list.sql",
                             equipment_type=equipment_type and equipment_type.upper(),
                             line=line and line.upper(),
                             zone=zone and zone.upper())
    rows = query(sql, params)
    return json.dumps(rows, ensure_ascii=False)


@tool
def get_equipment_status(equipment_type: Optional[str] = None, line: Optional[str] = None) -> str:
    """장비 상태 현황 — 상태(RUNNING/IDLE/MAINTENANCE/ERROR)별 집계 + 목록."""
    et = equipment_type and equipment_type.upper()
    ln = line and line.upper()

    sql_s, params_s = render_sql("equipment_status_summary.sql", equipment_type=et, line=ln)
    sql_d, params_d = render_sql("equipment_status_detail.sql", equipment_type=et, line=ln)

    summary = query(sql_s, params_s)
    detail = query(sql_d, params_d)
    return json.dumps({"summary": summary, "equipment": detail}, ensure_ascii=False)


@tool
def get_load_rates(equipment_type: Optional[str] = None, line: Optional[str] = None, zone: Optional[str] = None, hours: int = 1) -> str:
    """부하율 조회 — 최근 N시간 (기본 1시간). 장비 유형/라인/구간 필터 가능."""
    sql, params = render_sql("load_rates.sql",
                             hours=int(hours),
                             equipment_type=equipment_type and equipment_type.upper(),
                             line=line and line.upper(),
                             zone=zone and zone.upper())
    rows = query(sql, params)
    return json.dumps(rows, ensure_ascii=False)


@tool
def get_overloaded_equipment(threshold_pct: Optional[float] = None) -> str:
    """과부하 장비 조회 — 최근 1시간 내 임계값(alert_threshold) 이상인 장비. threshold_pct > 0이면 해당 값 기준, 아니면 장비 유형별 임계값 기준."""
    use_threshold = threshold_pct is not None and threshold_pct > 0
    sql, params = render_sql("overloaded.sql",
                             use_threshold=use_threshold,
                             threshold_pct=threshold_pct if use_threshold else None)
    rows = query(sql, params)
    return json.dumps(rows, ensure_ascii=False)


@tool
def get_equipment_detail(equipment_id: str) -> str:
    """특정 장비 상세 정보 + 최근 부하율 이력 (24건)."""
    eid = equipment_id.upper()
    params = {"equipment_id": eid}

    sql_i, _ = render_sql("equipment_info.sql", equipment_id=eid)
    sql_h, _ = render_sql("equipment_load_history.sql", equipment_id=eid)
    sql_a, _ = render_sql("equipment_alert_history.sql", equipment_id=eid)

    equip = query(sql_i, params)
    history = query(sql_h, params)
    alerts = query(sql_a, params)
    return json.dumps(
        {"equipment": equip, "load_history": history, "recent_alerts": alerts},
        ensure_ascii=False,
    )


@tool
def get_recent_alerts(hours: int = 24, alert_type: Optional[str] = None) -> str:
    """최근 알림 이력 조회 — 기본 24시간. alert_type(WARNING/CRITICAL) 필터 가능."""
    sql, params = render_sql("recent_alerts.sql",
                             hours=int(hours),
                             alert_type=alert_type and alert_type.upper())
    rows = query(sql, params)
    return json.dumps(rows, ensure_ascii=False)


@tool
def get_zone_summary(line: Optional[str] = None) -> str:
    """구간(zone)별 부하율 요약 — 최근 1시간 평균/최대/최소. 라인 필터 가능."""
    sql, params = render_sql("zone_summary.sql", line=line and line.upper())
    rows = query(sql, params)
    return json.dumps(rows, ensure_ascii=False)


@tool
def get_lots_on_equipment(equipment_id: str) -> str:
    """설비에 현재 물리적으로 위치한 Lot 조회.
    ⚠ '설비의 Lot'이라는 질문에서 '현재 물리적으로 있는 Lot'을 의미할 때 사용.
    스케줄(예정)된 Lot을 보려면 get_lots_scheduled_for_equipment를 사용하세요."""
    sql, params = render_sql("lots_on_equipment.sql", equipment_id=equipment_id.upper())
    rows = query(sql, params)
    return json.dumps(rows, ensure_ascii=False)


@tool
def get_lots_scheduled_for_equipment(equipment_id: str) -> str:
    """설비에 예정(스케줄)된 Lot 조회.
    ⚠ '설비의 Lot'이라는 질문에서 '앞으로 처리할 예정인 Lot'을 의미할 때 사용.
    현재 물리적으로 있는 Lot을 보려면 get_lots_on_equipment를 사용하세요."""
    sql, params = render_sql("lots_scheduled.sql", equipment_id=equipment_id.upper())
    rows = query(sql, params)
    return json.dumps(rows, ensure_ascii=False)


@tool
def get_lot_detail(lot_id: str) -> str:
    """특정 Lot의 상세 정보 — 현재 위치, 상태, 스케줄 이력 전부 포함."""
    lid = lot_id.upper()
    params = {"lot_id": lid}

    sql_i, _ = render_sql("lot_info.sql", lot_id=lid)
    sql_s, _ = render_sql("lot_schedules.sql", lot_id=lid)

    lot_info = query(sql_i, params)
    schedules = query(sql_s, params)
    return json.dumps({"lot": lot_info, "schedules": schedules}, ensure_ascii=False)


ALL_TOOLS = [
    get_equipment_list,
    get_equipment_status,
    get_load_rates,
    get_overloaded_equipment,
    get_equipment_detail,
    get_recent_alerts,
    get_zone_summary,
    get_lots_on_equipment,
    get_lots_scheduled_for_equipment,
    get_lot_detail,
]
