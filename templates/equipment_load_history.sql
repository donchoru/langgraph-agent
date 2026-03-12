SELECT recorded_at, load_rate_pct, throughput, queue_length
FROM load_rate
WHERE equipment_id = :equipment_id
ORDER BY recorded_at DESC LIMIT 24
