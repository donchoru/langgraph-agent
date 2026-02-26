"""SQL Tool 함수 7개 — @tool 데코레이터."""
import json
from typing import Optional
from langchain_core.tools import tool
from db.connection import query


@tool
def get_equipment_list(equipment_type: Optional[str] = None, line: Optional[str] = None, zone: Optional[str] = None) -> str:
    """장비 목록 조회. 유형(CONVEYOR/AGV/CRANE/SORTER/STACKER/SHUTTLE), 라인(L1/L2/L3), 구간(TFT/CELL/MODULE/PACK) 필터 가능."""
    conditions, params = [], []
    if equipment_type:
        conditions.append("equipment_type = ?")
        params.append(equipment_type.upper())
    if line:
        conditions.append("line = ?")
        params.append(line.upper())
    if zone:
        conditions.append("zone = ?")
        params.append(zone.upper())
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    rows = query(f"SELECT * FROM equipment{where} ORDER BY equipment_id", tuple(params))
    return json.dumps(rows, ensure_ascii=False)


@tool
def get_equipment_status(equipment_type: Optional[str] = None, line: Optional[str] = None) -> str:
    """장비 상태 현황 — 상태(RUNNING/IDLE/MAINTENANCE/ERROR)별 집계 + 목록."""
    conditions, params = [], []
    if equipment_type:
        conditions.append("equipment_type = ?")
        params.append(equipment_type.upper())
    if line:
        conditions.append("line = ?")
        params.append(line.upper())
    where = " WHERE " + " AND ".join(conditions) if conditions else ""

    summary = query(
        f"SELECT status, COUNT(*) as cnt FROM equipment{where} GROUP BY status ORDER BY cnt DESC",
        tuple(params),
    )
    detail = query(
        f"SELECT equipment_id, equipment_type, line, zone, status FROM equipment{where} ORDER BY status, equipment_id",
        tuple(params),
    )
    return json.dumps({"summary": summary, "equipment": detail}, ensure_ascii=False)


@tool
def get_load_rates(equipment_type: Optional[str] = None, line: Optional[str] = None, zone: Optional[str] = None, hours: int = 1) -> str:
    """부하율 조회 — 최근 N시간 (기본 1시간). 장비 유형/라인/구간 필터 가능."""
    conditions = [f"lr.recorded_at >= datetime('now', 'localtime', '-{int(hours)} hours')"]
    params = []
    if equipment_type:
        conditions.append("e.equipment_type = ?")
        params.append(equipment_type.upper())
    if line:
        conditions.append("e.line = ?")
        params.append(line.upper())
    if zone:
        conditions.append("e.zone = ?")
        params.append(zone.upper())
    where = " WHERE " + " AND ".join(conditions)
    rows = query(
        f"""SELECT e.equipment_id, e.equipment_type, e.line, e.zone, e.status,
                   lr.recorded_at, lr.load_rate_pct, lr.throughput, lr.queue_length
            FROM load_rate lr
            JOIN equipment e ON lr.equipment_id = e.equipment_id
            {where}
            ORDER BY lr.recorded_at DESC, e.equipment_id""",
        tuple(params),
    )
    return json.dumps(rows, ensure_ascii=False)


