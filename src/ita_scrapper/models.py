"""
Pydantic models for ITA Scrapper.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class TripType(str, Enum):
    """Type of trip."""

    ROUND_TRIP = "round_trip"
    ONE_WAY = "one_way"
    MULTI_CITY = "multi_city"


class CabinClass(str, Enum):
    """Cabin class options."""

    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class Airport(BaseModel):
    """Airport information."""

    code: str = Field(..., description="3-letter IATA airport code")
    name: Optional[str] = Field(None, description="Full airport name")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country name")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if len(v) != 3:
            raise ValueError("Airport code must be 3 letters")
        return v.upper()


class Airline(BaseModel):
    """Airline information."""

    code: str = Field(..., description="2-letter IATA airline code")
    name: Optional[str] = Field(None, description="Full airline name")


class FlightSegment(BaseModel):
    """Individual flight segment."""

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
    """Flight information."""

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
        """Get list of airline codes."""
        return list({segment.airline.code for segment in self.segments})


class SearchParams(BaseModel):
    """Flight search parameters."""

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
        if len(v) != 3:
            raise ValueError("Airport code must be 3 letters")
        return v.upper()

    @model_validator(mode="after")
    def validate_return_date_for_round_trip(self):
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
    """Flight search results."""

    flights: list[Flight]
    search_params: SearchParams
    search_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    total_results: int
    currency: str = "USD"

    @property
    def cheapest_flight(self) -> Optional[Flight]:
        """Get the cheapest flight."""
        return min(self.flights, key=lambda f: f.price) if self.flights else None

    @property
    def fastest_flight(self) -> Optional[Flight]:
        """Get the fastest flight."""
        return (
            min(self.flights, key=lambda f: f.total_duration_minutes)
            if self.flights
            else None
        )


class PriceCalendarEntry(BaseModel):
    """Single entry in price calendar."""

    date: date
    price: Optional[Decimal] = None
    available: bool = True


class PriceCalendar(BaseModel):
    """Price calendar for flexible date search."""

    origin: str
    destination: str
    entries: list[PriceCalendarEntry]
    cabin_class: CabinClass = CabinClass.ECONOMY

    def get_cheapest_dates(self, limit: int = 5) -> list[PriceCalendarEntry]:
        """Get the cheapest available dates."""
        available_entries = [e for e in self.entries if e.available and e.price]
        return sorted(available_entries, key=lambda e: e.price)[:limit]


class MultiCitySegment(BaseModel):
    """Multi-city trip segment."""

    origin: str
    destination: str
    departure_date: date


class MultiCitySearchParams(BaseModel):
    """Multi-city search parameters."""

    segments: list[MultiCitySegment] = Field(..., min_length=2, max_length=6)
    cabin_class: CabinClass = CabinClass.ECONOMY
    adults: int = Field(1, ge=1, le=9)
    children: int = Field(0, ge=0, le=8)
    infants: int = Field(0, ge=0, le=4)
