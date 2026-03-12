SELECT ls.*, e.equipment_type, e.line, e.zone
FROM lot_schedule ls
JOIN equipment e ON ls.equipment_id = e.equipment_id
WHERE ls.lot_id = :lot_id
ORDER BY ls.scheduled_start
