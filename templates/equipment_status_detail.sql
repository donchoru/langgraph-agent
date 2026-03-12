SELECT equipment_id, equipment_type, line, zone, status FROM equipment
WHERE 1=1
{% if equipment_type %}
AND equipment_type = :equipment_type
{% endif %}
{% if line %}
AND line = :line
{% endif %}
ORDER BY status, equipment_id
