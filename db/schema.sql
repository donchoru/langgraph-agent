CREATE TABLE IF NOT EXISTS equipment (
    equipment_id   TEXT PRIMARY KEY,
    equipment_type TEXT NOT NULL,  -- CONVEYOR, AGV, CRANE, SORTER, STACKER, SHUTTLE
    line           TEXT NOT NULL,  -- L1, L2, L3
    zone           TEXT NOT NULL,  -- TFT, CELL, MODULE, PACK
    status         TEXT NOT NULL DEFAULT 'RUNNING',  -- RUNNING, IDLE, MAINTENANCE, ERROR
    installed_date TEXT NOT NULL,
    description    TEXT
);

CREATE TABLE IF NOT EXISTS load_rate (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id  TEXT NOT NULL REFERENCES equipment(equipment_id),
    recorded_at   TEXT NOT NULL,
    load_rate_pct REAL NOT NULL,
    throughput    INTEGER NOT NULL DEFAULT 0,
    queue_length  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS alert_threshold (
    equipment_type TEXT PRIMARY KEY,
    warning_pct    REAL NOT NULL DEFAULT 80.0,
    critical_pct   REAL NOT NULL DEFAULT 95.0
);

CREATE TABLE IF NOT EXISTS alert_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id TEXT NOT NULL REFERENCES equipment(equipment_id),
    alert_type   TEXT NOT NULL,  -- WARNING, CRITICAL
    load_rate_pct REAL NOT NULL,
    threshold_pct REAL NOT NULL,
    triggered_at TEXT NOT NULL,
    resolved_at  TEXT,
    message      TEXT
);

CREATE INDEX IF NOT EXISTS idx_load_rate_equip_time ON load_rate(equipment_id, recorded_at);
CREATE INDEX IF NOT EXISTS idx_alert_history_time ON alert_history(triggered_at);