@tool
def get_overloaded_equipment(threshold_pct: Optional[float] = None) -> str:
    """과부하 장비 조회 — 최근 1시간 내 임계값(alert_threshold) 이상인 장비. threshold_pct > 0이면 해당 값 기준, 아니면 장비 유형별 임계값 기준."""
    if threshold_pct is not None and threshold_pct > 0:
        rows = query(
            """SELECT e.equipment_id, e.equipment_type, e.line, e.zone, e.status,
                      lr.recorded_at, lr.load_rate_pct
               FROM load_rate lr
               JOIN equipment e ON lr.equipment_id = e.equipment_id
               WHERE lr.load_rate_pct >= ?
                 AND lr.recorded_at >= datetime('now', 'localtime', '-1 hours')
               ORDER BY lr.load_rate_pct DESC""",
            (threshold_pct,),
        )
    else:
        rows = query(
            """SELECT e.equipment_id, e.equipment_type, e.line, e.zone, e.status,
                      lr.recorded_at, lr.load_rate_pct, at.warning_pct, at.critical_pct
               FROM load_rate lr
               JOIN equipment e ON lr.equipment_id = e.equipment_id
               JOIN alert_threshold at ON e.equipment_type = at.equipment_type
               WHERE lr.load_rate_pct >= at.warning_pct
                 AND lr.recorded_at >= datetime('now', 'localtime', '-1 hours')
               ORDER BY lr.load_rate_pct DESC""",
        )
    return json.dumps(rows, ensure_ascii=False)


@tool
def get_equipment_detail(equipment_id: str) -> str:
    """특정 장비 상세 정보 + 최근 부하율 이력 (24건)."""
    equip = query("SELECT * FROM equipment WHERE equipment_id = ?", (equipment_id.upper(),))
    history = query(
        """SELECT recorded_at, load_rate_pct, throughput, queue_length
           FROM load_rate WHERE equipment_id = ?
           ORDER BY recorded_at DESC LIMIT 24""",
        (equipment_id.upper(),),
    )
    alerts = query(
        """SELECT alert_type, load_rate_pct, threshold_pct, triggered_at, message
           FROM alert_history WHERE equipment_id = ?
           ORDER BY triggered_at DESC LIMIT 10""",
        (equipment_id.upper(),),
    )
    return json.dumps(
        {"equipment": equip, "load_history": history, "recent_alerts": alerts},
        ensure_ascii=False,
    )


@tool
def get_recent_alerts(hours: int = 24, alert_type: Optional[str] = None) -> str:
    """최근 알림 이력 조회 — 기본 24시간. alert_type(WARNING/CRITICAL) 필터 가능."""
    conditions = [f"triggered_at >= datetime('now', 'localtime', '-{int(hours)} hours')"]
    params = []
    if alert_type:
        conditions.append("alert_type = ?")
        params.append(alert_type.upper())
    where = " WHERE " + " AND ".join(conditions)
    rows = query(
        f"""SELECT ah.*, e.equipment_type, e.line, e.zone
            FROM alert_history ah
            JOIN equipment e ON ah.equipment_id = e.equipment_id
            {where}
            ORDER BY triggered_at DESC""",
        tuple(params),
    )
    return json.dumps(rows, ensure_ascii=False)


@tool
def get_zone_summary(line: Optional[str] = None) -> str:
    """구간(zone)별 부하율 요약 — 최근 1시간 평균/최대/최소. 라인 필터 가능."""
    conditions = ["lr.recorded_at >= datetime('now', 'localtime', '-1 hours')"]
    params = []
    if line:
        conditions.append("e.line = ?")
        params.append(line.upper())
    where = " WHERE " + " AND ".join(conditions)
    rows = query(
        f"""SELECT e.line, e.zone,
                   COUNT(DISTINCT e.equipment_id) as equipment_count,
                   ROUND(AVG(lr.load_rate_pct), 1) as avg_load,
                   ROUND(MAX(lr.load_rate_pct), 1) as max_load,
                   ROUND(MIN(lr.load_rate_pct), 1) as min_load
            FROM load_rate lr
            JOIN equipment e ON lr.equipment_id = e.equipment_id
            {where}
            GROUP BY e.line, e.zone
            ORDER BY e.line, e.zone""",
        tuple(params),
    )
    return json.dumps(rows, ensure_ascii=False)


ALL_TOOLS = [
    get_equipment_list,
    get_equipment_status,
    get_load_rates,
    get_overloaded_equipment,
    get_equipment_detail,
    get_recent_alerts,
    get_zone_summary,
]
