#!/usr/bin/env python3
"""
Test real ITA Matrix access (no demo mode).
"""

import asyncio
import logging
from datetime import date, timedelta

from ita_scrapper import ITAScrapper
from ita_scrapper.models import CabinClass
from ita_scrapper.exceptions import ITAScrapperError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_real_matrix_access():
    """Test accessing the real ITA Matrix website."""
    print("🔍 Testing Real ITA Matrix Access")
    print("=" * 50)
    print("This will attempt to access matrix.itasoftware.com")
    print("Note: This may take longer and could fail if the site structure changes")
    print()

    try:
        async with ITAScrapper(
            headless=False,  # Show browser for debugging
            use_matrix=True,
            timeout=60000,  # Longer timeout for real site
        ) as scrapper:
            print("🌐 Navigating to ITA Matrix...")

            # Simple search with nearby dates to increase success chance
            departure_date = date.today() + timedelta(days=30)
            return_date = departure_date + timedelta(days=7)

            print(f"🔍 Searching JFK → LAX")
            print(f"   Departure: {departure_date}")
            print(f"   Return: {return_date}")

            result = await scrapper.search_flights(
                origin="JFK",
                destination="LAX",
                departure_date=departure_date,
                return_date=return_date,
                cabin_class=CabinClass.ECONOMY,
                adults=1,
                max_results=5,
            )

            print(f"✅ Success! Found {len(result.flights)} flights")

            if result.flights:
                print("\nFlight results:")
                for i, flight in enumerate(result.flights[:3], 1):
                    duration_h = flight.total_duration_minutes // 60
                    duration_m = flight.total_duration_minutes % 60
                    print(
                        f"  {i}. ${flight.price} - {duration_h}h {duration_m}m - {', '.join(flight.airlines)}"
                    )
            else:
                print("⚠️  No flights found - site structure may have changed")

    except ITAScrapperError as e:
        print(f"❌ ITA Scrapper Error: {e}")
        print("This could indicate:")
        print("  • The website structure has changed")
        print("  • The site is blocking automated access")
        print("  • Network connectivity issues")

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("This could indicate:")
        print("  • Playwright/browser issues")
        print("  • System compatibility problems")


async def test_google_flights_fallback():
    """Test Google Flights as fallback."""
    print("\n🔄 Testing Google Flights Fallback")
    print("=" * 50)

    try:
        async with ITAScrapper(
            headless=False,  # Show browser for debugging
            use_matrix=False,  # Use Google Flights
            timeout=60000,
        ) as scrapper:
            print("🌐 Navigating to Google Flights...")

            departure_date = date.today() + timedelta(days=30)
            return_date = departure_date + timedelta(days=7)

            result = await scrapper.search_flights(
                origin="JFK",
                destination="LAX",
                departure_date=departure_date,
                return_date=return_date,
                cabin_class=CabinClass.ECONOMY,
                adults=1,
                max_results=5,
            )

            print(f"✅ Google Flights: Found {len(result.flights)} flights")

    except Exception as e:
        print(f"❌ Google Flights also failed: {e}")


async def test_site_access_only():
    """Test just accessing the sites without searching."""
    print("\n🌐 Testing Site Access Only")
    print("=" * 50)

    # Test ITA Matrix access
    try:
        print("Testing ITA Matrix access...")
        async with ITAScrapper(
            headless=False, use_matrix=True, timeout=30000
        ) as scrapper:
            print("🌐 Navigating to ITA Matrix...")
            await scrapper._navigate_to_flights()
            print("✅ ITA Matrix accessible!")

            # Take a screenshot
            await scrapper._page.screenshot(path="ita_matrix_success.png")
            print("📷 Screenshot saved as ita_matrix_success.png")

    except Exception as e:
        print(f"❌ ITA Matrix access failed: {e}")

    # Test Google Flights access
    try:
        print("\nTesting Google Flights access...")
        async with ITAScrapper(
            headless=False, use_matrix=False, timeout=30000
        ) as scrapper:
            print("🌐 Navigating to Google Flights...")
            await scrapper._navigate_to_flights()
            print("✅ Google Flights accessible!")

            # Take a screenshot
            await scrapper._page.screenshot(path="google_flights_success.png")
            print("📷 Screenshot saved as google_flights_success.png")

    except Exception as e:
        print(f"❌ Google Flights access failed: {e}")


async def main():
    """Main test function."""
    print("🧪 ITA Scrapper Real Website Tests")
    print("=" * 50)
    print("Testing access to real flight booking websites...")
    print("These tests may fail if websites change their structure")
    print("or implement anti-bot measures.")
    print()

    # Test ITA Matrix
    await test_real_matrix_access()

    # Test Google Flights as fallback
    await test_google_flights_fallback()

    # Test site access only
    await test_site_access_only()

    print("\n" + "=" * 50)
    print("📝 Test Summary:")
    print("• If both tests fail, the websites may have changed")
    print("• Use demo_mode=True for development and testing")
    print("• Real scraping may require:")
    print("  - Updated selectors")
    print("  - Proxy/rotation strategies")
    print("  - Human-like behavior simulation")
    print("  - Compliance with website ToS")


if __name__ == "__main__":
    asyncio.run(main())
