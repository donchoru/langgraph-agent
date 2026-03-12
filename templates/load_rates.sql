SELECT e.equipment_id, e.equipment_type, e.line, e.zone, e.status,
       lr.recorded_at, lr.load_rate_pct, lr.throughput, lr.queue_length
FROM load_rate lr
JOIN equipment e ON lr.equipment_id = e.equipment_id
WHERE lr.recorded_at >= datetime('now', 'localtime', '-{{ hours }} hours')
{% if equipment_type %}
AND e.equipment_type = :equipment_type
{% endif %}
{% if line %}
AND e.line = :line
{% endif %}
{% if zone %}
AND e.zone = :zone
{% endif %}
ORDER BY lr.recorded_at DESC, e.equipment_id
