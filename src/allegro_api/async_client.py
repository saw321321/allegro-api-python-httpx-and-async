"""
Main Allegro API Async client.
"""

from typing import Optional, Dict, Any, List
import logging
import httpx

from allegro_api.exceptions import AuthenticationError
from .base import AsyncBaseAPIClient
from .auth import AsyncOAuth2Client, OAuth2Token
from .resources.offers import OffersResource
from .resources.categories import CategoriesResource
from .resources.orders import OrdersResource
from .resources.user import UserResource
from .resources.payments import PaymentsResource
from .resources.billing import BillingResource
from .resources.products import ProductsResource
from .resources.fulfillment import FulfillmentResource
from .resources.promotions import PromotionsResource
from .resources.customer_service import CustomerServiceResource
from .resources.advanced_offers import AdvancedOffersResource
from .resources.auctions import AuctionsResource
from .resources.misc import MiscResource


logger = logging.getLogger(__name__)


class AsyncAllegroAPI(AsyncBaseAPIClient):
    """
    Main client for Allegro REST API.
    
    Example:
        >>> from allegro_api import AsyncAllegroAPI
        >>> api = AsyncAllegroAPI(client_id="your_client_id")
        >>> await api.authenticate()  # Follow device flow
        >>> user = await api.user.get_me()
    """
    
    API_BASE_URL = "https://api.allegro.pl/"
    SANDBOX_API_BASE_URL = "https://api.allegro.pl.allegrosandbox.pl/"
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        sandbox: bool = False,
        redirect_uri: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        Initialize Allegro API client.
        
        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            access_token: Existing access token
            refresh_token: Existing refresh token
            sandbox: Whether to use sandbox environment
            **kwargs: Additional arguments for BaseAPIClient
        """
        base_url = self.SANDBOX_API_BASE_URL if sandbox else self.API_BASE_URL
        super().__init__(base_url, access_token, sandbox)
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        
        # Initialize OAuth2 client if credentials provided
        self.oauth_client: Optional[AsyncOAuth2Client] = None
        if client_id:
            self.oauth_client = AsyncOAuth2Client(
                client_id=client_id,
                client_secret=client_secret,
                sandbox=sandbox,
            )
        
        # Current token object
        self._token: Optional[OAuth2Token] = None
        if access_token:
            self._token = OAuth2Token(
                access_token=access_token,
                token_type="Bearer",
                expires_in=3600,  # Default expiry
                refresh_token=refresh_token,
            )
        
        # Initialize resources
        self._init_resources()
    
    def _init_resources(self) -> None: #no async needed but need to change to async resources
        """Initialize API resources."""
        self.offers = OffersResource(self)
        self.categories = CategoriesResource(self)
        self.orders = OrdersResource(self)
        self.user = UserResource(self)
        self.payments = PaymentsResource(self)
        self.billing = BillingResource(self)
        self.products = ProductsResource(self)
        self.fulfillment = FulfillmentResource(self)
        self.promotions = PromotionsResource(self)
        self.customer_service = CustomerServiceResource(self)
        self.advanced_offers = AdvancedOffersResource(self)
        self.auctions = AuctionsResource(self)
        self.misc = MiscResource(self)
    
    async def authenticate( 
        self,
        method: str = "device",
        code: Optional[str] = None,
        open_browser: bool = True,
    ) -> OAuth2Token:  #NEEDS TO BE ASYNC
        """
        Authenticate with Allegro API.
        
        Args:
            method: Authentication method ("device", "code", "client_credentials")
            code: Authorization code (for "code" method)
            open_browser: Whether to open browser (for "device" method)
            
        Returns:
            OAuth2Token object
            
        Raises:
            ValueError: If invalid method or missing requirements
            AuthenticationError: If authentication fails
        """
        if not self.oauth_client:
            raise ValueError("OAuth2 client not initialized. Provide client_id.")
        
        if method == "device":
            token = await self.oauth_client.authenticate_with_device_flow(open_browser)
        elif method == "code":
            if not code:
                raise ValueError("Authorization code required for code flow")
            token = await self.oauth_client.exchange_code_for_token(code)
        elif method == "client_credentials":
            token = await self.oauth_client.client_credentials_flow()
        else:
            raise ValueError(f"Invalid authentication method: {method}")
        
        self._token = token
        self.set_access_token(token.access_token)
        if token.refresh_token:
            self.refresh_token = token.refresh_token
        
        return token
    
    async def refresh_access_token(self) -> OAuth2Token:  # NEEDS TO BE ASYNC
        """
        Refresh access token using refresh token.
        
        Returns:
            New OAuth2Token object
            
        Raises:
            ValueError: If no refresh token available
            AuthenticationError: If refresh fails
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        if not self.oauth_client:
            raise ValueError("OAuth2 client not initialized")
        
        token = await self.oauth_client.refresh_token(self.refresh_token)
        
        self._token = token
        self.set_access_token(token.access_token)
        if token.refresh_token:
            self.refresh_token = token.refresh_token
        
        return token
    
    async def ensure_authenticated(self) -> None:  # NEEDS TO BE ASYNC
        """
        Ensure client is authenticated, refreshing token if needed.
        
        Raises:
            AuthenticationError: If not authenticated and cannot refresh
        """
        if not self.access_token:
            raise AuthenticationError("Not authenticated. Call authenticate() first.")
        
        if self._token and self._token.is_expired and self.refresh_token:
            logger.info("Access token expired, refreshing...")
            await self.refresh_access_token()
    
    
    def get_authorization_url(self, state: Optional[str] = None) -> str: # no async needed
        """
        Get authorization URL for web flow.
        
        Args:
            state: Optional state parameter
            
        Returns:
            Authorization URL
            
        Raises:
            ValueError: If OAuth2 client not initialized
        """
        if not self.oauth_client:
            raise ValueError("OAuth2 client not initialized")
        
        return self.oauth_client.get_authorization_url(state)
    
    # Convenience methods for common operations
    
    async def search_offers(
        self,
        phrase: Optional[str] = None,
        category_id: Optional[str] = None,
        seller_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:  # NEEDS TO BE ASYNC
        """
        Search for offers.
        
        Args:
            phrase: Search phrase
            category_id: Category ID to filter by
            seller_id: Seller ID to filter by
            parameters: Additional search parameters
            sort: Sort order
            include: Fields to include
            exclude: Fields to exclude
            limit: Number of results
            offset: Results offset
            
        Returns:
            Search results
        """
        params = {
            "phrase": phrase,
            "category.id": category_id,
            "seller.id": seller_id,
            "limit": limit,
            "offset": offset,
        }
        
        if parameters:
            params.update(parameters)
        
        if sort:
            params["sort"] = sort
        
        if include:
            params["include"] = ",".join(include)
        
        if exclude:
            params["exclude"] = ",".join(exclude)
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return await self.get("/offers/listing", params=params)
    
    async def get_offer(self, offer_id: str) -> Dict[str, Any]: # NEEDS TO BE ASYNC
        """
        Get public offer details.
        
        Args:
            offer_id: Offer ID
            
        Returns:
            Offer details
        """
        return await self.get(f"/offers/{offer_id}")
    
    async def get_user_offers(  # NEEDS TO BE ASYNC
        self,
        offer_id: Optional[str] = None,
        name: Optional[str] = None,
        selling_format: Optional[str] = None,
        publication_status: Optional[List[str]] = None,
        selling_status: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get user's offers.
        
        Args:
            offer_id: Filter by offer ID
            name: Filter by name
            selling_format: Filter by format (BUY_NOW, AUCTION, ADVERTISEMENT)
            publication_status: Filter by publication status
            selling_status: Filter by selling status
            external_id: Filter by external ID
            limit: Number of results
            offset: Results offset
            sort: Sort order
            
        Returns:
            User's offers
        """
        await self.ensure_authenticated()
        
        params = {
            "offer.id": offer_id,
            "name": name,
            "sellingMode.format": selling_format,
            "publication.status": publication_status,
            "sellingMode.status": selling_status,
            "external.id": external_id,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        }
        
        # Handle list parameters
        if publication_status:
            params["publication.status"] = publication_status
        if selling_status:
            params["sellingMode.status"] = selling_status
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return await self.get("/sale/offers", params=params)