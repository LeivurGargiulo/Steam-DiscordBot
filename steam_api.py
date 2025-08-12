import requests
import time
import json
from typing import Dict, List, Optional, Any
from config import Config

class SteamAPI:
    """Steam API client for fetching game and user data"""
    
    def __init__(self):
        self.api_key = Config.STEAM_API_KEY
        self.base_url = Config.STEAM_API_BASE
        self.store_url = Config.STEAM_STORE_BASE
        self.community_url = Config.STEAM_COMMUNITY_BASE
        self.cache = {}
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Implement rate limiting to avoid API abuse"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < Config.RATE_LIMIT_DELAY:
            time.sleep(Config.RATE_LIMIT_DELAY - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            self._rate_limit()
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def get_user_profile(self, steam_id: str) -> Optional[Dict]:
        """Fetch user profile information"""
        url = f"{self.base_url}/ISteamUser/GetPlayerSummaries/v2/"
        params = {
            'key': self.api_key,
            'steamids': steam_id
        }
        
        data = self._make_request(url, params)
        if data and data.get('response', {}).get('players'):
            return data['response']['players'][0]
        return None
    
    def get_owned_games(self, steam_id: str) -> Optional[Dict]:
        """Fetch user's owned games"""
        url = f"{self.base_url}/IPlayerService/GetOwnedGames/v1/"
        params = {
            'key': self.api_key,
            'steamid': steam_id,
            'include_appinfo': 1,
            'include_played_free_games': 1
        }
        
        return self._make_request(url, params)
    
    def get_recent_games(self, steam_id: str) -> Optional[Dict]:
        """Fetch user's recently played games"""
        url = f"{self.base_url}/IPlayerService/GetRecentlyPlayedGames/v1/"
        params = {
            'key': self.api_key,
            'steamid': steam_id,
            'count': 5
        }
        
        return self._make_request(url, params)
    
    def get_player_achievements(self, steam_id: str, app_id: str) -> Optional[Dict]:
        """Fetch player achievements for a specific game"""
        url = f"{self.base_url}/ISteamUserStats/GetPlayerAchievements/v1/"
        params = {
            'key': self.api_key,
            'steamid': steam_id,
            'appid': app_id
        }
        
        return self._make_request(url, params)
    
    def get_game_schema(self, app_id: str) -> Optional[Dict]:
        """Fetch game schema (achievements, stats)"""
        url = f"{self.base_url}/ISteamUserStats/GetSchemaForGame/v2/"
        params = {
            'key': self.api_key,
            'appid': app_id
        }
        
        return self._make_request(url, params)
    
    def get_player_count(self, app_id: str) -> Optional[int]:
        """Fetch current player count for a game"""
        url = f"{self.base_url}/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
        params = {
            'appid': app_id
        }
        
        data = self._make_request(url, params)
        if data and data.get('response', {}).get('player_count') is not None:
            return data['response']['player_count']
        return None
    
    def get_friend_list(self, steam_id: str) -> Optional[Dict]:
        """Fetch user's friend list"""
        url = f"{self.base_url}/ISteamUser/GetFriendList/v1/"
        params = {
            'key': self.api_key,
            'steamid': steam_id,
            'relationship': 'friend'
        }
        
        return self._make_request(url, params)
    
    def get_user_level(self, steam_id: str) -> Optional[int]:
        """Fetch user's Steam level"""
        url = f"{self.base_url}/IPlayerService/GetSteamLevel/v1/"
        params = {
            'key': self.api_key,
            'steamid': steam_id
        }
        
        data = self._make_request(url, params)
        if data and data.get('response', {}).get('player_level') is not None:
            return data['response']['player_level']
        return None
    
    def get_badges(self, steam_id: str) -> Optional[Dict]:
        """Fetch user's badges"""
        url = f"{self.base_url}/IPlayerService/GetBadges/v1/"
        params = {
            'key': self.api_key,
            'steamid': steam_id
        }
        
        return self._make_request(url, params)
    
    def get_game_details(self, app_id: str) -> Optional[Dict]:
        """Fetch game details from Steam Store API"""
        url = f"{self.store_url}/api/appdetails"
        params = {
            'appids': app_id
        }
        
        data = self._make_request(url, params)
        if data and data.get(app_id, {}).get('success'):
            return data[app_id]['data']
        return None
    
    def get_featured_games(self) -> Optional[Dict]:
        """Fetch featured/top games"""
        url = f"{self.store_url}/api/featured"
        
        return self._make_request(url)
    
    def get_app_news(self, app_id: str, count: int = 5) -> Optional[Dict]:
        """Fetch news for a specific game"""
        url = f"{self.base_url}/ISteamNews/GetNewsForApp/v2/"
        params = {
            'appid': app_id,
            'count': count,
            'maxlength': 300
        }
        
        return self._make_request(url, params)
    
    def get_wishlist(self, steam_id: str) -> Optional[List]:
        """Fetch user's wishlist (requires public profile)"""
        # This is a simplified version - Steam doesn't provide a direct API for wishlists
        # We'll return a placeholder for now
        return None
    
    def get_random_game(self) -> Optional[Dict]:
        """Get a random popular game"""
        # Get featured games and pick a random one
        featured = self.get_featured_games()
        if featured and featured.get('featured_win'):
            import random
            games = featured['featured_win'].get('items', [])
            if games:
                return random.choice(games)
        return None
    
    def get_price_history(self, app_id: str) -> Optional[Dict]:
        """Get price history for a game (placeholder)"""
        # Steam doesn't provide price history via API
        # This would require integration with third-party services
        return {
            'app_id': app_id,
            'message': 'Price history requires third-party API integration (e.g., SteamDB, SteamSpy)'
        }
    
    def get_game_recommendations(self, steam_id: str) -> Optional[List]:
        """Get game recommendations based on user library"""
        # This is a simplified recommendation system
        owned_games = self.get_owned_games(steam_id)
        if owned_games and owned_games.get('response', {}).get('games'):
            # Get popular games and filter out owned ones
            featured = self.get_featured_games()
            if featured and featured.get('featured_win'):
                owned_app_ids = {game['appid'] for game in owned_games['response']['games']}
                recommendations = []
                for game in featured['featured_win'].get('items', []):
                    if game.get('id') not in owned_app_ids:
                        recommendations.append(game)
                    if len(recommendations) >= 5:
                        break
                return recommendations
        return None