SELECT status, COUNT(*) as cnt FROM equipment
WHERE 1=1
{% if equipment_type %}
AND equipment_type = :equipment_type
{% endif %}
{% if line %}
AND line = :line
{% endif %}
GROUP BY status ORDER BY cnt DESC
