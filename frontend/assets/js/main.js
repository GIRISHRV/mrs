/**
 * Main JavaScript for the Movie Recommendation System
 * Handles UI interactions and data display
 */

class MovieApp {
    constructor() {
        // DOM elements
        this.popularMoviesContainer = document.getElementById('popular-movies');
        this.genresContainer = document.getElementById('genres-container');
        this.searchForm = document.getElementById('search-form');
        this.searchInput = document.getElementById('search-input');
        
        this.init();
        
        // Setup search functionality
        this.setupSearch();
    }
    
    async init() {
        // Load initial data
        this.loadPopularMovies();
        this.loadGenres();
        this.bindEvents();
    }
    
    bindEvents() {
        // Search form submit
        if (this.searchForm) {
            this.searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const query = this.searchInput.value.trim();
                if (query) {
                    window.location.href = `pages/search-results.html?q=${encodeURIComponent(query)}`;
                }
            });
        }
    }
    
    setupSearch() {
        document.getElementById('search-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = document.getElementById('search-input').value.trim();
            if (query) {
                window.location.href = `pages/search-results.html?q=${encodeURIComponent(query)}`;
            }
        });
    }

    async loadPopularMovies() {
        if (!this.popularMoviesContainer) return;
        
        try {
            const response = await apiService.getPopularMovies();
            
            // Clear loading spinner
            this.popularMoviesContainer.innerHTML = '';
            
            // Extract movies array from response
            const movies = response.movies || [];
            console.log('Movies array:', movies);
            
            // Create movie grid
            const movieGrid = document.createElement('div');
            movieGrid.className = 'row g-4';
            
            // Add movies to grid
            movies.forEach(movie => {
                movieGrid.innerHTML += this.createMovieCard(movie);
            });

            // Add grid to container
            this.popularMoviesContainer.appendChild(movieGrid);

            // Add watch button handlers after rendering
            this.attachWatchButtonHandlers();

        } catch (error) {
            console.error('Error loading popular movies:', error);
            this.popularMoviesContainer.innerHTML = `
                <div class="col-12 text-center">
                    <div class="alert alert-danger">
                        Failed to load popular movies. Please try again later.
                    </div>
                </div>
            `;
        }
    }
    
    async loadGenres() {
        if (!this.genresContainer) return;
        
        try {
            const response = await apiService.getGenres();
            
            // Clear container
            this.genresContainer.innerHTML = '';
            
            // Extract genres array from response
            const genres = response.genres || [];
            console.log('Genres array:', genres); // Debug statement
            
            // Display genres
            genres.forEach(genre => {
                const genreCard = document.createElement('div');
                genreCard.className = 'col-md-3 col-sm-4 col-6';
                genreCard.innerHTML = `
                    <div class="genre-card" data-genre-id="${genre.id}">
                        <h5>${genre.name}</h5>
                    </div>
                `;
                
                genreCard.querySelector('.genre-card').addEventListener('click', () => {
                    window.location.href = `pages/genre.html?id=${genre.id}&name=${encodeURIComponent(genre.name)}`;
                });
                
                this.genresContainer.appendChild(genreCard);
            });
        } catch (error) {
            console.error('Error loading genres:', error);
            this.genresContainer.innerHTML = `
                <div class="col-12 text-center">
                    <div class="alert alert-danger">
                        Failed to load genres. Please try again later.
                    </div>
                </div>
            `;
        }
    }
    
    createMovieCard(movie) {
        return `
            <div class="col-md-3 col-sm-6 mb-4">
                <div class="card movie-card h-100">
                    <img src="${apiService.getImageUrl(movie.poster_path)}" 
                         class="card-img-top" 
                         alt="${movie.title}"
                         onerror="this.onerror=null; this.src='assets/images/placeholder.jpg'">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title text-truncate" title="${movie.title}">${movie.title}</h5>
                        <p class="card-text">
                            <small class="text-muted">
                                ${movie.release_date ? new Date(movie.release_date).getFullYear() : 'N/A'}
                            </small>
                            <span class="float-end">
                                <i class="fas fa-star text-warning"></i> 
                                ${movie.vote_average?.toFixed(1) || 'N/A'}
                            </span>
                        </p>
                        <div class="mt-auto d-grid gap-2">
                            <a href="pages/movie.html?id=${movie.tmdb_id || movie.id}" 
                               class="btn btn-primary">View Details</a>
                            ${this.isAuthenticated ? `
                                <button class="btn btn-outline-light watch-btn" 
                                        data-movie-id="${movie.id}">
                                    <i class="fas fa-check"></i> Mark as Watched
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    attachWatchButtonHandlers() {
        if (!this.isAuthenticated) return;
        
        document.querySelectorAll('.watch-btn').forEach(button => {
            button.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                const movieId = button.dataset.movieId;
                try {
                    await apiService.addToWatchHistory(movieId);
                    button.disabled = true;
                    button.innerHTML = '<i class="fas fa-check"></i> Watched';
                    this.showToast('Added to watch history!', 'success');
                } catch (error) {
                    this.showToast('Error adding to watch history', 'danger');
                }
            });
        });
    }
    
    showLoadingSpinner() {
        const spinner = document.createElement('div');
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = `
            <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        document.body.appendChild(spinner);
        return spinner;
    }
    
    hideLoadingSpinner(spinner) {
        if (spinner && spinner.parentNode) {
            spinner.parentNode.removeChild(spinner);
        }
    }
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    window.movieApp = new MovieApp();
});

// Add to assets/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // Remove or comment out any modal initialization code here
    // const modals = document.querySelectorAll('.modal');
    // modals.forEach(modal => new bootstrap.Modal(modal));
    
    // Navbar background change on scroll
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Image loading animation
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.classList.add('loading');
        img.onload = () => {
            img.classList.remove('loading');
            img.classList.add('loaded');
        };
    });

    // Handle hero image loading
    const heroImage = document.querySelector('.hero-image');
    if (heroImage) {
        heroImage.onload = () => {
            heroImage.classList.remove('loading');
            heroImage.classList.add('loaded');
        };

        // If image is already loaded when script runs
        if (heroImage.complete) {
            heroImage.classList.remove('loading');
            heroImage.classList.add('loaded');
        }
    }
});