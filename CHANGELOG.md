# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-02-14

### Added
- Garden bed management with space tracking
- Plant management with lifecycle states
- Harvest tracking and history
- Image upload support for plants
- Multi-architecture support (amd64, arm64, arm/v7)
- Database migrations system
- Comprehensive test suite with >85% coverage
- Documentation for development, testing, and deployment

### Changed
- Moved to PostgreSQL for improved reliability
- Enhanced plant spacing calculation system
- Added year filtering for plants

### Removed
- Removed deprecated season field from plants table