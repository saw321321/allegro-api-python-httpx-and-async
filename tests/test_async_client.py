"""
Tests for async Allegro API client.
"""

import pytest
import inspect
import ast
import textwrap

from src.allegro_api.base import AsyncBaseAPIClient

from unittest.mock import patch, AsyncMock

from allegro_api import AsyncAllegroAPI
from allegro_api.auth import OAuth2Token, AsyncOAuth2Client
from allegro_api.exceptions import AuthenticationError
from allegro_api.resources import OffersResource, CategoriesResource, OrdersResource, UserResource

from allegro_api.resources.base import AsyncBaseResource


def _get_awaited_methods(func):
    """
    Zwraca listę metod które są awaitowane w funkcji.
    """
    source = inspect.getsource(func)
    source = textwrap.dedent(source)

    tree = ast.parse(source)

    awaited = []

    class AwaitVisitor(ast.NodeVisitor):
        def visit_Await(self, node):
            if isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Attribute):
                    awaited.append(node.value.func.attr)
            self.generic_visit(node)

    AwaitVisitor().visit(tree)

    return awaited

class TestAsyncAllegroAPI:
    """Test AsyncAllegroAPI client."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        api = AsyncAllegroAPI(
            client_id="test_client_id",
            client_secret="test_client_secret",
            access_token="test_token",
            refresh_token="refresh_token",
            sandbox=False,
        )
        
        assert api.client_id == "test_client_id"
        assert api.client_secret == "test_client_secret"
        assert api.access_token == "test_token"
        assert api.refresh_token == "refresh_token"
        assert not api.sandbox
        assert api.base_url == AsyncAllegroAPI.API_BASE_URL
        assert api.oauth_client is not None
        
        # Check resources initialization
        assert isinstance(api.offers, OffersResource)
        assert isinstance(api.categories, CategoriesResource)
        assert isinstance(api.orders, OrdersResource)
        assert isinstance(api.user, UserResource)
    
    def test_sandbox_initialization(self):
        """Test sandbox environment initialization."""
        api = AsyncAllegroAPI(sandbox=True)
        
        assert api.sandbox
        assert api.base_url == AsyncAllegroAPI.SANDBOX_API_BASE_URL
    
    def test_initialization_with_token_only(self):
        """Test initialization with access token only."""
        api = AsyncAllegroAPI(access_token="test_token")
        
        assert api.access_token == "test_token"
        assert api._token is not None
        assert api._token.access_token == "test_token"
        assert api.oauth_client is None  # No OAuth client without client_id
    
    @patch.object(AsyncOAuth2Client, "authenticate_with_device_flow", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_authenticate_device_flow(self, mock_device_flow):
        """Test device flow authentication."""
        mock_token = OAuth2Token(
            access_token="new_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="new_refresh_token",
        )
        mock_device_flow.return_value = mock_token
        
        api = AsyncAllegroAPI(client_id="test_client_id")
        token = await api.authenticate(method="device", open_browser=False)
        
        assert token == mock_token
        assert api.access_token == "new_token"
        assert api.refresh_token == "new_refresh_token"
        mock_device_flow.assert_awaited_once_with(False)
    
    @patch.object(AsyncOAuth2Client, "exchange_code_for_token", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_authenticate_code_flow(self, mock_exchange):
        """Test authorization code flow authentication."""
        mock_token = OAuth2Token(
            access_token="new_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="new_refresh_token",
        )
        mock_exchange.return_value = mock_token
        
        api = AsyncAllegroAPI(
            client_id="test_client_id",
            client_secret="test_client_secret",
        )
        token = await api.authenticate(method="code", code="test_code")
        
        assert token == mock_token
        assert api.access_token == "new_token"
        assert api.refresh_token == "new_refresh_token"
        mock_exchange.assert_awaited_once_with("test_code")
    
    @pytest.mark.asyncio
    async def test_authenticate_without_code(self):
        """Test code flow without authorization code."""
        api = AsyncAllegroAPI(client_id="test_client_id")
        
        with pytest.raises(ValueError, match="Authorization code required"):
            await api.authenticate(method="code")
    
    @pytest.mark.asyncio
    async def test_authenticate_invalid_method(self):
        """Test authentication with invalid method."""
        api = AsyncAllegroAPI(client_id="test_client_id")
        
        with pytest.raises(ValueError, match="Invalid authentication method"):
            await api.authenticate(method="invalid")
    
    @pytest.mark.asyncio
    async def test_authenticate_without_oauth_client(self):
        """Test authentication without OAuth client."""
        api = AsyncAllegroAPI()
        
        with pytest.raises(ValueError, match="OAuth2 client not initialized"):
            await api.authenticate()
    
    @patch.object(AsyncOAuth2Client, "refresh_token", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_refresh_access_token(self, mock_refresh):
        """Test refreshing access token."""
        mock_token = OAuth2Token(
            access_token="refreshed_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="new_refresh_token",
        )
        mock_refresh.return_value = mock_token
        
        api = AsyncAllegroAPI(
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token="old_refresh_token",
        )
        
        token = await api.refresh_access_token()
        
        assert token == mock_token
        assert api.access_token == "refreshed_token"
        assert api.refresh_token == "new_refresh_token"
        mock_refresh.assert_awaited_once_with("old_refresh_token")
    
    @pytest.mark.asyncio
    async def test_refresh_without_refresh_token(self):
        """Test refresh without refresh token."""
        api = AsyncAllegroAPI(access_token="test_token")
        
        with pytest.raises(ValueError, match="No refresh token available"):
            await api.refresh_access_token()
    
    @pytest.mark.asyncio
    async def test_ensure_authenticated_valid_token(self):
        """Test ensure_authenticated with valid token."""
        api = AsyncAllegroAPI(access_token="test_token")
        api._token = OAuth2Token(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600,
        )
        
        # Should not raise
        await api.ensure_authenticated()
    
    @pytest.mark.asyncio
    async def test_ensure_authenticated_no_token(self):
        """Test ensure_authenticated without token."""
        api = AsyncAllegroAPI()
        
        with pytest.raises(AuthenticationError, match="Not authenticated"):
            await api.ensure_authenticated()
    
    @patch.object(AsyncAllegroAPI, "refresh_access_token", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_ensure_authenticated_expired_token(self, mock_refresh):
        """Test ensure_authenticated with expired token."""
        api = AsyncAllegroAPI(
            client_id="test_client_id",
            access_token="expired_token",
            refresh_token="refresh_token",
        )
        api._token = OAuth2Token(
            access_token="expired_token",
            token_type="Bearer",
            expires_in=1,
            _created_at=0,
        )
        
        await api.ensure_authenticated()
        
        mock_refresh.assert_awaited_once()
    
    @patch.object(AsyncAllegroAPI, "get", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_search_offers(self, mock_get):
        """Test search_offers convenience method."""
        mock_get.return_value = {"offers": []}
        
        api = AsyncAllegroAPI()
        await api.search_offers(
            phrase="test",
            category_id="123",
            seller_id="456",
            parameters={"brand": "Test"},
            sort="price",
            include=["delivery"],
            exclude=["description"],
            limit=50,
            offset=10,
        )
        
        mock_get.assert_awaited_once_with(
            "/offers/listing",
            params={
                "phrase": "test",
                "category.id": "123",
                "seller.id": "456",
                "brand": "Test",
                "sort": "price",
                "include": "delivery",
                "exclude": "description",
                "limit": 50,
                "offset": 10,
            }
        )
    
    @patch.object(AsyncAllegroAPI, "get", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_get_offer(self, mock_get):
        """Test get_offer convenience method."""
        mock_get.return_value = {"id": "123"}
        
        api = AsyncAllegroAPI()
        await api.get_offer("123")
        
        mock_get.assert_awaited_once_with("/offers/123")
    
    @patch.object(AsyncAllegroAPI, "get", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_get_user_offers(self, mock_get):
        """Test get_user_offers convenience method."""
        mock_get.return_value = {"offers": []}
        
        api = AsyncAllegroAPI(access_token="test_token")
        api._token = OAuth2Token(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600,
        )
        
        await api.get_user_offers(
            offer_id="123",
            name="test",
            selling_format="BUY_NOW",
            publication_status=["ACTIVE"],
            selling_status=["ACTIVE"],
            external_id="ext123",
            limit=30,
            offset=5,
            sort="-startTime",
        )
        
        mock_get.assert_awaited_once_with(
            "/sale/offers",
            params={
                "offer.id": "123",
                "name": "test",
                "sellingMode.format": "BUY_NOW",
                "publication.status": ["ACTIVE"],
                "sellingMode.status": ["ACTIVE"],
                "external.id": "ext123",
                "limit": 30,
                "offset": 5,
                "sort": "-startTime",
            },
        )
    
    def test_get_authorization_url(self):
        """Test get_authorization_url method."""
        api = AsyncAllegroAPI(
            client_id="test_client_id",
            redirect_uri="http://localhost:8000",
        )
        
        url = api.get_authorization_url(state="test_state")
        
        assert "https://allegro.pl/auth/oauth/authorize" in url
        assert "client_id=test_client_id" in url
        assert "state=test_state" in url
#My new tests for errors
    def test_handle_response_is_sync(self):
        # test do błędu 2: _handle_response nie musi być asynchroniczny (przez co nie powinien)
        assert not inspect.iscoroutinefunction(
            AsyncBaseAPIClient._handle_response
        ), "_handle_response should not be async"



    def test_authenticate_does_not_await_sync_oauth_methods(self):
        """
        Error 1:
        authenticate() must not await synchronous OAuth methods.
        """

        awaited = _get_awaited_methods(AsyncAllegroAPI.authenticate)

        oauth_methods = {
            "authenticate_with_device_flow": AsyncOAuth2Client.authenticate_with_device_flow,
            "exchange_code_for_token": AsyncOAuth2Client.exchange_code_for_token,
            "client_credentials_flow": AsyncOAuth2Client.client_credentials_flow,
        }

        for name in awaited:
            if name in oauth_methods:

                method = oauth_methods[name]

                assert inspect.iscoroutinefunction(method), (
                    f"{name} is awaited in authenticate() but is not async"
                )


    def test_refresh_access_token_does_not_await_sync_oauth(self):
        """
        Error 1:
        refresh_access_token() must not await sync OAuth method.
        """

        awaited = _get_awaited_methods(AsyncAllegroAPI.refresh_access_token)

        if "refresh_token" in awaited:

            assert inspect.iscoroutinefunction(
                AsyncOAuth2Client.refresh_token
            ), "AsyncOAuth2Client.refresh_token is awaited but is not async"


    def test_ensure_authenticated_awaits_only_async_methods(self):
        """
        Error 1:
        ensure_authenticated() must only await async methods.
        """

        awaited = _get_awaited_methods(AsyncAllegroAPI.ensure_authenticated)

        if "refresh_access_token" in awaited:

            assert "refresh_token" not in awaited or inspect.iscoroutinefunction(
            AsyncOAuth2Client.refresh_token
        )


# Testy do tego czy AsyncBaseResource jest naprawde Async.
class DummyAsyncClient:
    async def get(self, *args, **kwargs):
        return {"items": []}

    async def ensure_authenticated(self):
        return None


def test_paginate_is_async():
    """
    AsyncBaseResource._paginate must be async.
    """
    assert inspect.iscoroutinefunction(
        AsyncBaseResource._paginate
    ), "_paginate should be async"


def test_ensure_authenticated_is_async():
    """
    AsyncBaseResource._ensure_authenticated must be async.
    """
    assert inspect.iscoroutinefunction(
        AsyncBaseResource._ensure_authenticated
    ), "_ensure_authenticated should be async"


@pytest.mark.asyncio
async def test_paginate_awaits_client_get():
    """
    _paginate must await client.get()
    """
    client = DummyAsyncClient()
    client.get = AsyncMock(return_value={"items": []})

    resource = AsyncBaseResource(client)

    await resource._paginate("/test")

    client.get.assert_awaited()


@pytest.mark.asyncio
async def test_ensure_authenticated_awaits_client():
    """
    _ensure_authenticated must await client.ensure_authenticated()
    """
    client = DummyAsyncClient()
    client.ensure_authenticated = AsyncMock()

    resource = AsyncBaseResource(client)

    await resource._ensure_authenticated()

    client.ensure_authenticated.assert_awaited_once()