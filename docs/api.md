# ITA Scrapper API Documentation

## Table of Contents

- [Overview](#overview)
- [Core Classes](#core-classes)
- [Data Models](#data-models)
- [Utility Functions](#utility-functions)
- [Exception Handling](#exception-handling)
- [Configuration](#configuration)

## Overview

The ITA Scrapper library provides a comprehensive Python API for extracting flight information from travel booking websites. The library is built around a set of core classes that handle browser automation, data parsing, and result formatting.

### Key Components

- **ITAScrapper**: Main class for flight searches and browser automation
- **Data Models**: Pydantic models for type-safe flight data representation
- **Parsers**: Specialized parsers for extracting data from complex web interfaces
- **Utilities**: Helper functions for data processing and validation
- **Exceptions**: Comprehensive error handling for robust operation

## Core Classes

### ITAScrapper

The primary interface for all flight search operations.

```python
from ita_scrapper import ITAScrapper, CabinClass
from datetime import date

# Initialize with configuration
scrapper = ITAScrapper(
    headless=True,           # Run browser in background
    timeout=30000,           # 30 second timeout
    use_matrix=True,         # Use ITA Matrix (recommended)
    viewport_size=(1920, 1080)
)

# Recommended: Use as context manager
async with ITAScrapper() as scrapper:
    result = await scrapper.search_flights(
        origin="JFK",
        destination="LAX",
        departure_date=date(2024, 8, 15),
        return_date=date(2024, 8, 22),
        adults=2,
        cabin_class=CabinClass.BUSINESS
    )
```

#### Methods

##### `search_flights()`
Search for flights between two destinations.

**Parameters:**
- `origin` (str): Origin airport code (3-letter IATA)
- `destination` (str): Destination airport code (3-letter IATA)
- `departure_date` (date): Departure date
- `return_date` (Optional[date]): Return date for round-trip
- `cabin_class` (CabinClass): Service class preference
- `adults` (int): Number of adult passengers (1-9)
- `children` (int): Number of child passengers (0-8)
- `infants` (int): Number of infant passengers (0-4)
- `max_results` (int): Maximum flights to return

**Returns:**
`FlightResult` object containing list of flights and search metadata.

**Example:**
```python
# One-way search
result = await scrapper.search_flights(
    origin="NYC",
    destination="LON",
    departure_date=date(2024, 12, 15),
    adults=1,
    cabin_class=CabinClass.ECONOMY
)

print(f"Found {len(result.flights)} flights")
for flight in result.flights:
    print(f"${flight.price} - {flight.total_duration_minutes//60}h")
```

##### `get_price_calendar()`
Get flexible date pricing for a route.

**Parameters:**
- `origin` (str): Origin airport code
- `destination` (str): Destination airport code  
- `departure_month` (date): Month to get pricing for
- `cabin_class` (CabinClass): Service class

**Returns:**
`PriceCalendar` object with price entries for different dates.

**Example:**
```python
calendar = await scrapper.get_price_calendar(
    origin="JFK",
    destination="LAX",
    departure_month=date(2024, 8, 1),
    cabin_class=CabinClass.ECONOMY
)

cheapest_dates = calendar.get_cheapest_dates(limit=5)
for entry in cheapest_dates:
    print(f"{entry.date}: ${entry.price}")
```

##### `search_multi_city()`
Search for complex multi-city itineraries.

**Parameters:**
- `search_params` (MultiCitySearchParams): Multi-city trip configuration
- `max_results` (int): Maximum flights to return

**Returns:**
`FlightResult` object with multi-city flight options.

### ITAMatrixParser

Specialized parser for extracting data from ITA Matrix's Angular Material interface.

```python
from ita_scrapper.parsers import ITAMatrixParser

parser = ITAMatrixParser()
flights = await parser.parse_flight_results(page, max_results=10)
```

#### Methods

##### `parse_flight_results()`
Extract structured flight data from ITA Matrix results page.

**Parameters:**
- `page` (Page): Playwright page object on ITA Matrix results
- `max_results` (int): Maximum flights to parse

**Returns:**
List of `Flight` objects with comprehensive flight information.

## Data Models

All data models use Pydantic for validation and type safety.

### Flight

Represents a complete flight itinerary with pricing and service information.

```python
from ita_scrapper import Flight, FlightSegment, CabinClass
from decimal import Decimal

flight = Flight(
    segments=[segment1, segment2],  # List of flight segments
    price=Decimal("299.00"),        # Total price in USD
    cabin_class=CabinClass.ECONOMY, # Service class
    total_duration_minutes=480,     # Total journey time
    stops=1,                        # Number of connections
    is_refundable=False,           # Refund policy
    baggage_included=True          # Baggage inclusion
)

# Access properties
print(flight.departure_time)  # First segment departure
print(flight.arrival_time)    # Last segment arrival
print(flight.airlines)        # List of operating airlines
```

### FlightSegment

Individual flight leg from one airport to another.

```python
from ita_scrapper import FlightSegment, Airline, Airport
from datetime import datetime

segment = FlightSegment(
    airline=Airline(code="DL", name="Delta Air Lines"),
    flight_number="DL123",
    departure_airport=Airport(code="JFK", name="John F. Kennedy"),
    arrival_airport=Airport(code="LAX", name="Los Angeles International"),
    departure_time=datetime(2024, 8, 15, 8, 30),
    arrival_time=datetime(2024, 8, 15, 11, 45),
    duration_minutes=375,  # 6h 15m
    aircraft_type="Airbus A321",
    stops=0  # Nonstop
)
```

### SearchParams

Flight search configuration with validation.

```python
from ita_scrapper import SearchParams, CabinClass, TripType
from datetime import date

params = SearchParams(
    origin="JFK",
    destination="LAX", 
    departure_date=date(2024, 8, 15),
    return_date=date(2024, 8, 22),  # Optional for round-trip
    trip_type=TripType.ROUND_TRIP,  # Auto-determined
    cabin_class=CabinClass.BUSINESS,
    adults=2,
    children=1,
    infants=0
)

# Validation occurs at creation
# Raises ValidationError for invalid inputs
```

### FlightResult

Container for search results with analysis methods.

```python
result = FlightResult(
    flights=[flight1, flight2, flight3],
    search_params=params,
    total_results=25,
    currency="USD"
)

# Analysis methods
cheapest = result.cheapest_flight
fastest = result.fastest_flight

# Filter results
nonstop_flights = [f for f in result.flights if f.stops == 0]
business_flights = [f for f in result.flights 
                   if f.cabin_class == CabinClass.BUSINESS]
```

### Enums

#### CabinClass
Service class options with increasing service levels.

```python
from ita_scrapper import CabinClass

CabinClass.ECONOMY          # Standard economy
CabinClass.PREMIUM_ECONOMY  # Enhanced economy  
CabinClass.BUSINESS         # Business class
CabinClass.FIRST           # First class
```

#### TripType
Trip type enumeration.

```python
from ita_scrapper import TripType

TripType.ONE_WAY      # One-way flights
TripType.ROUND_TRIP   # Round-trip flights
TripType.MULTI_CITY   # Multi-city itineraries
```

## Utility Functions

### Price Parsing

```python
from ita_scrapper import parse_price
from decimal import Decimal

# Various formats supported
price1 = parse_price("$1,234.56")     # Decimal('1234.56')
price2 = parse_price("€1.234,56")     # Decimal('1234.56')
price3 = parse_price("1234.56 USD")   # Decimal('1234.56')
```

### Duration Parsing

```python
from ita_scrapper import parse_duration

# Multiple formats
duration1 = parse_duration("2h 30m")    # 150 minutes
duration2 = parse_duration("1:45")      # 105 minutes  
duration3 = parse_duration("90 minutes") # 90 minutes
```

### Time Parsing

```python
from ita_scrapper import parse_time
from datetime import date

# With reference date
time1 = parse_time("2:30 PM", ref_date=date(2024, 8, 15))
# Returns: datetime(2024, 8, 15, 14, 30)

# Handle next-day flights
time2 = parse_time("1:30 AM +1", ref_date=date(2024, 8, 15))
# Returns: datetime(2024, 8, 16, 1, 30)
```

### Airport Code Validation

```python
from ita_scrapper import validate_airport_code

# Normalizes and validates
code1 = validate_airport_code("jfk")    # "JFK"
code2 = validate_airport_code("KJFK")   # "KJFK" (ICAO)

# Raises ValidationError for invalid codes
try:
    validate_airport_code("12A")
except ValidationError as e:
    print(f"Invalid: {e}")
```

### Date Utilities

```python
from ita_scrapper import format_duration, get_date_range, is_valid_date_range
from datetime import date

# Format duration
formatted = format_duration(150)  # "2h 30m"

# Generate date ranges
dates = get_date_range(date(2024, 8, 15), 7)  # 7 days starting Aug 15

# Validate date ranges
valid = is_valid_date_range(date.today(), date.today() + timedelta(days=7))
```

## Exception Handling

Comprehensive exception hierarchy for robust error handling.

```python
from ita_scrapper import (
    ITAScrapperError,    # Base exception
    NavigationError,     # Website access issues
    ParseError,          # Data parsing failures
    ITATimeoutError,     # Operation timeouts
    ValidationError      # Input validation errors
)

try:
    async with ITAScrapper() as scrapper:
        result = await scrapper.search_flights("JFK", "LAX", date.today())
        
except NavigationError as e:
    print(f"Cannot access website: {e}")
    # Retry with different configuration or alert user
    
except ParseError as e:
    print(f"Cannot parse results: {e}")
    # Try alternative parsing or use cached data
    
except ITATimeoutError as e:
    print(f"Operation timed out: {e}")
    # Retry with longer timeout or reduced scope
    
except ValidationError as e:
    print(f"Invalid input: {e}")
    # Prompt user for correct input
    
except ITAScrapperError as e:
    print(f"General scrapping error: {e}")
    # General error handling
```

## Configuration

### Browser Configuration

```python
# Custom browser settings
scrapper = ITAScrapper(
    headless=False,              # Show browser for debugging
    timeout=60000,               # 60 second timeout
    viewport_size=(2560, 1440),  # High resolution
    user_agent="custom-agent",   # Custom user agent
    use_matrix=True              # Prefer ITA Matrix
)
```

### Performance Tuning

```python
# For high-volume operations
scrapper = ITAScrapper(
    headless=True,        # Faster execution
    timeout=45000,        # Reasonable timeout
    viewport_size=(1280, 720)  # Smaller viewport
)

# Search with limits
result = await scrapper.search_flights(
    origin="JFK",
    destination="LAX", 
    departure_date=date.today(),
    max_results=5  # Limit results for faster parsing
)
```

### Error Recovery

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def robust_search():
    async with ITAScrapper() as scrapper:
        return await scrapper.search_flights("JFK", "LAX", date.today())

# Automatically retries on failures with exponential backoff
result = await robust_search()
```

## Best Practices

### 1. Always Use Context Managers

```python
# ✅ Recommended
async with ITAScrapper() as scrapper:
    result = await scrapper.search_flights(...)

# ❌ Not recommended (manual cleanup required)
scrapper = ITAScrapper()
await scrapper.start()
try:
    result = await scrapper.search_flights(...)
finally:
    await scrapper.close()
```

### 2. Handle Exceptions Appropriately

```python
# ✅ Specific exception handling
try:
    result = await scrapper.search_flights(...)
except NavigationError:
    # Specific handling for access issues
    pass
except ParseError:
    # Specific handling for parsing issues
    pass

# ❌ Too broad exception handling
try:
    result = await scrapper.search_flights(...)
except Exception:
    # Loses specific error context
    pass
```

### 3. Validate Inputs Early

```python
# ✅ Validate before expensive operations
try:
    params = SearchParams(
        origin="JFK",
        destination="LAX",
        departure_date=date.today()
    )
    result = await scrapper.search_flights(**params.dict())
except ValidationError as e:
    print(f"Fix input: {e}")
    return

# ❌ Let validation happen during scraping
result = await scrapper.search_flights("INVALID", "LAX", date.today())
```

### 4. Use Appropriate Timeouts

```python
# ✅ Longer timeout for complex searches  
scrapper = ITAScrapper(timeout=60000)  # 1 minute

# ✅ Shorter timeout for simple operations
scrapper = ITAScrapper(timeout=30000)  # 30 seconds
```

### 5. Limit Result Scope

```python
# ✅ Reasonable result limits
result = await scrapper.search_flights(
    origin="JFK",
    destination="LAX",
    departure_date=date.today(),
    max_results=10  # Faster parsing
)

# ❌ Too many results slow down parsing
result = await scrapper.search_flights(..., max_results=100)
```