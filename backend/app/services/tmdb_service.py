import requests
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self):
        self.api_key = settings.tmdb_api_key
        self.access_token = settings.tmdb_access_token
        self.base_url = settings.tmdb_base_url
    
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

    def get_similar_movies(self, movie_id: int) -> Dict:
        """Get similar movies based on movie ID"""
        return self._make_request(f"/movie/{movie_id}/similar")
    
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

# Create a singleton instance
tmdb_service = TMDBService()