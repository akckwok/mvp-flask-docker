import { createDropZone } from '../components/DropZone.js';
import { createStatusCard } from '../components/StatusCard.js';

// Store the list of pipelines fetched from the server
let availablePipelines = [];

// Fetch the list of pipelines from the backend when the app loads
async function fetchPipelines() {
    try {
        const response = await fetch('/api/pipelines');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        availablePipelines = await response.json();
        console.log('Available pipelines:', availablePipelines);
    } catch (error) {
        console.error('Failed to fetch pipelines:', error);
        // Optionally, display an error to the user
        alert('Could not load the list of available pipelines. Please check the server.');
    }
}

// This function is called when a file is selected in the DropZone
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
            // After successful upload, create a status card.
            // Pass the job ID, file info, and the list of pipelines.
            createStatusCard(result.jobId, file, availablePipelines);
        } else {
            console.error('Upload failed:', result.error);
            alert(`Upload Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Network error during upload:', error);
        alert('A network error occurred during upload. Is the server running?');
    }
}

export function initializeJobSubmissionPage() {
    const dropZoneContainer = document.getElementById('drop-zone-container');
    if (dropZoneContainer) {
        createDropZone(dropZoneContainer, handleFileSelect);
    }

    // Fetch the pipelines when the job submission page is initialized
    fetchPipelines();
}
