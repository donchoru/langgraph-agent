SELECT l.lot_id, l.product_type, l.quantity, l.status,
       l.current_equipment_id, l.created_at, l.updated_at
FROM lot l
WHERE l.current_equipment_id = :equipment_id
  AND l.status IN ('IN_TRANSIT', 'IN_PROCESS')
ORDER BY l.updated_at DESC
