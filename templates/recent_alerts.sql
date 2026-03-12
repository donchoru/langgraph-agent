SELECT ah.*, e.equipment_type, e.line, e.zone
FROM alert_history ah
JOIN equipment e ON ah.equipment_id = e.equipment_id
WHERE triggered_at >= datetime('now', 'localtime', '-{{ hours }} hours')
{% if alert_type %}
AND alert_type = :alert_type
{% endif %}
ORDER BY triggered_at DESC
