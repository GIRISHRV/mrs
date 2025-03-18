import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.movie import Movie

class RecommendationService:
    """Service for generating movie recommendations using different algorithms"""
    
    def __init__(self):
        # Cache for movie vectors (content-based filtering)
        self.movie_vectors = None
        self.movie_indices = None
        self.last_update = None
    
    def _prepare_content_features(self, movies):
        """Prepare movie content features for content-based filtering"""
        # Create a DataFrame with movie features
        movie_data = []
        for movie in movies:
            # Combine relevant text features
            content = f"{movie.title} {movie.overview} {' '.join([g.name for g in movie.genres])}"
            
            movie_data.append({
                'id': movie.id,
                'tmdb_id': movie.tmdb_id,
                'content': content
            })
        
        df = pd.DataFrame(movie_data)
        
        # Create TF-IDF vectors from movie content
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['content'])
        
        # Calculate cosine similarity matrix
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Create a mapping of movie IDs to matrix indices
        indices = pd.Series(df.index, index=df['tmdb_id']).drop_duplicates()
        
        return cosine_sim, indices
    
    def _content_based_recommendations(self, movie_tmdb_id, cosine_sim, indices, all_movies, limit=10):
        """Get content-based recommendations for a movie"""
        # Get the index of the movie
        idx = indices[movie_tmdb_id]
        
        # Get similarity scores for all movies
        sim_scores = list(enumerate(cosine_sim[idx]))
        
        # Sort movies based on similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top similar movies (excluding the movie itself)
        sim_scores = sim_scores[1:limit+1]
        
        # Get movie indices
        movie_indices = [i[0] for i in sim_scores]
        
        # Return the top movies
        return [all_movies[i] for i in movie_indices]
    
    def _collaborative_filtering(self, user, all_movies, db, limit=10):
        """Simple collaborative filtering based on user ratings"""
        # Get all users and their ratings
        users_ratings = db.query(User, Movie).join(
            "watch_history"
        ).filter(
            Movie.id.in_([m.id for m in all_movies])
        ).all()
        
        # Create a user-item matrix (simplified)
        # In a real system, you would use a more sophisticated approach
        # such as matrix factorization (SVD) from libraries like Surprise
        
        # For now, return movies liked by users with similar preferences
        user_genres = set([g.id for g in user.preferences])
        
        # Find users with similar genre preferences
        similar_users = []
        for u, _ in users_ratings:
            if u.id != user.id:
                u_genres = set([g.id for g in u.preferences])
                # Calculate Jaccard similarity between genre sets
                similarity = len(user_genres.intersection(u_genres)) / len(user_genres.union(u_genres)) if user_genres or u_genres else 0
                similar_users.append((u, similarity))
        
        # Sort users by similarity
        similar_users.sort(key=lambda x: x[1], reverse=True)
        similar_users = similar_users[:5]  # Consider top 5 similar users
        
        # Get movies liked by similar users but not watched by the current user
        watched_movies = set([m.id for m in user.watch_history])
        recommended_movies = []
        
        for similar_user, _ in similar_users:
            for movie in similar_user.watch_history:
                # Check if user rated this movie highly
                # This requires additional logic to get the rating from the user_movie table
                if movie.id not in watched_movies:
                    recommended_movies.append(movie)
                    if len(recommended_movies) >= limit:
                        break
        
        return recommended_movies[:limit]
    
    def get_recommendations_for_user(self, user: User, limit: int = 10, db: Session = None) -> List[Movie]:
        """Get personalized recommendations based on user's watch history"""
        if not user.watch_history:
            return self.get_popular_movies(limit)
        
        # Get user's recently watched movies
        recent_movies = (
            db.query(Movie)
            .join(watch_history)
            .filter(watch_history.c.user_id == user.id)
            .order_by(watch_history.c.watched_at.desc())
            .limit(5)
            .all()
        )
        
        # Get similar movies based on watch history
        recommendations = []
        for movie in recent_movies:
            similar_movies = self._content_based_recommendations(
                movie.tmdb_id,
                limit=3  # Get top 3 similar movies for each watched movie
            )
            recommendations.extend(similar_movies)
        
        # Remove duplicates and already watched movies
        watched_ids = {m.id for m in user.watch_history}
        unique_recommendations = []
        seen = set()
        
        for movie in recommendations:
            if movie.id not in watched_ids and movie.id not in seen:
                unique_recommendations.append(movie)
                seen.add(movie.id)
        
        return unique_recommendations[:limit]