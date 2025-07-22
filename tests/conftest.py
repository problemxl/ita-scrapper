"""
Test configuration and fixtures.
"""

import asyncio
from datetime import date, timedelta

import pytest

from ita_scrapper import ITAScrapper
from ita_scrapper.models import CabinClass, SearchParams, TripType


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def scrapper():
    """Create a scrapper instance for testing."""
    scrapper = ITAScrapper(headless=True, timeout=10000)
    await scrapper.start()
    yield scrapper
    await scrapper.close()


@pytest.fixture
def sample_search_params():
    """Sample search parameters for testing."""
    return SearchParams(
        origin="JFK",
        destination="LAX",
        departure_date=date.today() + timedelta(days=30),
        return_date=date.today() + timedelta(days=37),
        trip_type=TripType.ROUND_TRIP,
        cabin_class=CabinClass.ECONOMY,
        adults=1,
    )


@pytest.fixture
def one_way_search_params():
    """One-way search parameters for testing."""
    return SearchParams(
        origin="NYC",
        destination="SFO",
        departure_date=date.today() + timedelta(days=15),
        trip_type=TripType.ONE_WAY,
        cabin_class=CabinClass.ECONOMY,
        adults=2,
    )
