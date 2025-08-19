async function fetchProfile() {
    try {
        const response = await fetch('/api/profile');
        if (!response.ok) {
            throw new Error('Failed to fetch profile');
        }
        const profile = await response.json();
        document.getElementById('username').textContent = profile.username;
        document.getElementById('full_name').textContent = profile.full_name;
        document.getElementById('email').textContent = profile.email;
        document.getElementById('phone_number').textContent = profile.phone_number;
    } catch (error) {
        console.error('Error fetching profile:', error);
        alert('Could not load your profile. Please try again later.');
    }
}

fetchProfile();
