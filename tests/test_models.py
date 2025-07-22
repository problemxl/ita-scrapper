"""
Tests for ITA Scrapper models.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ita_scrapper.models import (
    Airline,
    Airport,
    CabinClass,
    Flight,
    FlightResult,
    FlightSegment,
    SearchParams,
    TripType,
)


class TestAirport:
    """Test Airport model."""

    def test_valid_airport_code(self):
        """Test valid airport code creation."""
        airport = Airport(code="jfk")
        assert airport.code == "JFK"

    def test_invalid_airport_code(self):
        """Test invalid airport code raises error."""
        with pytest.raises(ValueError):
            Airport(code="invalid")

    def test_airport_with_details(self):
        """Test airport with full details."""
        airport = Airport(
            code="LAX",
            name="Los Angeles International Airport",
            city="Los Angeles",
            country="United States",
        )
        assert airport.code == "LAX"
        assert airport.name == "Los Angeles International Airport"


class TestSearchParams:
    """Test SearchParams model."""

    def test_valid_round_trip_params(self):
        """Test valid round trip parameters."""
        departure = date.today() + timedelta(days=30)
        return_date = departure + timedelta(days=7)

        params = SearchParams(
            origin="JFK",
            destination="LAX",
            departure_date=departure,
            return_date=return_date,
            trip_type=TripType.ROUND_TRIP,
        )

        assert params.origin == "JFK"
        assert params.destination == "LAX"
        assert params.trip_type == TripType.ROUND_TRIP

    def test_one_way_without_return_date(self):
        """Test one way trip without return date."""
        params = SearchParams(
            origin="NYC",
            destination="SFO",
            departure_date=date.today() + timedelta(days=15),
            trip_type=TripType.ONE_WAY,
        )

        assert params.return_date is None
        assert params.trip_type == TripType.ONE_WAY

    def test_invalid_return_date(self):
        """Test invalid return date raises error."""
        departure = date.today() + timedelta(days=30)
        return_date = departure - timedelta(days=1)  # Before departure

        with pytest.raises(ValueError):
            SearchParams(
                origin="JFK",
                destination="LAX",
                departure_date=departure,
                return_date=return_date,
                trip_type=TripType.ROUND_TRIP,
            )

    def test_round_trip_without_return_date(self):
        """Test round trip without return date raises error."""
        with pytest.raises(ValueError):
            SearchParams(
                origin="JFK",
                destination="LAX",
                departure_date=date.today() + timedelta(days=30),
                trip_type=TripType.ROUND_TRIP,
            )

    def test_passenger_validation(self):
        """Test passenger count validation."""
        # Valid passenger counts
        params = SearchParams(
            origin="JFK",
            destination="LAX",
            departure_date=date.today() + timedelta(days=30),
            trip_type=TripType.ONE_WAY,
            adults=2,
            children=1,
            infants=1,
        )
        assert params.adults == 2
        assert params.children == 1
        assert params.infants == 1


class TestFlight:
    """Test Flight model."""

    def test_flight_properties(self):
        """Test flight property calculations."""
        from datetime import datetime

        departure_time = datetime(2024, 6, 15, 10, 0)
        arrival_time = datetime(2024, 6, 15, 13, 30)

        segment = FlightSegment(
            airline=Airline(code="AA", name="American Airlines"),
            flight_number="AA123",
            departure_airport=Airport(code="JFK"),
            arrival_airport=Airport(code="LAX"),
            departure_time=departure_time,
            arrival_time=arrival_time,
            duration_minutes=210,
        )

        flight = Flight(
            segments=[segment],
            price=Decimal("299.99"),
            cabin_class=CabinClass.ECONOMY,
            total_duration_minutes=210,
        )

        assert flight.departure_time == departure_time
        assert flight.arrival_time == arrival_time
        assert flight.airlines == ["AA"]
        assert flight.price == Decimal("299.99")


class TestFlightResult:
    """Test FlightResult model."""

    def test_flight_result_properties(self, sample_search_params):
        """Test flight result property calculations."""

        # Create sample flights
        cheap_flight = Flight(
            segments=[],
            price=Decimal("199.99"),
            cabin_class=CabinClass.ECONOMY,
            total_duration_minutes=300,
        )

        fast_flight = Flight(
            segments=[],
            price=Decimal("399.99"),
            cabin_class=CabinClass.ECONOMY,
            total_duration_minutes=180,
        )

        result = FlightResult(
            flights=[cheap_flight, fast_flight],
            search_params=sample_search_params,
            total_results=2,
        )

        assert result.cheapest_flight == cheap_flight
        assert result.fastest_flight == fast_flight
        assert len(result.flights) == 2

    def test_empty_flight_result(self, sample_search_params):
        """Test empty flight result."""
        result = FlightResult(
            flights=[], search_params=sample_search_params, total_results=0
        )

        assert result.cheapest_flight is None
        assert result.fastest_flight is None
        assert len(result.flights) == 0
