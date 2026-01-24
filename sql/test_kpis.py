import duckdb

con = duckdb.connect("data/project.db")

print("\n--- TEST KPI WALMART: total_sales ---")
print(con.execute("""
    SELECT SUM(CAST(REPLACE(Weekly_Sales, ',', '') AS DOUBLE)) AS total_sales
    FROM walmart
    WHERE Weekly_Sales IS NOT NULL;
""").fetchall())

print("\n--- TEST KPI EV: top 5 range ---")
print(con.execute("""
    SELECT brand, model, range_km
    FROM ev
    WHERE range_km IS NOT NULL
    ORDER BY range_km DESC
    LIMIT 5;
""").fetchall())

con.close()
print("\n Tests terminés")

