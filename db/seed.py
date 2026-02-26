"""샘플 데이터 생성 — 장비 30대, 부하율 720건, 알림 이력."""
import random
from datetime import datetime, timedelta
from pathlib import Path
from db.connection import get_connection

SCHEMA_PATH = Path(__file__).parent / "schema.sql"

EQUIPMENT_TYPES = ["CONVEYOR", "AGV", "CRANE", "SORTER", "STACKER", "SHUTTLE"]
TYPE_PREFIX = {
    "CONVEYOR": "CVR", "AGV": "AGV", "CRANE": "CRN",
    "SORTER": "SRT", "STACKER": "STK", "SHUTTLE": "SHT",
}
LINES = ["L1", "L2", "L3"]
ZONES = ["TFT", "CELL", "MODULE", "PACK"]
STATUSES = ["RUNNING", "RUNNING", "RUNNING", "IDLE", "MAINTENANCE", "ERROR"]

THRESHOLDS = {
    "CONVEYOR": (80.0, 95.0),
    "AGV":      (75.0, 90.0),
    "CRANE":    (70.0, 85.0),
    "SORTER":   (80.0, 95.0),
    "STACKER":  (75.0, 90.0),
    "SHUTTLE":  (78.0, 92.0),
}


def seed():
    conn = get_connection()
    try:
        # 스키마 생성
        conn.executescript(SCHEMA_PATH.read_text())

        # 기존 데이터 삭제
        for table in ["alert_history", "load_rate", "alert_threshold", "equipment"]:
            conn.execute(f"DELETE FROM {table}")

        random.seed(42)
        now = datetime.now()

        # 장비 30대 생성
        equipments = []
        seq = {}
        for _ in range(30):
            etype = random.choice(EQUIPMENT_TYPES)
            line = random.choice(LINES)
            zone = random.choice(ZONES)
            key = (etype, line, zone)
            seq[key] = seq.get(key, 0) + 1
            eid = f"{TYPE_PREFIX[etype]}-{line}-{zone}-{seq[key]:02d}"
            status = random.choice(STATUSES)
            installed = (now - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d")
            equipments.append((eid, etype, line, zone, status, installed, f"{etype} {line}-{zone}"))

        conn.executemany(
            "INSERT INTO equipment VALUES (?,?,?,?,?,?,?)", equipments
        )

        # 임계값 설정
        for etype, (warn, crit) in THRESHOLDS.items():
            conn.execute(
                "INSERT INTO alert_threshold VALUES (?,?,?)", (etype, warn, crit)
            )

        # 부하율 720건 (장비당 24건 = 최근 4시간, 10분 간격)
        load_rows = []
        alert_rows = []
        for eid, etype, line, zone, status, _, _ in equipments:
            warn_pct, crit_pct = THRESHOLDS[etype]

            # 장비별 기본 부하율 범위 설정 (이상 시나리오 포함)
            if status == "ERROR":
                base, spread = 92.0, 8.0  # 높은 부하
            elif status == "MAINTENANCE":
                base, spread = 10.0, 5.0  # 낮은 부하
            elif status == "IDLE":
                base, spread = 5.0, 3.0
            else:
                base, spread = 55.0, 30.0  # RUNNING: 넓은 범위

            for i in range(24):
                ts = (now - timedelta(minutes=10 * (23 - i))).strftime("%Y-%m-%d %H:%M:%S")
                rate = max(0, min(100, base + random.uniform(-spread, spread)))
                throughput = int(rate * random.uniform(0.8, 1.2))
                queue = max(0, int((rate - 60) * random.uniform(0, 0.5))) if rate > 60 else 0

                load_rows.append((eid, ts, round(rate, 1), throughput, queue))

                # 알림 생성
                if rate >= crit_pct:
                    alert_rows.append((
                        eid, "CRITICAL", round(rate, 1), crit_pct, ts, None,
                        f"{eid} 부하율 {rate:.1f}% — 임계값 {crit_pct}% 초과"
                    ))
                elif rate >= warn_pct:
                    alert_rows.append((
                        eid, "WARNING", round(rate, 1), warn_pct, ts, None,
                        f"{eid} 부하율 {rate:.1f}% — 경고 {warn_pct}% 초과"
                    ))

        conn.executemany(
            "INSERT INTO load_rate (equipment_id, recorded_at, load_rate_pct, throughput, queue_length) VALUES (?,?,?,?,?)",
            load_rows,
        )
        conn.executemany(
            "INSERT INTO alert_history (equipment_id, alert_type, load_rate_pct, threshold_pct, triggered_at, resolved_at, message) VALUES (?,?,?,?,?,?,?)",
            alert_rows,
        )

        conn.commit()

        # 결과 요약
        eq_count = conn.execute("SELECT COUNT(*) FROM equipment").fetchone()[0]
        lr_count = conn.execute("SELECT COUNT(*) FROM load_rate").fetchone()[0]
        al_count = conn.execute("SELECT COUNT(*) FROM alert_history").fetchone()[0]
        print(f"Seed 완료: 장비 {eq_count}대, 부하율 {lr_count}건, 알림 {al_count}건")

    finally:
        conn.close()


if __name__ == "__main__":
    seed()
