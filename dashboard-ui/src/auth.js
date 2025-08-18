export async function checkAuth() {
    try {
        const response = await fetch('/api/check-auth');
        if (response.ok) {
            const data = await response.json();
            return data.is_authenticated;
        }
        return false;
    } catch (error) {
        console.error('Error checking authentication status:', error);
        return false;
    }
}
