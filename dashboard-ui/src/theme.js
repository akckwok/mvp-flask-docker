const themeDropdown = document.getElementById('theme-dropdown');
const html = document.querySelector('html');

function setTheme(theme) {
    console.log('Setting theme to:', theme);
    console.log('html element:', html);
    html.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    console.log('Loading theme from localStorage:', savedTheme);
    if (savedTheme) {
        setTheme(savedTheme);
        const currentThemeInput = document.querySelector(`input[name="theme-dropdown"][value="${savedTheme}"]`);
        if (currentThemeInput) {
            currentThemeInput.checked = true;
        }
    }
}

if (themeDropdown) {
    themeDropdown.addEventListener('change', (e) => {
        if (e.target.name === 'theme-dropdown') {
            console.log('Theme changed to:', e.target.value);
            setTheme(e.target.value);
        }
    });
}

document.addEventListener('DOMContentLoaded', loadTheme);
