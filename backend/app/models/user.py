from sqlalchemy import Boolean, Column, Integer, String, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.database import Base
from datetime import datetime
import bcrypt
from app.models.movie import watch_history

# Many-to-many relationship table for user preferences (genres)
user_genre = Table(
    'user_genre',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)

# Many-to-many relationship table for user watch history
user_movie = Table(
    'user_movie',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('movie_id', Integer, ForeignKey('movies.id')),
    Column('rating', Integer, nullable=True),
    Column('watched_at', DateTime, default=datetime.utcnow)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    preferences = relationship("Genre", secondary="user_genre", back_populates="users")
    watch_history = relationship(
        "Movie",
        secondary="watch_history",
        back_populates="watched_by",
        lazy="dynamic"
    )
    watchlist_entries = relationship("Watchlist", back_populates="user")
    ratings_entries = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def verify_password(self, password):
        return bcrypt.checkpw(password.encode(), self.hashed_password.encode())