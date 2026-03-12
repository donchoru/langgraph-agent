SELECT e.line, e.zone,
       COUNT(DISTINCT e.equipment_id) as equipment_count,
       ROUND(AVG(lr.load_rate_pct), 1) as avg_load,
       ROUND(MAX(lr.load_rate_pct), 1) as max_load,
       ROUND(MIN(lr.load_rate_pct), 1) as min_load
FROM load_rate lr
JOIN equipment e ON lr.equipment_id = e.equipment_id
WHERE lr.recorded_at >= datetime('now', 'localtime', '-1 hours')
{% if line %}
AND e.line = :line
{% endif %}
GROUP BY e.line, e.zone
ORDER BY e.line, e.zone
