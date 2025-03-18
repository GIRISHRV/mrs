class YourSpace {
    constructor() {
        this.watchHistoryContainer = document.getElementById('watch-history-container');
        this.recommendationsContainer = document.getElementById('recommendations-container');
        this.init();
    }

    async init() {
        try {
            await this.loadWatchHistory();
            await this.loadRecommendations();
        } catch (error) {
            console.error('Error initializing Your Space:', error);
        }
    }

    async loadWatchHistory() {
        try {
            const history = await apiService.getWatchHistory();
            
            if (!history.length) {
                this.watchHistoryContainer.innerHTML = `
                    <div class="col-12 text-center">
                        <p>You haven't watched any movies yet.</p>
                        <a href="../index.html" class="btn btn-primary">Browse Movies</a>
                    </div>
                `;
                return;
            }

            this.watchHistoryContainer.innerHTML = history
                .map(movie => this.createMovieCard(movie))
                .join('');

        } catch (error) {
            console.error('Error loading watch history:', error);
        }
    }

    async loadRecommendations() {
        try {
            const recommendations = await apiService.getPersonalizedRecommendations();
            
            if (!recommendations.length) {
                this.recommendationsContainer.innerHTML = `
                    <div class="col-12 text-center">
                        <p>Start watching movies to get personalized recommendations!</p>
                    </div>
                `;
                return;
            }

            this.recommendationsContainer.innerHTML = recommendations
                .map(movie => this.createMovieCard(movie))
                .join('');

        } catch (error) {
            console.error('Error loading recommendations:', error);
        }
    }

    createMovieCard(movie) {
        return `
            <div class="col-md-2 col-sm-4 col-6">
                <div class="card bg-dark text-white movie-card">
                    <img src="https://image.tmdb.org/t/p/w500${movie.poster_path}" 
                         class="card-img-top" 
                         alt="${movie.title}">
                    <div class="card-body">
                        <h6 class="card-title text-truncate">${movie.title}</h6>
                        <small class="text-muted">
                            ${new Date(movie.watched_at || movie.release_date).getFullYear()}
                        </small>
                    </div>
                </div>
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new YourSpace();
});