SELECT alert_type, load_rate_pct, threshold_pct, triggered_at, message
FROM alert_history
WHERE equipment_id = :equipment_id
ORDER BY triggered_at DESC LIMIT 10
