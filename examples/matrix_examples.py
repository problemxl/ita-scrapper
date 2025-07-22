#!/usr/bin/env python3
"""
ITA Matrix specific examples for the ITA Scrapper library.
"""

import asyncio
import logging
from datetime import date, timedelta
from decimal import Decimal

from ita_scrapper import ITAScrapper
from ita_scrapper.models import CabinClass, TripType
from ita_scrapper.exceptions import ITAScrapperError


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def matrix_basic_search():
    """Example: Basic search using ITA Matrix."""
    print("🔍 ITA Matrix Basic Search Example")
    print("=" * 50)

    try:
        # Use ITA Matrix (use_matrix=True is default)
        async with ITAScrapper(
            headless=True, use_matrix=True, demo_mode=True
        ) as scrapper:
            result = await scrapper.search_flights(
                origin="JFK",
                destination="LHR",
                departure_date=date.today() + timedelta(days=30),
                return_date=date.today() + timedelta(days=37),
                cabin_class=CabinClass.ECONOMY,
                adults=1,
            )

            print(f"Found {len(result.flights)} flights using ITA Matrix")
            print(
                f"Search: {result.search_params.origin} → {result.search_params.destination}"
            )
            print(f"Departure: {result.search_params.departure_date}")
            print(f"Return: {result.search_params.return_date}")
            print()

            if result.flights:
                print("Flight options:")
                for i, flight in enumerate(result.flights[:3], 1):
                    duration_h = flight.total_duration_minutes // 60
                    duration_m = flight.total_duration_minutes % 60
                    stops_text = (
                        "Direct" if flight.stops == 0 else f"{flight.stops} stop(s)"
                    )

                    print(
                        f"  {i}. ${flight.price:,} - {duration_h}h {duration_m}m - {stops_text}"
                    )
                    print(f"     Airlines: {', '.join(flight.airlines)}")
                    print()

    except ITAScrapperError as e:
        logger.error(f"Matrix search error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def compare_matrix_vs_google():
    """Example: Compare results between ITA Matrix and Google Flights."""
    print("\n⚖️  ITA Matrix vs Google Flights Comparison")
    print("=" * 50)

    search_params = {
        "origin": "LAX",
        "destination": "JFK",
        "departure_date": date.today() + timedelta(days=21),
        "return_date": date.today() + timedelta(days=28),
        "cabin_class": CabinClass.ECONOMY,
        "adults": 1,
    }

    try:
        # Search with ITA Matrix
        print("🔍 Searching with ITA Matrix...")
        async with ITAScrapper(
            headless=True, use_matrix=True, demo_mode=True
        ) as matrix_scrapper:
            matrix_result = await matrix_scrapper.search_flights(**search_params)

        # Search with Google Flights
        print("🔍 Searching with Google Flights...")
        async with ITAScrapper(
            headless=True, use_matrix=False, demo_mode=True
        ) as google_scrapper:
            google_result = await google_scrapper.search_flights(**search_params)

        # Compare results
        print("\n📊 Comparison Results:")
        print(f"ITA Matrix found: {len(matrix_result.flights)} flights")
        print(f"Google Flights found: {len(google_result.flights)} flights")

        if matrix_result.flights and google_result.flights:
            matrix_cheapest = matrix_result.cheapest_flight
            google_cheapest = google_result.cheapest_flight

            print(f"\nCheapest prices:")
            print(f"  ITA Matrix: ${matrix_cheapest.price}")
            print(f"  Google Flights: ${google_cheapest.price}")

            price_diff = abs(matrix_cheapest.price - google_cheapest.price)
            if matrix_cheapest.price < google_cheapest.price:
                print(f"  💰 ITA Matrix is ${price_diff} cheaper!")
            elif google_cheapest.price < matrix_cheapest.price:
                print(f"  💰 Google Flights is ${price_diff} cheaper!")
            else:
                print(f"  🤝 Both sources show same price")

    except ITAScrapperError as e:
        logger.error(f"Comparison error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def matrix_advanced_search():
    """Example: Advanced search features specific to ITA Matrix."""
    print("\n🎯 ITA Matrix Advanced Search Example")
    print("=" * 50)

    try:
        async with ITAScrapper(
            headless=True, use_matrix=True, demo_mode=True
        ) as scrapper:
            # Complex international route
            result = await scrapper.search_flights(
                origin="SFO",
                destination="BKK",  # Bangkok
                departure_date=date.today() + timedelta(days=60),
                return_date=date.today() + timedelta(days=74),
                cabin_class=CabinClass.BUSINESS,
                adults=2,
            )

            print(
                f"Advanced search: {result.search_params.origin} → {result.search_params.destination}"
            )
            print(f"Business class for 2 adults")
            print(f"Found {len(result.flights)} options")

            if result.flights:
                print("\nBusiness class options:")
                for i, flight in enumerate(result.flights, 1):
                    duration_h = flight.total_duration_minutes // 60
                    duration_m = flight.total_duration_minutes % 60

                    print(f"  {i}. ${flight.price:,} - {duration_h}h {duration_m}m")
                    print(f"     Airlines: {', '.join(flight.airlines)}")
                    print(f"     Stops: {flight.stops}")
                    print(f"     Refundable: {'Yes' if flight.is_refundable else 'No'}")
                    print()

                # Show statistics
                prices = [f.price for f in result.flights]
                avg_price = sum(prices) / len(prices)
                print(f"📊 Statistics:")
                print(f"   Average price: ${avg_price:,.2f}")
                print(f"   Price range: ${min(prices):,} - ${max(prices):,}")
                print(f"   Total savings potential: ${max(prices) - min(prices):,}")

    except ITAScrapperError as e:
        logger.error(f"Advanced search error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def matrix_flexible_dates():
    """Example: Flexible date search with ITA Matrix."""
    print("\n📅 ITA Matrix Flexible Dates Example")
    print("=" * 50)

    try:
        async with ITAScrapper(
            headless=True, use_matrix=True, demo_mode=True
        ) as scrapper:
            # Get price calendar
            calendar = await scrapper.get_price_calendar(
                origin="NYC",
                destination="LON",
                departure_month=date.today() + timedelta(days=45),
                cabin_class=CabinClass.ECONOMY,
            )

            print(f"Price calendar: {calendar.origin} → {calendar.destination}")
            print(f"Analyzing {len(calendar.entries)} dates")

            # Find best deals
            cheapest_dates = calendar.get_cheapest_dates(7)
            print(f"\n💰 Top 7 cheapest dates:")
            for i, entry in enumerate(cheapest_dates, 1):
                if entry.price:
                    day_name = entry.date.strftime("%A")
                    print(
                        f"  {i}. {entry.date.strftime('%Y-%m-%d')} ({day_name}): ${entry.price}"
                    )

            # Analyze day-of-week patterns
            weekday_prices = {}
            for entry in calendar.entries:
                if entry.price and entry.available:
                    day_name = entry.date.strftime("%A")
                    if day_name not in weekday_prices:
                        weekday_prices[day_name] = []
                    weekday_prices[day_name].append(entry.price)

            print(f"\n📊 Average prices by day of week:")
            for day, prices in weekday_prices.items():
                if prices:
                    avg_price = sum(prices) / len(prices)
                    print(f"  {day}: ${avg_price:.2f}")

    except ITAScrapperError as e:
        logger.error(f"Flexible dates error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def matrix_error_handling():
    """Example: Error handling specific to ITA Matrix."""
    print("\n🚨 ITA Matrix Error Handling Example")
    print("=" * 50)

    # Test various error scenarios
    test_cases = [
        {
            "name": "Invalid airport code",
            "params": {
                "origin": "INVALID",
                "destination": "JFK",
                "departure_date": date.today() + timedelta(days=30),
            },
        },
        {
            "name": "Past departure date",
            "params": {
                "origin": "JFK",
                "destination": "LAX",
                "departure_date": date.today() - timedelta(days=1),
            },
        },
        {
            "name": "Return before departure",
            "params": {
                "origin": "JFK",
                "destination": "LAX",
                "departure_date": date.today() + timedelta(days=30),
                "return_date": date.today() + timedelta(days=29),
            },
        },
    ]

    for test_case in test_cases:
        try:
            async with ITAScrapper(
                headless=True, use_matrix=True, demo_mode=True
            ) as scrapper:
                await scrapper.search_flights(**test_case["params"])
                print(f"❌ {test_case['name']}: Should have failed but didn't")
        except ITAScrapperError as e:
            print(f"✅ {test_case['name']}: Correctly caught error - {e}")
        except Exception as e:
            print(f"⚠️  {test_case['name']}: Unexpected error type - {e}")


async def main():
    """Run all ITA Matrix examples."""
    print("🚀 ITA Matrix Examples")
    print("=" * 50)
    print("These examples demonstrate ITA Matrix-specific features.")
    print("ITA Matrix often provides more detailed flight information")
    print("and better search capabilities than Google Flights.")
    print()

    # Run examples
    await matrix_basic_search()
    await compare_matrix_vs_google()
    await matrix_advanced_search()
    await matrix_flexible_dates()
    await matrix_error_handling()

    print("\n✅ All ITA Matrix examples completed!")
    print("\nITA Matrix Benefits:")
    print("  • More detailed flight information")
    print("  • Better handling of complex routes")
    print("  • Advanced search filters")
    print("  • More accurate pricing")
    print("  • Better for travel agents and power users")


if __name__ == "__main__":
    asyncio.run(main())
