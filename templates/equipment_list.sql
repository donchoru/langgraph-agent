SELECT * FROM equipment
WHERE 1=1
{% if equipment_type %}
AND equipment_type = :equipment_type
{% endif %}
{% if line %}
AND line = :line
{% endif %}
{% if zone %}
AND zone = :zone
{% endif %}
ORDER BY equipment_id
