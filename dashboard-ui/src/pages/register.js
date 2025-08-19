document.getElementById('register-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    if (data.password !== data.confirm_password) {
        alert("Passwords do not match.");
        return;
    }

    const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        window.location.href = '/';
    } else {
        const errorData = await response.json();
        alert(errorData.errors ? JSON.stringify(errorData.errors) : 'Registration failed');
    }
});
