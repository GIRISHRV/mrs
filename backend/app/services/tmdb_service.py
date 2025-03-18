import requests
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from app.config import settings
import httpx
import logging
import aiohttp

logger = logging.getLogger(__name__)

load_dotenv()

class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self):
        self.api_key = settings.tmdb_api_key
        self.access_token = settings.tmdb_access_token
        self.base_url = settings.tmdb_base_url
        self.session = None
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """Make a request to the TMDB API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json;charset=utf-8"
        }
        
        # Add API key to params
        params = params or {}
        params["api_key"] = self.api_key
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"TMDB API error: {str(e)}")
            raise

    def get_popular_movies(self, page: int = 1) -> Dict:
        """Get popular movies"""
        return self._make_request("/movie/popular", {"page": page})
    
    def get_movie_details(self, movie_id: int) -> Dict:
        """Get details for a specific movie"""
        return self._make_request(f"/movie/{movie_id}")
    
    def search_movies(self, query: str, page: int = 1) -> Dict:
        """Search for movies by title"""
        params = {
            "query": query,
            "page": page,
            "include_adult": False
        }
        return self._make_request("/search/movie", params)
    
    def get_movie_recommendations(self, movie_id: int) -> Dict:
        """Get recommendations for a movie"""
        return self._make_request(f"/movie/{movie_id}/recommendations")
    
    def get_movie_genres(self) -> Dict:
        """Get all movie genres"""
        return self._make_request("/genre/movie/list")
    
    def discover_movies(self, params: Dict[str, Any]) -> Dict:
        """Discover movies with filters"""
        return self._make_request("/discover/movie", params)

    def get_similar_movies(self, movie_id: int, page: int = 1) -> Dict:
        """Get similar movies from TMDB API"""
        try:
            url = f"{self.base_url}/movie/{movie_id}/similar"
            params = {
                "api_key": self.api_key,
                "language": "en-US",
                "page": page
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"TMDB API error getting similar movies: {str(e)}")
            return {"results": [], "page": 1, "total_pages": 1, "total_results": 0}
    
    async def get_movies_by_genre(self, genre_id: int, page: int = 1) -> dict:
        """Get movies by genre ID from TMDB"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/discover/movie",
                    params={
                        "api_key": self.api_key,
                        "with_genres": genre_id,
                        "language": "en-US",
                        "sort_by": "popularity.desc",
                        "include_adult": False,
                        "page": page
                    }
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"TMDB API error: {str(e)}")
            raise Exception(f"Failed to fetch movies: {str(e)}")

    async def get_movie(self, movie_id: int) -> dict:
        """Get detailed information about a specific movie from TMDB."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            url = f"{self.base_url}/movie/{movie_id}"
            params = {
                "api_key": self.api_key,
                "language": "en-US"
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 404:
                    logger.warning(f"Movie {movie_id} not found on TMDB")
                    return None
                    
                if response.status != 200:
                    logger.error(f"TMDB API error: {response.status}")
                    return None
                    
                data = await response.json()
                return {
                    "tmdb_id": data["id"],
                    "title": data["title"],
                    "overview": data.get("overview", ""),
                    "poster_path": data.get("poster_path"),
                    "release_date": data.get("release_date"),
                    "vote_average": data.get("vote_average", 0),
                    "vote_count": data.get("vote_count", 0),
                    "popularity": data.get("popularity", 0),
                    "genres": data.get("genres", [])
                }

        except Exception as e:
            logger.error(f"Error fetching movie from TMDB: {str(e)}")
            return None

# Create a singleton instance
tmdb_service = TMDBService()