# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2025-08-15

### Changed
- Version bump to 0.1.2

## [0.1.1] - 2025-08-15

### Added
- Enhanced parsing capabilities and bug fixes

## [0.1.0] - 2025-07-21

### Added
- Initial release of ITA Scrapper
- Core scraping functionality for ITA Matrix
- Support for round-trip and one-way flights
- Pydantic models for type-safe data handling
- Comprehensive utility functions for parsing flight data
- CLI interface for command-line usage
- Full test suite with pytest
- Support for multiple cabin classes
- Async/await support with context managers
- Robust error handling and logging

### Features
- Search flights by origin/destination airports
- Support for flexible date searches
- Parse prices, durations, times, and airport codes
- Validate travel dates and airport codes
- Format flight durations in human-readable format
- Handle multiple passenger types (adults, children, infants)
- Headless and non-headless browser modes
- JSON and table output formats for CLI

### Dependencies
- playwright >= 1.40.0
- pydantic >= 2.0.0  
- python-dateutil >= 2.8.0
- typing-extensions >= 4.0.0
- click >= 8.0.0

[Unreleased]: https://github.com/yourusername/ita-scrapper/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/yourusername/ita-scrapper/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/yourusername/ita-scrapper/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/yourusername/ita-scrapper/releases/tag/v0.1.0
