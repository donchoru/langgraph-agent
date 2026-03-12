SELECT e.equipment_id, e.equipment_type, e.line, e.zone, e.status,
       lr.recorded_at, lr.load_rate_pct
{% if not use_threshold %}
       , at.warning_pct, at.critical_pct
{% endif %}
FROM load_rate lr
JOIN equipment e ON lr.equipment_id = e.equipment_id
{% if not use_threshold %}
JOIN alert_threshold at ON e.equipment_type = at.equipment_type
{% endif %}
WHERE lr.recorded_at >= datetime('now', 'localtime', '-1 hours')
{% if use_threshold %}
AND lr.load_rate_pct >= :threshold_pct
{% else %}
AND lr.load_rate_pct >= at.warning_pct
{% endif %}
ORDER BY lr.load_rate_pct DESC
