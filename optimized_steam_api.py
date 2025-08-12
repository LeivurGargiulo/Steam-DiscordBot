"""
Optimized Steam API Client

This module provides an enhanced Steam API client with:
- Async HTTP requests for better performance
- Comprehensive error handling and retry logic
- Intelligent caching integration
- Rate limiting and backoff strategies
- Type hints for better code safety
- Detailed logging and monitoring
"""

import aiohttp
import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
from urllib.parse import urlencode

from optimized_config import Config

logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """Structured API response with metadata"""
    data: Any
    status_code: int
    headers: Dict[str, str]
    response_time: float
    cached: bool = False
    retry_count: int = 0

class SteamAPIError(Exception):
    """Base exception for Steam API errors"""
    pass

class SteamAPIRateLimitError(SteamAPIError):
    """Exception raised when rate limited by Steam API"""
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"Rate limited by Steam API. Retry after {retry_after} seconds")

class SteamAPINotFoundError(SteamAPIError):
    """Exception raised when resource not found"""
    pass

class SteamAPITimeoutError(SteamAPIError):
    """Exception raised when request times out"""
    pass

class OptimizedSteamAPI:
    """Enhanced Steam API client with async support and advanced features"""
    
    def __init__(self, cache_manager=None, session: Optional[aiohttp.ClientSession] = None):
        self.config = Config.get_steam_api_params()
        self.cache_manager = cache_manager
        self.session = session
        
        # Request tracking
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        
        # Rate limiting
        self.last_request_time = 0.0
        self.request_queue = asyncio.Queue()
        
        # Circuit breaker
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.circuit_open = False
        self.circuit_timeout = 60  # seconds
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with optimal settings"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(
                total=self.config['timeout'],
                connect=10,
                sock_read=30
            )
            
            connector = aiohttp.TCPConnector(
                limit=self.config.get('max_concurrent_requests', 10),
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    'User-Agent': 'SteamBot/1.0 (Discord Bot)',
                    'Accept': 'application/json'
                }
            )
        
        return self.session
    
    async def _rate_limit_delay(self):
        """Implement rate limiting to avoid API abuse"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Minimum delay between requests
        min_delay = 0.1  # 100ms
        if time_since_last < min_delay:
            await asyncio.sleep(min_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    async def _check_circuit_breaker(self):
        """Check if circuit breaker is open"""
        if self.circuit_open:
            if time.time() - self.last_failure_time > self.circuit_timeout:
                self.circuit_open = False
                self.failure_count = 0
                logger.info("Circuit breaker closed")
            else:
                raise SteamAPIError("Circuit breaker is open - too many recent failures")
    
    async def _make_request_with_retry(
        self, 
        url: str, 
        params: Dict = None, 
        method: str = 'GET',
        headers: Dict = None
    ) -> APIResponse:
        """Make HTTP request with retry logic and error handling"""
        await self._check_circuit_breaker()
        await self._rate_limit_delay()
        
        session = await self._get_session()
        start_time = time.time()
        
        for attempt in range(self.config['retry_attempts'] + 1):
            try:
                # Prepare request
                request_headers = headers or {}
                request_params = params or {}
                
                # Add API key if not present
                if 'key' not in request_params and self.config['api_key']:
                    request_params['key'] = self.config['api_key']
                
                # Make request
                async with session.request(
                    method, 
                    url, 
                    params=request_params, 
                    headers=request_headers
                ) as response:
                    
                    response_time = time.time() - start_time
                    self.total_response_time += response_time
                    self.request_count += 1
                    
                    # Handle different response codes
                    if response.status == 200:
                        self.failure_count = 0  # Reset failure count on success
                        data = await response.json()
                        
                        return APIResponse(
                            data=data,
                            status_code=response.status,
                            headers=dict(response.headers),
                            response_time=response_time,
                            retry_count=attempt
                        )
                    
                    elif response.status == 404:
                        raise SteamAPINotFoundError(f"Resource not found: {url}")
                    
                    elif response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limited by Steam API. Retry after {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    elif response.status >= 500:
                        # Server error - retry
                        logger.warning(f"Server error {response.status} on attempt {attempt + 1}")
                        if attempt < self.config['retry_attempts']:
                            await asyncio.sleep(self.config['retry_delay'] * (2 ** attempt))
                            continue
                        else:
                            response.raise_for_status()
                    
                    else:
                        response.raise_for_status()
                
            except asyncio.TimeoutError:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt < self.config['retry_attempts']:
                    await asyncio.sleep(self.config['retry_delay'] * (2 ** attempt))
                    continue
                else:
                    raise SteamAPITimeoutError(f"Request timed out after {self.config['timeout']} seconds")
            
            except aiohttp.ClientError as e:
                logger.warning(f"HTTP client error on attempt {attempt + 1}: {e}")
                if attempt < self.config['retry_attempts']:
                    await asyncio.sleep(self.config['retry_delay'] * (2 ** attempt))
                    continue
                else:
                    raise SteamAPIError(f"HTTP request failed: {e}")
        
        # If we get here, all retries failed
        self.failure_count += 1
        if self.failure_count >= 5:  # Open circuit breaker after 5 consecutive failures
            self.circuit_open = True
            self.last_failure_time = time.time()
            logger.error("Circuit breaker opened due to repeated failures")
        
        self.error_count += 1
        raise SteamAPIError("All retry attempts failed")
    
    def _generate_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key for request"""
        key_data = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_user_profile(self, steam_id: str) -> Optional[Dict]:
        """Get Steam user profile with caching"""
        endpoint = "ISteamUser/GetPlayerSummaries/v2"
        params = {'steamids': steam_id}
        
        # Check cache first
        if self.cache_manager:
            cache_key = self._generate_cache_key(endpoint, params)
            cached = await self.cache_manager.get("steam_profile", cache_key)
            if cached:
                logger.debug(f"Cache hit for profile {steam_id}")
                return cached
        
        try:
            url = f"{self.config['base_url']}/{endpoint}/"
            response = await self._make_request_with_retry(url, params)
            
            if response.data and response.data.get('response', {}).get('players'):
                profile = response.data['response']['players'][0]
                
                # Cache the result
                if self.cache_manager:
                    await self.cache_manager.set(
                        "steam_profile", 
                        profile, 
                        ttl=Config.cache.profile_ttl,
                        cache_key=cache_key
                    )
                
                logger.info(f"Successfully fetched profile for {steam_id} in {response.response_time:.2f}s")
                return profile
            
            logger.warning(f"No profile data found for {steam_id}")
            return None
            
        except SteamAPIError as e:
            logger.error(f"Failed to fetch profile for {steam_id}: {e}")
            return None
    
    async def get_game_details(self, app_id: str) -> Optional[Dict]:
        """Get game details with caching"""
        endpoint = "appdetails"
        params = {'appids': app_id}
        
        # Check cache first
        if self.cache_manager:
            cache_key = self._generate_cache_key(endpoint, params)
            cached = await self.cache_manager.get("steam_game", cache_key)
            if cached:
                logger.debug(f"Cache hit for game {app_id}")
                return cached
        
        try:
            url = f"{self.config['store_url']}/api/{endpoint}"
            response = await self._make_request_with_retry(url, params)
            
            if response.data and response.data.get(app_id, {}).get('success'):
                game_data = response.data[app_id]['data']
                
                # Cache the result
                if self.cache_manager:
                    await self.cache_manager.set(
                        "steam_game", 
                        game_data, 
                        ttl=Config.cache.game_ttl,
                        cache_key=cache_key
                    )
                
                logger.info(f"Successfully fetched game details for {app_id} in {response.response_time:.2f}s")
                return game_data
            
            logger.warning(f"No game data found for {app_id}")
            return None
            
        except SteamAPIError as e:
            logger.error(f"Failed to fetch game details for {app_id}: {e}")
            return None
    
    async def get_player_count(self, app_id: str) -> Optional[int]:
        """Get current player count with short-term caching"""
        endpoint = "ISteamUserStats/GetNumberOfCurrentPlayers/v1"
        params = {'appid': app_id}
        
        # Check cache first
        if self.cache_manager:
            cache_key = self._generate_cache_key(endpoint, params)
            cached = await self.cache_manager.get("steam_playercount", cache_key)
            if cached:
                logger.debug(f"Cache hit for player count {app_id}")
                return cached
        
        try:
            url = f"{self.config['base_url']}/{endpoint}/"
            response = await self._make_request_with_retry(url, params)
            
            if response.data and response.data.get('response', {}).get('player_count') is not None:
                count = response.data['response']['player_count']
                
                # Cache the result with short TTL
                if self.cache_manager:
                    await self.cache_manager.set(
                        "steam_playercount", 
                        count, 
                        ttl=Config.cache.player_count_ttl,
                        cache_key=cache_key
                    )
                
                logger.info(f"Successfully fetched player count for {app_id}: {count} in {response.response_time:.2f}s")
                return count
            
            logger.warning(f"No player count data found for {app_id}")
            return None
            
        except SteamAPIError as e:
            logger.error(f"Failed to fetch player count for {app_id}: {e}")
            return None
    
    async def get_owned_games(self, steam_id: str) -> Optional[Dict]:
        """Get user's owned games"""
        endpoint = "IPlayerService/GetOwnedGames/v1"
        params = {
            'steamid': steam_id,
            'include_appinfo': 1,
            'include_played_free_games': 1
        }
        
        try:
            url = f"{self.config['base_url']}/{endpoint}/"
            response = await self._make_request_with_retry(url, params)
            
            if response.data and response.data.get('response'):
                logger.info(f"Successfully fetched owned games for {steam_id} in {response.response_time:.2f}s")
                return response.data['response']
            
            logger.warning(f"No owned games data found for {steam_id}")
            return None
            
        except SteamAPIError as e:
            logger.error(f"Failed to fetch owned games for {steam_id}: {e}")
            return None
    
    async def get_recent_games(self, steam_id: str) -> Optional[Dict]:
        """Get user's recently played games"""
        endpoint = "IPlayerService/GetRecentlyPlayedGames/v1"
        params = {
            'steamid': steam_id,
            'count': 10
        }
        
        try:
            url = f"{self.config['base_url']}/{endpoint}/"
            response = await self._make_request_with_retry(url, params)
            
            if response.data and response.data.get('response'):
                logger.info(f"Successfully fetched recent games for {steam_id} in {response.response_time:.2f}s")
                return response.data['response']
            
            logger.warning(f"No recent games data found for {steam_id}")
            return None
            
        except SteamAPIError as e:
            logger.error(f"Failed to fetch recent games for {steam_id}: {e}")
            return None
    
    async def get_player_achievements(self, steam_id: str, app_id: str) -> Optional[Dict]:
        """Get player achievements for a specific game"""
        endpoint = "ISteamUserStats/GetPlayerAchievements/v1"
        params = {
            'steamid': steam_id,
            'appid': app_id
        }
        
        try:
            url = f"{self.config['base_url']}/{endpoint}/"
            response = await self._make_request_with_retry(url, params)
            
            if response.data and response.data.get('playerstats'):
                logger.info(f"Successfully fetched achievements for {steam_id} in game {app_id} in {response.response_time:.2f}s")
                return response.data['playerstats']
            
            logger.warning(f"No achievements data found for {steam_id} in game {app_id}")
            return None
            
        except SteamAPIError as e:
            logger.error(f"Failed to fetch achievements for {steam_id} in game {app_id}: {e}")
            return None
    
    async def get_game_schema(self, app_id: str) -> Optional[Dict]:
        """Get game schema (achievements, stats)"""
        endpoint = "ISteamUserStats/GetSchemaForGame/v2"
        params = {'appid': app_id}
        
        try:
            url = f"{self.config['base_url']}/{endpoint}/"
            response = await self._make_request_with_retry(url, params)
            
            if response.data and response.data.get('game'):
                logger.info(f"Successfully fetched game schema for {app_id} in {response.response_time:.2f}s")
                return response.data['game']
            
            logger.warning(f"No game schema found for {app_id}")
            return None
            
        except SteamAPIError as e:
            logger.error(f"Failed to fetch game schema for {app_id}: {e}")
            return None
    
    async def get_top_games(self, limit: int = 10) -> Optional[List[Dict]]:
        """Get top games by player count"""
        try:
            # This would require a different approach as Steam doesn't provide a direct API
            # We could implement this by fetching popular games from the store
            logger.info(f"Fetching top {limit} games")
            
            # Placeholder implementation
            return []
            
        except SteamAPIError as e:
            logger.error(f"Failed to fetch top games: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        return {
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': self.error_count / self.request_count if self.request_count > 0 else 0,
            'average_response_time': avg_response_time,
            'circuit_breaker_open': self.circuit_open,
            'failure_count': self.failure_count
        }
    
    async def close(self):
        """Close the API client and cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Steam API client session closed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()