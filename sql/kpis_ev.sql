-- EV KPI (table: ev)

-- KPI 1 : Nombre de modèles par marque
SELECT
  brand,
  COUNT(*) AS nb_models
FROM ev
WHERE brand IS NOT NULL
GROUP BY brand
ORDER BY nb_models DESC;

-- KPI 2 : Autonomie moyenne par marque
SELECT
  brand,
  AVG(range_km) AS avg_range_km
FROM ev
WHERE brand IS NOT NULL AND range_km IS NOT NULL
GROUP BY brand
ORDER BY avg_range_km DESC;

-- KPI 3 : Batterie moyenne (kWh) par segment
SELECT
  segment,
  AVG(battery_capacity_kWh) AS avg_battery_kWh
FROM ev
WHERE segment IS NOT NULL AND battery_capacity_kWh IS NOT NULL
GROUP BY segment
ORDER BY avg_battery_kWh DESC;

-- KPI 4 : Top 10 autonomies (marque + modèle)
SELECT
  brand,
  model,
  range_km
FROM ev
WHERE range_km IS NOT NULL
ORDER BY range_km DESC
LIMIT 10;
