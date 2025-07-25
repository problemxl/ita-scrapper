"""
Pydantic data models for ITA Scrapper flight data structures.

This module defines the core data models used throughout the ITA Scrapper library
for representing flights, search parameters, results, and related entities. All models
use Pydantic for validation, serialization, and type safety.

The models are designed to handle the complex hierarchical structure of flight data
including multi-segment flights, various cabin classes, passenger configurations,
and pricing information. They provide both validation at creation time and convenient
access methods for common operations.

Key model categories:
- Flight Data: Flight, FlightSegment, Airport, Airline
- Search Configuration: SearchParams, MultiCitySearchParams
- Results: FlightResult, PriceCalendar
- Enums: TripType, CabinClass

All models support JSON serialization/deserialization and include comprehensive
validation rules to ensure data integrity.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class TripType(str, Enum):
    """
    Enumeration of supported trip types for flight searches.

    This enum defines the different types of trips that can be searched,
    affecting how the search form is filled and results are interpreted.

    Values:
        ROUND_TRIP: Round-trip flights with departure and return dates.
            Most common for leisure and business travel.
        ONE_WAY: One-way flights with only a departure date.
            Common for open-ended travel or one-way relocations.
        MULTI_CITY: Multi-city itineraries with multiple segments.
            For complex trips visiting multiple destinations.

    Example:
        >>> search_params = SearchParams(
        ...     origin="JFK",
        ...     destination="LAX",
        ...     departure_date=date.today(),
        ...     trip_type=TripType.ONE_WAY
        ... )
    """

    ROUND_TRIP = "round_trip"
    ONE_WAY = "one_way"
    MULTI_CITY = "multi_city"


class CabinClass(str, Enum):
    """
    Enumeration of airline cabin classes with increasing service levels.

    Defines the different service levels available on flights, affecting
    pricing, seat comfort, amenities, and baggage allowances. Each class
    typically offers progressively better service and higher prices.

    Values:
        ECONOMY: Standard economy class with basic service.
            Most affordable option with standard seats and limited amenities.
        PREMIUM_ECONOMY: Enhanced economy with better seats and service.
            More legroom, better meals, priority boarding.
        BUSINESS: Business class with significant upgrades.
            Lie-flat seats on long-haul, priority check-in, lounge access.
        FIRST: First class with premium service and amenities.
            Private suites on some airlines, dedicated cabin crew, gourmet dining.

    Note:
        Not all flights offer all cabin classes. Availability varies by
        airline, aircraft type, and route. Premium classes may be limited
        on shorter domestic flights.

    Example:
        >>> # Search for business class flights
        >>> result = await scrapper.search_flights(
        ...     origin="NYC",
        ...     destination="LON",
        ...     departure_date=date.today(),
        ...     cabin_class=CabinClass.BUSINESS
        ... )
    """

    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class Airport(BaseModel):
    """
    Represents an airport with IATA code and optional location information.

    Stores airport identification and location data used in flight segments
    and search parameters. The IATA code is the primary identifier, with
    additional fields for human-readable location information.

    Attributes:
        code: Three-letter IATA airport code (required). Automatically
            converted to uppercase for consistency. Examples: "JFK", "LAX", "LHR"
        name: Full airport name (optional). Examples: "John F. Kennedy International"
        city: City where airport is located (optional). Examples: "New York", "Los Angeles"
        country: Country where airport is located (optional). Examples: "United States", "UK"

    Validation:
        - Airport code must be exactly 3 letters
        - Code is automatically converted to uppercase

    Example:
        >>> airport = Airport(code="jfk", name="John F. Kennedy International",
        ...                  city="New York", country="United States")
        >>> print(airport.code)  # "JFK"

        >>> # Minimal airport with just code
        >>> origin = Airport(code="lax")
        >>> print(origin.code)  # "LAX"
    """

    code: str = Field(..., description="3-letter IATA airport code")
    name: Optional[str] = Field(None, description="Full airport name")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country name")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        """Validate that airport code is exactly 3 letters and convert to uppercase."""
        if len(v) != 3:
            raise ValueError("Airport code must be 3 letters")
        return v.upper()


class Airline(BaseModel):
    """
    Represents an airline with IATA code and optional name.

    Stores airline identification used in flight segments to track which
    airlines operate different parts of a journey. Used for filtering,
    display, and analysis of flight options.

    Attributes:
        code: Two-letter IATA airline code (required). Examples: "DL" (Delta),
            "AA" (American), "BA" (British Airways), "LH" (Lufthansa)
        name: Full airline name (optional). Examples: "Delta Air Lines",
            "American Airlines", "British Airways"

    Example:
        >>> airline = Airline(code="DL", name="Delta Air Lines")
        >>> print(f"{airline.name} ({airline.code})")  # "Delta Air Lines (DL)"

        >>> # Minimal airline with just code
        >>> carrier = Airline(code="AA")
        >>> print(carrier.code)  # "AA"
    """

    code: str = Field(..., description="2-letter IATA airline code")
    name: Optional[str] = Field(None, description="Full airline name")


class FlightSegment(BaseModel):
    """
    Represents a single flight segment (one takeoff and landing).

    A flight segment is the basic unit of air travel, representing a single
    flight from one airport to another. Complex journeys may consist of
    multiple segments with connections. This model captures all the essential
    information about one leg of a journey.

    Attributes:
        airline: Airline operating this segment
        flight_number: Airline's flight number (e.g., "DL1234", "AA567")
        departure_airport: Airport where segment begins
        arrival_airport: Airport where segment ends
        departure_time: Scheduled departure time (timezone-aware datetime)
        arrival_time: Scheduled arrival time (timezone-aware datetime)
        duration_minutes: Flight duration in minutes (gate to gate)
        aircraft_type: Aircraft model (optional). Examples: "Boeing 737", "Airbus A320"
        stops: Number of intermediate stops (0 for nonstop)

    Note:
        - Times should include timezone information when available
        - Duration includes taxi time but not layover time between segments
        - Stops > 0 indicates technical stops without plane changes

    Example:
        >>> segment = FlightSegment(
        ...     airline=Airline(code="DL", name="Delta Air Lines"),
        ...     flight_number="DL123",
        ...     departure_airport=Airport(code="JFK"),
        ...     arrival_airport=Airport(code="LAX"),
        ...     departure_time=datetime(2024, 8, 15, 8, 30),
        ...     arrival_time=datetime(2024, 8, 15, 11, 45),
        ...     duration_minutes=375,  # 6h 15m
        ...     aircraft_type="Airbus A321",
        ...     stops=0
        ... )
    """

    airline: Airline
    flight_number: str
    departure_airport: Airport
    arrival_airport: Airport
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    aircraft_type: Optional[str] = None
    stops: int = Field(0, description="Number of stops")


class Flight(BaseModel):
    """
    Represents a complete flight itinerary with pricing and service information.

    A flight represents a complete journey from origin to destination, which may
    consist of one or more segments (for connections). This is the primary unit
    returned by flight searches and includes all information needed for booking
    decisions including pricing, duration, and service details.

    Attributes:
        segments: List of flight segments making up this journey. Single segment
            for nonstop flights, multiple segments for flights with connections
        price: Total price in USD (Decimal for precise financial calculations)
        cabin_class: Service class for the entire journey
        total_duration_minutes: Total journey time including layovers
        stops: Total number of stops (connections) in the journey
        is_refundable: Whether the fare allows refunds (usually premium fares)
        baggage_included: Whether checked baggage is included in the price

    Properties:
        departure_time: Departure time of first segment
        arrival_time: Arrival time of last segment
        airlines: List of unique airline codes operating segments

    Note:
        - Price represents the total cost for all passengers and segments
        - Total duration includes layover time between segments
        - Baggage inclusion varies by airline and fare type

    Example:
        >>> # Nonstop flight
        >>> flight = Flight(
        ...     segments=[nonstop_segment],
        ...     price=Decimal("299.00"),
        ...     cabin_class=CabinClass.ECONOMY,
        ...     total_duration_minutes=375,
        ...     stops=0,
        ...     is_refundable=False,
        ...     baggage_included=False
        ... )
        >>> print(f"${flight.price} - {flight.total_duration_minutes//60}h")

        >>> # Multi-segment flight with connection
        >>> flight = Flight(
        ...     segments=[first_segment, second_segment],
        ...     price=Decimal("456.00"),
        ...     cabin_class=CabinClass.BUSINESS,
        ...     total_duration_minutes=720,  # Includes layover
        ...     stops=1,
        ...     is_refundable=True,
        ...     baggage_included=True
        ... )
    """

    segments: list[FlightSegment]
    price: Decimal = Field(..., description="Total price in USD")
    cabin_class: CabinClass
    total_duration_minutes: int
    stops: int = Field(0, description="Total number of stops")
    is_refundable: bool = False
    baggage_included: bool = False

    @property
    def departure_time(self) -> datetime:
        """Get departure time of first segment."""
        return self.segments[0].departure_time

    @property
    def arrival_time(self) -> datetime:
        """Get arrival time of last segment."""
        return self.segments[-1].arrival_time

    @property
    def airlines(self) -> list[str]:
        """Get list of unique airline codes operating this flight."""
        return list({segment.airline.code for segment in self.segments})


class SearchParams(BaseModel):
    """
    Comprehensive flight search parameters with validation.

    Defines all parameters needed to perform a flight search, including
    origin/destination, dates, passenger counts, and service preferences.
    Includes extensive validation to ensure search parameters are logical
    and compatible with booking site requirements.

    Attributes:
        origin: Origin airport code (3-letter IATA). Automatically uppercased
        destination: Destination airport code (3-letter IATA). Automatically uppercased
        departure_date: Date of departure. Must be today or future
        return_date: Return date for round-trip flights. Must be after departure
        trip_type: Type of trip (automatically set based on return_date)
        cabin_class: Preferred service class (affects pricing and availability)
        adults: Number of adult passengers (18+), range 1-9
        children: Number of child passengers (2-17), range 0-8
        infants: Number of infant passengers (<2), range 0-4

    Validation Rules:
        - Airport codes must be exactly 3 letters
        - At least 1 adult passenger required
        - Return date must be after departure date for round trips
        - Total passengers limited by airline policies
        - Trip type automatically determined by presence of return date

    Example:
        One-way search:
        >>> params = SearchParams(
        ...     origin="JFK",
        ...     destination="LAX",
        ...     departure_date=date(2024, 8, 15),
        ...     adults=2,
        ...     cabin_class=CabinClass.BUSINESS
        ... )
        >>> print(params.trip_type)  # TripType.ONE_WAY

        Round-trip family search:
        >>> params = SearchParams(
        ...     origin="NYC",
        ...     destination="LON",
        ...     departure_date=date(2024, 12, 20),
        ...     return_date=date(2024, 12, 27),
        ...     adults=2,
        ...     children=2,
        ...     infants=1,
        ...     cabin_class=CabinClass.PREMIUM_ECONOMY
        ... )
    """

    origin: str = Field(..., description="Origin airport code")
    destination: str = Field(..., description="Destination airport code")
    departure_date: date
    return_date: Optional[date] = None
    trip_type: TripType = TripType.ROUND_TRIP
    cabin_class: CabinClass = CabinClass.ECONOMY
    adults: int = Field(1, ge=1, le=9)
    children: int = Field(0, ge=0, le=8)
    infants: int = Field(0, ge=0, le=4)

    @field_validator("origin", "destination")
    @classmethod
    def validate_airport_codes(cls, v):
        """Validate airport codes are 3 letters and convert to uppercase."""
        if len(v) != 3:
            raise ValueError("Airport code must be 3 letters")
        return v.upper()

    @model_validator(mode="after")
    def validate_return_date_for_round_trip(self):
        """Validate return date logic and trip type consistency."""
        if self.trip_type == TripType.ROUND_TRIP and self.return_date is None:
            raise ValueError("Return date required for round trip")
        if (
            self.return_date
            and self.departure_date
            and self.return_date <= self.departure_date
        ):
            raise ValueError("Return date must be after departure date")
        return self


class FlightResult(BaseModel):
    """
    Container for flight search results with metadata and analysis methods.

    Represents the complete response from a flight search, including all
    found flights, the original search parameters, and metadata about the
    search execution. Provides convenience methods for analyzing results.

    Attributes:
        flights: List of Flight objects returned by the search, sorted by
            relevance or price depending on the search site
        search_params: Original search parameters used for this search
        search_timestamp: When the search was performed (UTC timezone)
        total_results: Total number of flights found (may be more than returned)
        currency: Currency for all prices (default "USD")

    Properties:
        cheapest_flight: Flight with lowest price, or None if no flights
        fastest_flight: Flight with shortest duration, or None if no flights

    Note:
        - Results may be limited by max_results parameter in search
        - Prices are typically in USD but currency field indicates actual currency
        - Search timestamp helps with cache management and result freshness

    Example:
        >>> result = await scrapper.search_flights("JFK", "LAX", date.today())
        >>> print(f"Found {len(result.flights)} flights")
        >>> print(f"Cheapest: ${result.cheapest_flight.price}")
        >>> print(f"Fastest: {result.fastest_flight.total_duration_minutes//60}h")

        >>> # Filter results
        >>> nonstop_flights = [f for f in result.flights if f.stops == 0]
        >>> business_flights = [f for f in result.flights
        ...                    if f.cabin_class == CabinClass.BUSINESS]
    """

    flights: list[Flight]
    search_params: SearchParams
    search_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    total_results: int
    currency: str = "USD"

    @property
    def cheapest_flight(self) -> Optional[Flight]:
        """Get the flight with the lowest price."""
        return min(self.flights, key=lambda f: f.price) if self.flights else None

    @property
    def fastest_flight(self) -> Optional[Flight]:
        """Get the flight with the shortest total duration."""
        return (
            min(self.flights, key=lambda f: f.total_duration_minutes)
            if self.flights
            else None
        )


class PriceCalendarEntry(BaseModel):
    """
    Single date entry in a price calendar for flexible date searches.

    Represents the price and availability for flights on a specific date,
    used in flexible date search results to show price trends across
    multiple dates.

    Attributes:
        date: The specific date for this price entry
        price: Flight price for this date (None if no flights available)
        available: Whether flights are available on this date

    Note:
        - Price may be None even if available=True (indicates availability
          but price not determined/displayed)
        - Used for building price calendars and finding optimal travel dates

    Example:
        >>> entry = PriceCalendarEntry(
        ...     date=date(2024, 8, 15),
        ...     price=Decimal("299.00"),
        ...     available=True
        ... )
        >>> if entry.available and entry.price:
        ...     print(f"{entry.date}: ${entry.price}")
    """

    date: date
    price: Optional[Decimal] = None
    available: bool = True


class PriceCalendar(BaseModel):
    """
    Price calendar for flexible date search showing price trends over time.

    Contains price and availability data across multiple dates for a specific
    route and cabin class. Useful for finding the cheapest travel dates and
    understanding price patterns (weekday vs weekend, seasonal trends).

    Attributes:
        origin: Origin airport code for this price calendar
        destination: Destination airport code for this price calendar
        entries: List of price entries for different dates
        cabin_class: Cabin class these prices apply to

    Methods:
        get_cheapest_dates: Find the dates with lowest prices

    Note:
        - Typically covers a month or several weeks of potential travel dates
        - Prices may vary significantly by day of week and season
        - Used for flexible travelers who can adjust dates for better prices

    Example:
        >>> calendar = await scrapper.get_price_calendar(
        ...     origin="JFK",
        ...     destination="LAX",
        ...     departure_month=date(2024, 8, 1),
        ...     cabin_class=CabinClass.ECONOMY
        ... )
        >>> cheapest = calendar.get_cheapest_dates(limit=3)
        >>> for entry in cheapest:
        ...     print(f"{entry.date}: ${entry.price}")
    """

    origin: str
    destination: str
    entries: list[PriceCalendarEntry]
    cabin_class: CabinClass = CabinClass.ECONOMY

    def get_cheapest_dates(self, limit: int = 5) -> list[PriceCalendarEntry]:
        """
        Get the cheapest available dates from the calendar.

        Args:
            limit: Maximum number of dates to return

        Returns:
            List of PriceCalendarEntry objects sorted by price (lowest first)

        Example:
            >>> cheapest = calendar.get_cheapest_dates(limit=3)
            >>> best_date = cheapest[0] if cheapest else None
        """
        available_entries = [e for e in self.entries if e.available and e.price]
        return sorted(available_entries, key=lambda e: e.price)[:limit]


class MultiCitySegment(BaseModel):
    """
    Single segment in a multi-city trip itinerary.

    Represents one leg of a multi-city journey, defining the origin,
    destination, and departure date for that segment. Multiple segments
    are combined to create complex itineraries.

    Attributes:
        origin: Origin airport code for this segment (3-letter IATA)
        destination: Destination airport code for this segment (3-letter IATA)
        departure_date: Date of departure for this segment

    Note:
        - Each segment's destination typically becomes the next segment's origin
        - Final segment destination is the end point of the entire journey
        - Dates should be in logical chronological order

    Example:
        Multi-city trip NYC -> Paris -> Rome -> NYC:
        >>> segments = [
        ...     MultiCitySegment(origin="NYC", destination="CDG",
        ...                     departure_date=date(2024, 8, 15)),
        ...     MultiCitySegment(origin="CDG", destination="FCO",
        ...                     departure_date=date(2024, 8, 20)),
        ...     MultiCitySegment(origin="FCO", destination="NYC",
        ...                     departure_date=date(2024, 8, 25))
        ... ]
    """

    origin: str
    destination: str
    departure_date: date


class MultiCitySearchParams(BaseModel):
    """
    Search parameters for complex multi-city flight itineraries.

    Defines the parameters for searching multi-city trips that visit
    multiple destinations. Supports 2-6 segments for complex travel
    patterns that aren't possible with simple round-trip searches.

    Attributes:
        segments: List of trip segments (2-6 segments supported).
            Each segment defines one leg of the journey
        cabin_class: Preferred cabin class for all segments
        adults: Number of adult passengers (1-9)
        children: Number of child passengers (0-8)
        infants: Number of infant passengers (0-4)

    Validation:
        - Must have 2-6 segments (airline/site limitations)
        - Passenger counts follow same rules as regular searches
        - No automatic validation of segment connectivity

    Example:
        European tour: London -> Paris -> Rome -> London:
        >>> params = MultiCitySearchParams(
        ...     segments=[
        ...         MultiCitySegment("LHR", "CDG", date(2024, 9, 1)),
        ...         MultiCitySegment("CDG", "FCO", date(2024, 9, 8)),
        ...         MultiCitySegment("FCO", "LHR", date(2024, 9, 15))
        ...     ],
        ...     cabin_class=CabinClass.BUSINESS,
        ...     adults=2
        ... )

        Business trip with multiple meetings:
        >>> params = MultiCitySearchParams(
        ...     segments=[
        ...         MultiCitySegment("JFK", "LAX", date(2024, 10, 5)),
        ...         MultiCitySegment("LAX", "SFO", date(2024, 10, 10)),
        ...         MultiCitySegment("SFO", "JFK", date(2024, 10, 15))
        ...     ],
        ...     adults=1,
        ...     cabin_class=CabinClass.ECONOMY
        ... )
    """

    segments: list[MultiCitySegment] = Field(..., min_length=2, max_length=6)
    cabin_class: CabinClass = CabinClass.ECONOMY
    adults: int = Field(1, ge=1, le=9)
    children: int = Field(0, ge=0, le=8)
    infants: int = Field(0, ge=0, le=4)
