# API Coverage

This library provides 100% coverage of the Allegro REST API. Below is a complete list of all implemented resources and their methods.

## Core Resources

### Offers (`api.offers`)
- List, get, create, update, delete offers
- Publish/unpublish offers
- Update prices and quantities
- Manage offer events
- Batch operations
- Product-based offer creation
- Tags and promotions management

### Categories (`api.categories`)
- Browse category tree
- Get category parameters
- Search categories
- Get category suggestions

### Orders (`api.orders`)
- List and get orders
- Order events monitoring
- Shipment management
- Invoice handling
- Refund processing
- Customer returns

### User (`api.user`)
- User information and ratings
- Return policies
- Warranties
- Shipping rates
- Disputes
- Messages

## Financial Resources

### Payments (`api.payments`)
- Payment operations and history
- Refund management
- Surcharges
- Wallet operations

### Billing (`api.billing`)
- Billing entries
- Commission refunds
- Account balance
- Financial operations history

## Product Catalog

### Products (`api.products`)
- Product search and details
- Product proposals
- Product matching
- Compatibility lists
- Change proposals

## Fulfillment

### Fulfillment (`api.fulfillment`)
- Advance Ship Notices
- Stock levels and movements
- Parcel tracking
- Product management
- Removal requests

## Marketing & Promotions

### Promotions (`api.promotions`)
- Loyalty promotions
- Badge campaigns
- Allegro Prices
- AlleDiscount
- Offer bundles

## Customer Service

### Customer Service (`api.customer_service`)
- Post-purchase issues
- Dispute resolution
- Message center
- Contact management

## Advanced Features

### Advanced Offers (`api.advanced_offers`)
- Offer variants
- Offer translations
- Price automation
- Compatibility lists
- Size tables

### Auctions (`api.auctions`)
- Bidding operations
- Auction monitoring
- Watchlist management

## Other Resources

### Misc (`api.misc`)
- Marketplace information
- Charity campaigns
- Public user data
- Additional services
- Tax settings
- Pricing calculations
- Responsible persons/producers
- Affiliate conversions

## Usage Examples

```python
# Access any resource through the main API client
api = AllegroAPI(client_id="your_client_id")
api.authenticate()

# Use any resource
products = api.products.search(phrase="laptop")
stock = api.fulfillment.get_stock_levels()
promotions = api.promotions.get_badge_campaigns()
disputes = api.customer_service.get_disputes()
```

All methods include:
- Type hints for parameters and return values
- Comprehensive docstrings
- Automatic error handling
- Support for filtering and pagination where applicable