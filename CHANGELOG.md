# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-05

### Added
- Initial release with 100% Allegro REST API coverage
- Full OAuth2 authentication support (device flow, authorization code, client credentials)
- Automatic token refresh mechanism
- Comprehensive error handling with custom exceptions
- Type hints for all methods and parameters
- Support for both production and sandbox environments

### Features
- **Core Resources**:
  - Offers management (create, update, delete, publish, batch operations)
  - Categories browsing and parameter retrieval
  - Orders processing and shipment management
  - User information and settings

- **Financial Operations**:
  - Payment operations and history
  - Billing entries and commission refunds
  - Wallet management

- **Product Catalog**:
  - Product search and proposals
  - Compatibility lists
  - Product change proposals

- **Fulfillment (One Fulfillment)**:
  - Advance Ship Notices
  - Stock management
  - Parcel tracking
  - Removal requests

- **Marketing & Promotions**:
  - Loyalty programs and promotions
  - Badge campaigns
  - Allegro Prices
  - Offer bundles

- **Customer Service**:
  - Post-purchase issues
  - Dispute resolution
  - Message center
  - Contact management

- **Advanced Features**:
  - Offer variants
  - Multi-language translations
  - Price automation rules
  - Size tables

- **Auctions**:
  - Bidding operations
  - Auction monitoring
  - Watchlist management

- **Additional Resources**:
  - Marketplace information
  - Tax settings
  - Pricing calculations
  - Affiliate conversions

### Documentation
- Comprehensive README with examples
- API coverage documentation
- Code examples for common use cases