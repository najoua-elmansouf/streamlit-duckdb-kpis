
-- Walmart KPI
-- Weekly_Sales est VARCHAR, on le convertit en DOUBLE
-- On enlève au passage d'éventuelles virgules
-- Remplace() ne gêne pas si y'a pas de virgules.

-- KPI 1 : Total des ventes
SELECT
  SUM(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS total_sales
FROM walmart
WHERE Weekly_Sales IS NOT NULL;

-- KPI 2 : Ventes par magasin (Store_Number)
SELECT
  Store_Number,
  SUM(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS total_sales
FROM walmart
WHERE Weekly_Sales IS NOT NULL
GROUP BY Store_Number
ORDER BY total_sales DESC;

-- KPI 3 : Ventes jour férié vs non férié
SELECT
  Holiday_Flag,
  SUM(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS total_sales,
  AVG(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS avg_weekly_sales
FROM walmart
WHERE Weekly_Sales IS NOT NULL
GROUP BY Holiday_Flag
ORDER BY Holiday_Flag;

-- KPI 4 : Évolution des ventes dans le temps (par date)
SELECT
  Date,
  SUM(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS total_sales
FROM walmart
WHERE Weekly_Sales IS NOT NULL
GROUP BY Date
ORDER BY Date;
