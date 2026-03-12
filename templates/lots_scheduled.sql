SELECT ls.lot_id, l.product_type, l.quantity, l.status,
       l.current_equipment_id,
       ls.equipment_id AS scheduled_equipment_id,
       ls.scheduled_start, ls.scheduled_end,
       ls.actual_start, ls.actual_end
FROM lot_schedule ls
JOIN lot l ON ls.lot_id = l.lot_id
WHERE ls.equipment_id = :equipment_id
  AND ls.actual_end IS NULL
ORDER BY ls.scheduled_start
