document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.getElementById('uploadButton');
    const statusDiv = document.getElementById('status');

    uploadButton.addEventListener('click', async () => {
        const file = fileInput.files[0];
        if (!file) {
            statusDiv.textContent = 'Error: Please select a file first.';
            return;
        }

        statusDiv.textContent = 'Uploading file...';

        // Create a FormData object to send the file
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                statusDiv.innerHTML = `<strong>Success:</strong> ${result.message}<br><strong>Simulated Command:</strong> ${result.docker_command_simulation}`;
            } else {
                statusDiv.textContent = `Error: ${result.error}`;
            }
        } catch (error) {
            statusDiv.textContent = 'A network error occurred. Is the server running?';
            console.error('Upload error:', error);
        }
    });
});
