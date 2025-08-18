import { createDropZone } from '../components/DropZone.js';
import { createStatusCard } from '../components/StatusCard.js';

async function handleFileSelect(file) {
    console.log(`Uploading file: ${file.name}`);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            // Pass the real command from the server to the status card
            createStatusCard(file, result.docker_command_simulation);
        } else {
            console.error('Upload failed:', result.error);
            // Display a user-friendly error
            alert(`Upload Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Network error during upload:', error);
        alert('A network error occurred. Is the server running?');
    }
}

export function initializeJobSubmissionPage() {
    const dropZoneContainer = document.getElementById('drop-zone-container');
    if (dropZoneContainer) {
        createDropZone(dropZoneContainer, handleFileSelect);
    }
}
