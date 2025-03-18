class AuthGuard {
    static async checkAuth() {
        const token = localStorage.getItem('token');
        const isLandingPage = window.location.pathname.includes('landing.html');
        
        if (!token && !isLandingPage) {
            await this.fadeAndRedirect();
        } else if (token && isLandingPage) {
            await this.fadeAndRedirect('index.html');
        }
    }

    static async fadeAndRedirect(path = 'landing.html') {
        document.body.style.opacity = '0';
        document.body.style.transition = 'opacity 0.3s ease';
        await new Promise(resolve => setTimeout(resolve, 300));
        window.location.href = path;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Set initial opacity
    document.body.style.opacity = '1';
    AuthGuard.checkAuth();
});