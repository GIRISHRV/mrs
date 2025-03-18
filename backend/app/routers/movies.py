from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.models.database import get_db
from app.models.user import User
from app.models.movie import Movie, Genre
from app.services.tmdb_service import tmdb_service
from app.utils.auth import get_current_user
from app.schemas.schemas import MovieResponse, GenreResponse
from datetime import datetime
import logging

router = APIRouter(prefix="/movies", tags=["Movies"])
logger = logging.getLogger(__name__)

@router.get("/popular", response_model=List[MovieResponse])
async def get_popular_movies(
    page: int = Query(1, ge=1), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get popular movies from TMDB"""
    response = tmdb_service.get_popular_movies(page)
    
    # Process and save movies to the database
    movies = []
    for movie_data in response.get("results", []):
        # Check if movie exists in database
        db_movie = db.query(Movie).filter(Movie.tmdb_id == movie_data["id"]).first()
        
        if not db_movie:
            # Create new movie record
            db_movie = Movie(
                tmdb_id=movie_data["id"],
                title=movie_data["title"],
                overview=movie_data["overview"],
                release_date=datetime.strptime(movie_data["release_date"], "%Y-%m-%d") if movie_data.get("release_date") else None,
                poster_path=movie_data["poster_path"],
                vote_average=movie_data["vote_average"],
                vote_count=movie_data["vote_count"],
                popularity=movie_data["popularity"],
            )
            
            # Add genres
            for genre_id in movie_data.get("genre_ids", []):
                genre = db.query(Genre).filter(Genre.id == genre_id).first()
                if genre:
                    db_movie.genres.append(genre)
                    
            db.add(db_movie)
            db.commit()
            db.refresh(db_movie)
        
        movies.append(db_movie)
    
    return movies

@router.get("/search")
async def search_movies(
    query: str = Query(...),  # Make it required
    page: int = Query(1, ge=1)
):
    """Search for movies by title"""
    try:
        logger.info(f"Search request received - Query: '{query}', Page: {page}")
        
        # Handle empty query case
        if not query.strip():
            logger.warning("Empty search query received")
            return {
                "page": 1,
                "results": [],
                "total_pages": 0,
                "total_results": 0
            }
            
        response = tmdb_service.search_movies(query.strip(), page)
        logger.info(f"Search response received with {len(response.get('results', []))} results")
        
        # Filter out movies without poster path
        filtered_results = [
            movie for movie in response.get("results", [])
            if movie.get("poster_path")
        ]
        
        return {
            "page": response.get("page", 1),
            "results": filtered_results,
            "total_pages": response.get("total_pages", 1),
            "total_results": response.get("total_results", 0)
        }
        
    except Exception as e:
        logger.error(f"Error searching movies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/genres", response_model=List[GenreResponse])
async def get_genres(db: Session = Depends(get_db)):
    """Get all movie genres"""
    genres = db.query(Genre).all()
    
    if not genres:
        # If genres don't exist in the database, fetch from TMDB API
        response = tmdb_service.get_movie_genres()
        
        for genre_data in response.get("genres", []):
            genre = Genre(id=genre_data["id"], name=genre_data["name"])
            db.add(genre)
        
        db.commit()
        genres = db.query(Genre).all()
    
    return genres

@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie_details(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific movie"""
    # Check if movie exists in database
    db_movie = db.query(Movie).filter(Movie.tmdb_id == movie_id).first()
    
    if not db_movie:
        # If not in database, fetch from TMDB API
        movie_data = tmdb_service.get_movie_details(movie_id)
        
        # Create new movie record (similar to popular movies)
        # ...
        
    return db_movie

@router.post("/{movie_id}/rate", response_model=dict)
async def rate_movie(
    movie_id: int,
    rating: int = Query(..., ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rate a movie (1-10 scale)"""
    # Check if movie exists in database
    db_movie = db.query(Movie).filter(Movie.tmdb_id == movie_id).first()
    
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Record the rating in the user_movie table
    # Implementation depends on how the many-to-many relationship is set up
    # ...
    
    return {"success": True, "message": "Rating saved successfully"}

@router.post("/{movie_id}/rate")
async def rate_movie(
    movie_id: int,
    rating: int = Body(..., ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Save rating to database
        user_movie = db.query(user_movie).filter(
            user_movie.c.user_id == current_user.id,
            user_movie.c.movie_id == movie_id
        ).first()

        if user_movie:
            # Update existing rating
            user_movie.rating = rating
        else:
            # Add new rating
            db.execute(
                user_movie.insert().values(
                    user_id=current_user.id,
                    movie_id=movie_id,
                    rating=rating
                )
            )
        
        db.commit()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException
from typing import Dict, List
from ..services.tmdb_service import tmdb_service

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("/popular")
async def get_popular_movies(page: int = 1):
    try:
        print(f"Fetching popular movies for page {page}")
        response = tmdb_service.get_popular_movies(page)
        print(f"TMDB Response: {response}")
        
        # Return only the results array
        return {
            "movies": response.get("results", [])
        }
    except Exception as e:
        print(f"Error in get_popular_movies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/genres")
async def get_genres():
    try:
        print("Fetching movie genres")
        response = tmdb_service.get_movie_genres()
        print(f"TMDB Genres Response: {response}")
        
        # Return only the genres array
        return {
            "genres": response.get("genres", [])
        }
    except Exception as e:
        print(f"Error in get_genres: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_movies(
    query: str = Query(...),  # Make it required
    page: int = Query(1, ge=1)
):
    """Search for movies by title"""
    try:
        logger.info(f"Search request received - Query: '{query}', Page: {page}")
        
        # Handle empty query case
        if not query.strip():
            logger.warning("Empty search query received")
            return {
                "page": 1,
                "results": [],
                "total_pages": 0,
                "total_results": 0
            }
            
        response = tmdb_service.search_movies(query.strip(), page)
        logger.info(f"Search response received with {len(response.get('results', []))} results")
        
        # Filter out movies without poster path
        filtered_results = [
            movie for movie in response.get("results", [])
            if movie.get("poster_path")
        ]
        
        return {
            "page": response.get("page", 1),
            "results": filtered_results,
            "total_pages": response.get("total_pages", 1),
            "total_results": response.get("total_results", 0)
        }
        
    except Exception as e:
        logger.error(f"Error searching movies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/genre/{genre_id}")
async def get_movies_by_genre(
    genre_id: int,
    page: int = 1
):
    try:
        logger.info(f"Fetching movies for genre {genre_id}, page {page}")
        
        # Get movies from TMDB API - remove await since _make_request is not async
        response = tmdb_service.discover_movies({
            "with_genres": genre_id,
            "page": page,
            "sort_by": "popularity.desc"
        })
        
        if not response or "results" not in response:
            raise HTTPException(status_code=404, detail="No movies found for this genre")
            
        return response
        
    except Exception as e:
        logger.error(f"Error getting movies for genre {genre_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint for debugging"""
    return {"status": "ok", "message": "API is working"}

@router.get("/{movie_id}")
async def get_movie_details(movie_id: int):
    try:
        logger.info(f"Fetching details for movie: {movie_id}")
        # Get movie details directly from TMDB
        response = tmdb_service.get_movie_details(movie_id)
        print(f"TMDB Movie Details Response: {response}")

        # Transform response to match frontend expectations
        movie_details = {
            "id": response.get("id"),
            "title": response.get("title"),
            "overview": response.get("overview"),
            "poster_path": response.get("poster_path"),
            "backdrop_path": response.get("backdrop_path"),
            "release_date": response.get("release_date"),
            "runtime": response.get("runtime"),
            "vote_average": response.get("vote_average"),
            "genres": response.get("genres", [])
        }
        return movie_details
    except Exception as e:
        logger.error(f"Error in get_movie_details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{movie_id}/similar")
async def get_similar_movies(
    movie_id: int,
    limit: int = Query(8, ge=1, le=20),
    current_user: User = Depends(get_current_user)  # Add auth requirement
):
    """Get similar movies based on a movie ID"""
    try:
        logger.info(f"Getting similar movies for movie_id: {movie_id}, limit: {limit}")
        
        # Call TMDB service to get similar movies
        response = tmdb_service.get_similar_movies(movie_id)
        
        if not response or "results" not in response:
            logger.warning(f"No similar movies found for movie_id: {movie_id}")
            return {"movies": []}
        
        # Filter results and limit
        movies = [
            movie for movie in response.get("results", [])
            if movie.get("poster_path") and movie.get("release_date")
        ][:limit]
        
        logger.info(f"Found {len(movies)} similar movies")
        return {"movies": movies}
        
    except Exception as e:
        logger.error(f"Error getting similar movies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))