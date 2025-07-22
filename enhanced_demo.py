#!/usr/bin/env python3
"""
Enhanced example showcasing the improved flight data parsing capabilities.
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


async def enhanced_flight_search_demo():
    """Demonstrate enhanced flight search capabilities."""
    print("✈️  Enhanced Flight Data Parsing Demo")
    print("=" * 60)

    try:
        # Use ITA Matrix for better data quality
        async with ITAScrapper(
            headless=False,  # Show browser to see the parsing in action
            use_matrix=True,
            timeout=60000,
        ) as scrapper:
            print("🔍 Searching for flights with enhanced parsing...")

            # Search for flights with detailed parsing
            departure_date = date.today() + timedelta(days=30)
            return_date = departure_date + timedelta(days=7)

            result = await scrapper.search_flights(
                origin="JFK",
                destination="LHR",
                departure_date=departure_date,
                return_date=return_date,
                cabin_class=CabinClass.ECONOMY,
                adults=1,
                max_results=3,
            )

            print(f"\n✅ Found {len(result.flights)} flights")
            print(
                f"🛫 Route: {result.search_params.origin} → {result.search_params.destination}"
            )
            print(f"📅 Departure: {result.search_params.departure_date}")
            print(f"📅 Return: {result.search_params.return_date}")

            if result.flights:
                print("\n" + "=" * 60)
                print("📊 DETAILED FLIGHT ANALYSIS")
                print("=" * 60)

                # Show detailed flight information
                for i, flight in enumerate(result.flights, 1):
                    print(f"\n✈️  FLIGHT {i}")
                    print("-" * 30)
                    print(f"💰 Price: ${flight.price}")
                    print(
                        f"⏱️  Total Duration: {flight.total_duration_minutes // 60}h {flight.total_duration_minutes % 60}m"
                    )
                    print(f"🔄 Stops: {flight.stops}")
                    print(f"🏢 Airlines: {', '.join(flight.airlines)}")
                    print(f"🎫 Cabin Class: {flight.cabin_class.value}")
                    print(f"💼 Refundable: {'Yes' if flight.is_refundable else 'No'}")
                    print(
                        f"🎒 Baggage Included: {'Yes' if flight.baggage_included else 'No'}"
                    )

                    # Show detailed segment information
                    print(
                        f"\n📍 FLIGHT SEGMENTS ({len(flight.segments)} segment{'s' if len(flight.segments) != 1 else ''}):"
                    )
                    for j, segment in enumerate(flight.segments, 1):
                        print(
                            f"  Segment {j}: {segment.departure_airport.code} → {segment.arrival_airport.code}"
                        )
                        print(
                            f"    🏢 Airline: {segment.airline.name} ({segment.airline.code})"
                        )
                        print(f"    🎫 Flight: {segment.flight_number}")
                        print(
                            f"    🛫 Departure: {segment.departure_time.strftime('%I:%M %p on %b %d')}"
                        )
                        print(
                            f"    🛬 Arrival: {segment.arrival_time.strftime('%I:%M %p on %b %d')}"
                        )
                        print(
                            f"    ⏱️  Duration: {segment.duration_minutes // 60}h {segment.duration_minutes % 60}m"
                        )
                        if segment.stops > 0:
                            print(f"    🔄 Stops: {segment.stops}")
                        if segment.aircraft_type:
                            print(f"    ✈️  Aircraft: {segment.aircraft_type}")

                # Flight comparison analysis
                print(f"\n" + "=" * 60)
                print("📈 FLIGHT COMPARISON")
                print("=" * 60)

                if result.cheapest_flight:
                    cheapest = result.cheapest_flight
                    print(f"💰 CHEAPEST: ${cheapest.price}")
                    print(
                        f"   Duration: {cheapest.total_duration_minutes // 60}h {cheapest.total_duration_minutes % 60}m"
                    )
                    print(f"   Airlines: {', '.join(cheapest.airlines)}")
                    print(f"   Stops: {cheapest.stops}")

                if result.fastest_flight:
                    fastest = result.fastest_flight
                    print(
                        f"⚡ FASTEST: {fastest.total_duration_minutes // 60}h {fastest.total_duration_minutes % 60}m"
                    )
                    print(f"   Price: ${fastest.price}")
                    print(f"   Airlines: {', '.join(fastest.airlines)}")
                    print(f"   Stops: {fastest.stops}")

                # Price analysis
                prices = [float(f.price) for f in result.flights]
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)

                print(f"\n💰 PRICE ANALYSIS:")
                print(f"   Average: ${avg_price:.2f}")
                print(f"   Range: ${min_price:.2f} - ${max_price:.2f}")
                print(f"   Savings: ${max_price - min_price:.2f} (choosing cheapest)")

                # Duration analysis
                durations = [f.total_duration_minutes for f in result.flights]
                avg_duration = sum(durations) / len(durations)
                min_duration = min(durations)
                max_duration = max(durations)

                print(f"\n⏱️  DURATION ANALYSIS:")
                print(f"   Average: {avg_duration // 60:.0f}h {avg_duration % 60:.0f}m")
                print(
                    f"   Range: {min_duration // 60}h {min_duration % 60}m - {max_duration // 60}h {max_duration % 60}m"
                )
                print(
                    f"   Time saved: {(max_duration - min_duration) // 60}h {(max_duration - min_duration) % 60}m (choosing fastest)"
                )

                # Airlines analysis
                all_airlines = set()
                for flight in result.flights:
                    all_airlines.update(flight.airlines)

                print(f"\n🏢 AIRLINES FOUND:")
                print(f"   {', '.join(sorted(all_airlines))}")

            else:
                print("❌ No flights found")
                print("This might indicate:")
                print("• No flights available for the selected dates")
                print("• Parsing issues with the current page structure")
                print("• Anti-bot measures blocking the search")

    except ITAScrapperError as e:
        logger.error(f"Scrapper error: {e}")
        print(f"❌ Scraper error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")


async def compare_parsing_methods():
    """Compare the enhanced parsing with basic parsing."""
    print("\n" + "=" * 60)
    print("🔬 PARSING METHOD COMPARISON")
    print("=" * 60)

    try:
        # Test both ITA Matrix and Google Flights
        routes = [
            ("JFK", "LAX", "JFK to LAX (Domestic)"),
            ("NYC", "LON", "NYC to London (International)"),
        ]

        for origin, dest, description in routes:
            print(f"\n🛣️  Testing route: {description}")
            print("-" * 40)

            departure_date = date.today() + timedelta(days=45)

            # Test ITA Matrix (enhanced parsing)
            try:
                async with ITAScrapper(
                    headless=True, use_matrix=True, timeout=45000
                ) as scrapper:
                    result_ita = await scrapper.search_flights(
                        origin=origin,
                        destination=dest,
                        departure_date=departure_date,
                        cabin_class=CabinClass.ECONOMY,
                        adults=1,
                        max_results=2,
                    )

                    print(f"✅ ITA Matrix: {len(result_ita.flights)} flights found")
                    if result_ita.flights:
                        ita_cheapest = result_ita.cheapest_flight.price
                        print(f"   💰 Cheapest: ${ita_cheapest}")
                        print(
                            f"   🏢 Airlines: {', '.join(result_ita.flights[0].airlines)}"
                        )

            except Exception as e:
                print(f"❌ ITA Matrix failed: {e}")

            # Test Google Flights (basic parsing)
            try:
                async with ITAScrapper(
                    headless=True, use_matrix=False, timeout=45000
                ) as scrapper:
                    result_google = await scrapper.search_flights(
                        origin=origin,
                        destination=dest,
                        departure_date=departure_date,
                        cabin_class=CabinClass.ECONOMY,
                        adults=1,
                        max_results=2,
                    )

                    print(
                        f"✅ Google Flights: {len(result_google.flights)} flights found"
                    )
                    if result_google.flights:
                        google_cheapest = result_google.cheapest_flight.price
                        print(f"   💰 Cheapest: ${google_cheapest}")
                        print(
                            f"   🏢 Airlines: {', '.join(result_google.flights[0].airlines)}"
                        )

            except Exception as e:
                print(f"❌ Google Flights failed: {e}")

    except Exception as e:
        print(f"❌ Comparison failed: {e}")


async def main():
    """Run the enhanced flight search demo."""
    await enhanced_flight_search_demo()

    # Ask user if they want to compare parsing methods
    print(f"\n{'=' * 60}")
    user_input = input(
        "🔄 Do you want to compare ITA Matrix vs Google Flights parsing? (y/N): "
    )
    if user_input.lower() in ["y", "yes"]:
        await compare_parsing_methods()

    print(f"\n{'=' * 60}")
    print("🎉 Enhanced flight data parsing demo completed!")
    print("💡 Key improvements demonstrated:")
    print("   • Better price extraction from tooltips")
    print("   • Enhanced airline identification")
    print("   • Detailed flight segment information")
    print("   • Comprehensive flight analysis")
    print("   • Robust error handling")


if __name__ == "__main__":
    asyncio.run(main())
