# Quick Start

## Basic Flight Search

```python
from ita_scrapper import ITAScrapper

# Initialize scrapper
scrapper = ITAScrapper()

# Simple search
results = scrapper.search_flights(
    origin="NYC",
    destination="LAX",
    departure_date="2024-03-15"
)

# Display results
for flight in results.flights:
    print(f"{flight.airline} {flight.flight_number}")
    print(f"Departure: {flight.departure_time}")
    print(f"Arrival: {flight.arrival_time}")
    print(f"Price: ${flight.price}")
    print("---")
```

## Advanced Search Options

```python
from ita_scrapper.models import SearchParams
from datetime import date

# Create detailed search parameters
params = SearchParams(
    origin="NYC",
    destination="LAX",
    departure_date=date(2024, 3, 15),
    return_date=date(2024, 3, 22),
    passengers=2,
    cabin_class="business",
    max_stops=1
)

results = scrapper.search_flights_with_params(params)
```

## Error Handling

```python
from ita_scrapper.exceptions import ITAScrapperException, NetworkError

try:
    results = scrapper.search_flights("NYC", "LAX", "2024-03-15")
except NetworkError as e:
    print(f"Network issue: {e}")
except ITAScrapperException as e:
    print(f"Scrapping error: {e}")
```

## Configuration

```python
from ita_scrapper.config import ScrapperConfig

# Custom configuration
config = ScrapperConfig(
    timeout=30,
    max_retries=3,
    headless=False,  # Show browser window
    user_agent="Custom User Agent"
)

scrapper = ITAScrapper(config=config)
```

## Next Steps

- See [Examples](examples.md) for more complex scenarios
- Read the [API Reference](../api.md) for complete documentation
- Check [Troubleshooting](../troubleshooting.md) if you encounter issues