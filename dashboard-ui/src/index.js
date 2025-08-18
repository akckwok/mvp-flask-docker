import { initializeRouter } from './App.js';
import { initializeJobSubmissionPage } from './pages/JobSubmission.js';
import { checkAuth } from './auth.js';

document.addEventListener('DOMContentLoaded', async () => {
    const isAuthenticated = await checkAuth();
    if (!isAuthenticated) {
        window.location.href = '/';
        return;
    }

    initializeRouter();
    initializeJobSubmissionPage();

    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', async (e) => {
            e.preventDefault();
            const response = await fetch('/api/logout', { method: 'POST' });
            if (response.ok) {
                window.location.href = '/';
            } else {
                alert('Logout failed.');
            }
        });
    }
});
