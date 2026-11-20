import pandas as pd

# Get the airport's code and coordinates from OurAirports
airports = pd.read_csv("https://davidmegginson.github.io/ourairports-data/airports.csv")
airport = airports[airports["iata_code"] == "JFK"].iloc[0]

# Build URL at https://open-meteo.com/en/docs/historical-weather-api
url = (
    "https://archive-api.open-meteo.com/v1/archive"
    f"?latitude={airport['latitude_deg']}&longitude={airport['longitude_deg']}"
    "&start_date=2025-01-01&end_date=2025-01-01"
    "&hourly=temperature_2m,precipitation,snowfall,wind_speed_10m,cloud_cover,weather_code"
    "&timezone=auto&format=csv"
)

weather = pd.read_csv(url, skiprows=3)  # first 3 lines are location info

# Transformations needed for joins later on
weather["time"] = pd.to_datetime(weather["time"])

print(weather.dtypes)  # schema: column names + data types
print(weather.head().to_string())  # first 5 rows
