const pages = document.querySelectorAll('.page');
const navLinks = document.querySelectorAll('.nav-link');

function showPage(pageId) {
    // Hide all pages
    pages.forEach(page => {
        page.classList.remove('active');
    });

    // Show the target page
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
    }

    // Update nav link styles
    navLinks.forEach(link => {
        link.classList.remove('active');
        // The link's href is '#pageId', so we match against that
        if (link.getAttribute('href') === `#${pageId}`) {
            link.classList.add('active');
        }
    });
}

import { initializeAllJobsPage } from './pages/AllJobs.js';

function handleRouteChange() {
    // Get the page id from the hash, or default to 'job-submission'
    const pageId = window.location.hash.substring(1) || 'job-submission';
    showPage(pageId);

    if (pageId === 'all-jobs') {
        initializeAllJobsPage();
    }
}

async function checkAuth() {
    try {
        const response = await fetch('/api/user');
        if (!response.ok) {
            window.location.href = '/login.html';
            return null;
        }
        const user = await response.json();
        return user;
    } catch (error) {
        console.error('Authentication check failed', error);
        window.location.href = '/login.html';
        return null;
    }
}

function setupLogout() {
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', async () => {
            await fetch('/api/logout');
            window.location.href = '/login.html';
        });
    }
}

async function initializeApp() {
    const user = await checkAuth();
    if (user) {
        const usernameDisplay = document.getElementById('username-display');
        if (usernameDisplay) {
            usernameDisplay.textContent = user.username;
        }

        // Listen for hash changes
        window.addEventListener('hashchange', handleRouteChange);

        // Handle the initial page load
        handleRouteChange();

        setupLogout();
    }
}

initializeApp();
