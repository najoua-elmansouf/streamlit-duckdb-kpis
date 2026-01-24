# Colonnes utiles

## Table walmart
- Store / région = Store_Number (BIGINT)
- Date = Date (DATE)
- Ventes = Weekly_Sales (VARCHAR -> à convertir en DOUBLE)
- Jour férié = Holiday_Flag (BIGINT)
- Variables externes (option) :
  - Temperature (DOUBLE)
  - Fuel_Price (DOUBLE)
  - CPI (BIGINT)
  - Unemployment (DOUBLE)

## Table ev
- Marque = brand (VARCHAR)
- Modèle = model (VARCHAR)
- Autonomie = range_km (BIGINT)
- Segment = segment (VARCHAR)
- Carrosserie = car_body_type (VARCHAR)
- Batterie (kWh) = battery_capacity_kWh (DOUBLE)
- Transmission = drivetrain (VARCHAR)
- Sièges = seats (BIGINT)
- Accélération = acceleration_0_100_s (DOUBLE)
