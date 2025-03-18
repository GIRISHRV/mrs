from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# First define Genre schemas since MovieResponse depends on it
class GenreBase(BaseModel):
    name: str

class GenreCreate(GenreBase):
    id: int

class GenreResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

# Then define Movie schemas
class MovieBase(BaseModel):
    title: str
    overview: Optional[str] = None

class MovieCreate(MovieBase):
    tmdb_id: int
    poster_path: Optional[str] = None
    release_date: Optional[datetime] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None

class MovieResponse(BaseModel):
    id: int
    tmdb_id: int
    title: str
    overview: str
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None
    genres: List[GenreResponse] = []
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, movie):
        # Handle None values for optional fields
        if hasattr(movie, 'release_date') and isinstance(movie.release_date, datetime):
            movie.release_date = movie.release_date.strftime('%Y-%m-%d')
        if not hasattr(movie, 'backdrop_path'):
            movie.backdrop_path = None
        if not hasattr(movie, 'genres'):
            movie.genres = []
        return super().from_orm(movie)

# Movie history schemas (needed for UserResponse)
class MovieHistoryCreate(BaseModel):
    movie_id: int

class MovieHistoryBase(BaseModel):
    id: int
    movie_id: int
    title: str
    poster_path: Optional[str] = None
    watched_at: datetime

    class Config:
        from_attributes = True

class MovieHistoryResponse(BaseModel):
    id: int
    title: str
    poster_path: Optional[str] = None
    watched_at: datetime

    class Config:
        from_attributes = True

# Watchlist schemas (needed for UserResponse)
class WatchlistCreate(BaseModel):
    movie_id: int

class WatchlistBase(BaseModel):
    id: int
    movie_id: int
    title: str
    poster_path: Optional[str] = None
    added_at: datetime

class WatchlistResponse(WatchlistBase):
    user_id: int
    
    class Config:
        from_attributes = True

# Rating schemas (needed for UserResponse)
class RatingCreate(BaseModel):
    movie_id: int
    rating: int

class RatingBase(BaseModel):
    id: int
    movie_id: int
    title: str
    poster_path: Optional[str] = None
    rating: int
    created_at: datetime
    updated_at: datetime

class RatingResponse(RatingBase):
    user_id: int
    
    class Config:
        from_attributes = True

# Now we can define User schemas since all dependent schemas are defined
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="User's password")

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    avatar_url: Optional[str] = None

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

# Genre preference schema
class GenrePreferenceCreate(BaseModel):
    genre_ids: List[int]

class GenrePreferenceResponse(BaseModel):
    genres: List[GenreResponse]
    
    class Config:
        from_attributes = True

# Add this print statement to debug
print("Schemas loaded successfully")