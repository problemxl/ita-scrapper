# Examples

## Multi-City Trips

```python
from ita_scrapper import ITAScrapper
from ita_scrapper.models import SearchParams

scrapper = ITAScrapper()

# NYC → LAX → SFO → NYC
params = SearchParams(
    origin="NYC",
    destination="LAX",
    departure_date="2024-03-15",
    intermediate_stops=["SFO"],
    return_date="2024-03-25"
)

results = scrapper.search_flights_with_params(params)
```

## Date Range Search

```python
from datetime import date, timedelta

# Search flexible dates (±3 days)
flexible_params = SearchParams(
    origin="NYC",
    destination="LAX",
    departure_date=date(2024, 3, 15),
    date_flexibility=3  # ±3 days
)

results = scrapper.search_flights_with_params(flexible_params)
```

## Group Travel

```python
# Family trip with mixed cabin classes
family_params = SearchParams(
    origin="NYC",
    destination="Orlando",
    departure_date="2024-07-01",
    return_date="2024-07-08",
    passengers=4,
    cabin_class="economy",
    children=2,
    infants=0
)

results = scrapper.search_flights_with_params(family_params)
```

## Filtering Results

```python
# Search and filter results
results = scrapper.search_flights("NYC", "LAX", "2024-03-15")

# Filter by price
cheap_flights = [f for f in results.flights if f.price < 500]

# Filter by airline
delta_flights = [f for f in results.flights if "Delta" in f.airline]

# Filter by stops
direct_flights = [f for f in results.flights if f.stops == 0]
```

## Custom Parsing

```python
from ita_scrapper.parsers import ITAMatrixParser

# Custom parser with enhanced extraction
parser = ITAMatrixParser(
    extract_seat_availability=True,
    extract_baggage_info=True,
    extract_amenities=True
)

scrapper = ITAScrapper(parser=parser)
results = scrapper.search_flights("NYC", "LAX", "2024-03-15")

# Access enhanced data
for flight in results.flights:
    if hasattr(flight, 'seat_availability'):
        print(f"Seats available: {flight.seat_availability}")
```

## Batch Processing

```python
import asyncio
from typing import List

async def search_multiple_routes():
    scrapper = ITAScrapper()
    
    routes = [
        ("NYC", "LAX"),
        ("NYC", "SFO"),
        ("NYC", "SEA"),
        ("NYC", "MIA")
    ]
    
    tasks = []
    for origin, dest in routes:
        task = scrapper.search_flights_async(origin, dest, "2024-03-15")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

# Run batch search
all_results = asyncio.run(search_multiple_routes())
```

## Real-time Monitoring

```python
import time
from datetime import datetime

def monitor_price_changes(origin: str, destination: str, date: str, 
                         target_price: float, check_interval: int = 3600):
    """Monitor flight prices and alert when target price is reached."""
    
    scrapper = ITAScrapper()
    
    while True:
        try:
            results = scrapper.search_flights(origin, destination, date)
            lowest_price = min(f.price for f in results.flights)
            
            print(f"[{datetime.now()}] Lowest price: ${lowest_price}")
            
            if lowest_price <= target_price:
                print(f"🎉 Target price reached! Found flights for ${lowest_price}")
                break
                
        except Exception as e:
            print(f"Error during monitoring: {e}")
        
        time.sleep(check_interval)

# Monitor NYC to LAX flights
monitor_price_changes("NYC", "LAX", "2024-03-15", 400.0)
```

## Integration with Travel APIs

```python
import requests
from ita_scrapper import ITAScrapper

def enrich_with_weather_data(flight_result):
    """Add weather information to flight results."""
    
    # Get weather for destination
    weather_api = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": flight_result.destination_city,
        "appid": "your_api_key",
        "units": "metric"
    }
    
    response = requests.get(weather_api, params=params)
    weather_data = response.json()
    
    # Add weather to flight data
    flight_result.destination_weather = {
        "temperature": weather_data["main"]["temp"],
        "description": weather_data["weather"][0]["description"],
        "humidity": weather_data["main"]["humidity"]
    }
    
    return flight_result

# Search flights and add weather data
scrapper = ITAScrapper()
results = scrapper.search_flights("NYC", "LAX", "2024-03-15")

enriched_results = [enrich_with_weather_data(flight) for flight in results.flights]
```