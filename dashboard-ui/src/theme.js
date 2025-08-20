const html = document.querySelector('html');

function setTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    }
}

// The theme dropdown has been removed, so the event listener is no longer needed.
// The default theme is now set in index.html, and this script handles loading
// a user's persisted theme choice from localStorage.

document.addEventListener('DOMContentLoaded', loadTheme);
