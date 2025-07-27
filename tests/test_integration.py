"""
Integration tests for ITA Scrapper.
"""

from datetime import date, timedelta

import pytest

from ita_scrapper import ITAScrapper
from ita_scrapper.models import CabinClass, TripType


@pytest.mark.asyncio
@pytest.mark.integration
class TestITAScrapperIntegration:
    """Integration tests for ITA Scrapper."""

    async def test_scrapper_context_manager(self):
        """Test scrapper as context manager."""
        async with ITAScrapper(headless=True) as scrapper:
            assert scrapper._browser is not None
            assert scrapper._page is not None

    async def test_manual_start_close(self):
        """Test manual start and close."""
        scrapper = ITAScrapper(headless=True)
        await scrapper.start()

        assert scrapper._browser is not None
        assert scrapper._page is not None

        await scrapper.close()

    # @pytest.mark.slow
    async def test_search_flights_integration(self):
        """Test actual flight search (slow test)."""
        # Skip this test in CI/CD or mark as slow
        # pytest.skip("Slow integration test - run manually")

        async with ITAScrapper(headless=True) as scrapper:
            result = await scrapper.search_flights(
                origin="JFK",
                destination="LAX",
                departure_date=date.today() + timedelta(days=30),
                return_date=date.today() + timedelta(days=37),
            )

            assert result is not None
            assert result.search_params.origin == "JFK"
            assert result.search_params.destination == "LAX"

    # @pytest.mark.slow
    async def test_one_way_search_integration(self):
        """Test one-way flight search."""
        # pytest.skip("Slow integration test - run manually")

        async with ITAScrapper(headless=True) as scrapper:
            result = await scrapper.search_flights(
                origin="NYC",
                destination="SFO",
                departure_date=date.today() + timedelta(days=15),
                cabin_class=CabinClass.BUSINESS,
                adults=2,
            )

            assert result is not None
            assert result.search_params.trip_type == TripType.ONE_WAY
            assert result.search_params.cabin_class == CabinClass.BUSINESS
            assert result.search_params.adults == 2
