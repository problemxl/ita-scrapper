#!/usr/bin/env python3
"""
Test the enhanced flight data parsing with real ITA Matrix HTML structure.
"""

import asyncio
import logging
from datetime import date, timedelta
from pathlib import Path

from ita_scrapper import ITAScrapper
from ita_scrapper.models import CabinClass
from ita_scrapper.parsers import ITAMatrixParser

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_enhanced_parsing():
    """Test the enhanced parsing capabilities."""
    print("🔬 Testing Enhanced Flight Data Parsing")
    print("=" * 60)

    # Test with real ITA Matrix structure
    try:
        async with ITAScrapper(
            headless=False,  # Show browser for debugging
            use_matrix=True,
            timeout=60000,
        ) as scrapper:
            print("🌐 Testing with ITA Matrix...")

            # Test search
            departure_date = date.today() + timedelta(days=30)
            return_date = departure_date + timedelta(days=7)

            print(f"🔍 Searching JFK → LHR")
            print(f"   Departure: {departure_date}")
            print(f"   Return: {return_date}")

            result = await scrapper.search_flights(
                origin="JFK",
                destination="LHR",
                departure_date=departure_date,
                return_date=return_date,
                cabin_class=CabinClass.ECONOMY,
                adults=1,
                max_results=5,
            )

            print(f"\n✅ Found {len(result.flights)} flights")

            if result.flights:
                print("\n📋 Flight Details:")
                print("-" * 50)

                for i, flight in enumerate(result.flights, 1):
                    print(f"\n{i}. Flight ${flight.price}")
                    print(
                        f"   Duration: {flight.total_duration_minutes // 60}h {flight.total_duration_minutes % 60}m"
                    )
                    print(f"   Stops: {flight.stops}")
                    print(f"   Airlines: {', '.join(flight.airlines)}")

                    for j, segment in enumerate(flight.segments):
                        print(
                            f"   Segment {j + 1}: {segment.departure_airport.code} → {segment.arrival_airport.code}"
                        )
                        print(f"     {segment.airline.name} {segment.flight_number}")
                        print(
                            f"     Dep: {segment.departure_time.strftime('%I:%M %p %b %d')}"
                        )
                        print(
                            f"     Arr: {segment.arrival_time.strftime('%I:%M %p %b %d')}"
                        )

                # Test flight filtering and sorting
                print(f"\n💰 Cheapest flight: ${result.cheapest_flight.price}")
                print(
                    f"⚡ Fastest flight: {result.fastest_flight.total_duration_minutes // 60}h {result.fastest_flight.total_duration_minutes % 60}m"
                )

            else:
                print("❌ No flights found - this might indicate parsing issues")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")


async def test_html_parsing():
    """Test parsing logic with the provided HTML example."""
    print("\n🧪 Testing HTML Parsing Logic")
    print("=" * 60)

    # Read the example HTML file
    example_html_path = (
        Path(__file__).parent.parent / "src" / "ita_scrapper" / "example.html"
    )

    if not example_html_path.exists():
        print("❌ Example HTML file not found")
        return

    try:
        parser = ITAMatrixParser()

        # Create a mock page for testing
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Load the example HTML
            with open(example_html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            await page.set_content(html_content)

            print("📄 Loaded example HTML")

            # Test tooltip extraction
            tooltip_data = await parser._extract_tooltip_data(page)
            print(f"🏷️  Found {len(tooltip_data)} tooltips")

            # Show some tooltip examples
            for i, (tooltip_id, tooltip_text) in enumerate(
                list(tooltip_data.items())[:5]
            ):
                print(f"   {i + 1}. {tooltip_id}: {tooltip_text[:60]}...")

            # Test price extraction
            prices_found = []
            for tooltip_text in tooltip_data.values():
                prices = parser._extract_prices_from_text(tooltip_text)
                if prices:
                    prices_found.extend(prices.values())

            if prices_found:
                print(f"💲 Found prices: {[f'${p}' for p in prices_found]}")

            # Test airline extraction
            airlines_found = set()
            for tooltip_text in tooltip_data.values():
                airlines = parser._extract_airlines_from_text(tooltip_text)
                airlines_found.update(airlines)

            if airlines_found:
                print(f"✈️  Found airlines: {', '.join(airlines_found)}")

            # Test time extraction
            times_found = []
            for tooltip_text in tooltip_data.values():
                times = parser._extract_times_from_text(tooltip_text)
                times_found.extend(times)

            if times_found:
                print(f"🕒 Found {len(times_found)} time entries")
                for time_info in times_found[:3]:  # Show first 3
                    print(
                        f"   {time_info['airport']}: {time_info['time']} {time_info['date']}"
                    )

            await browser.close()

        print("✅ HTML parsing test completed")

    except Exception as e:
        logger.error(f"HTML parsing test failed: {e}")
        print(f"❌ HTML parsing test failed: {e}")


async def test_parsing_robustness():
    """Test parsing robustness with various input formats."""
    print("\n🛡️  Testing Parsing Robustness")
    print("=" * 60)

    parser = ITAMatrixParser()

    # Test price parsing
    price_tests = [
        "Price per passenger: $593",
        "$1,234.56",
        "USD 500",
        "500 USD",
        "€450",  # Should handle even though not USD
        "invalid price text",
    ]

    print("💲 Price parsing tests:")
    for price_text in price_tests:
        price = parser._extract_price_from_text(price_text)
        status = "✅" if price else "❌"
        print(f"   {status} '{price_text}' → {price}")

    # Test airline parsing
    airline_tests = [
        "Virgin Atlantic, Delta",
        "Delta, Virgin Atlantic",
        "American Airlines",
        "United",
        "AA",
        "random text with no airline",
    ]

    print("\n✈️  Airline parsing tests:")
    for airline_text in airline_tests:
        airlines = parser._extract_airlines_from_text(airline_text)
        status = "✅" if airlines else "❌"
        print(f"   {status} '{airline_text}' → {airlines}")

    # Test time parsing
    time_tests = [
        "LHR time: 6:25 AM Sat July 12",
        "JFK time: 12:45 PM Fri July 18",
        "Local time: 1:25 AM Sat July 12",
        "invalid time format",
    ]

    print("\n🕒 Time parsing tests:")
    for time_text in time_tests:
        times = parser._extract_times_from_text(time_text)
        status = "✅" if times else "❌"
        result = times[0] if times else "None"
        print(f"   {status} '{time_text}' → {result}")

    print("\n✅ Robustness testing completed")


async def main():
    """Run all tests."""
    print("🚀 Starting Enhanced Flight Data Parsing Tests")
    print("=" * 70)

    # Test HTML parsing logic first (doesn't require network)
    await test_html_parsing()

    # Test parsing robustness
    await test_parsing_robustness()

    # Test with real site (may fail due to anti-bot measures)
    print(f"\n{'=' * 70}")
    user_input = input("🌐 Do you want to test with the real ITA Matrix site? (y/N): ")
    if user_input.lower() in ["y", "yes"]:
        await test_enhanced_parsing()
    else:
        print("⏭️  Skipping real site test")

    print(f"\n{'=' * 70}")
    print("🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
