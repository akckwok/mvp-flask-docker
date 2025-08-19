import { createDropZone } from '../components/DropZone.js';
import { createStatusCard } from '../components/StatusCard.js';

let availablePipelines = [];
let availableSubmissions = [];
let selectedPipeline = null;
let selectedSubmission = null;

function updatePipelineInfo() {
    const pipelineInfo = document.getElementById('pipeline-info');
    if (!selectedPipeline) {
        pipelineInfo.style.display = 'none';
        return;
    }

    document.getElementById('pipeline-desc').textContent = selectedPipeline.description;

    const inputsList = document.getElementById('pipeline-inputs');
    inputsList.innerHTML = '';
    selectedPipeline.inputs.forEach(input => {
        const li = document.createElement('li');
        li.textContent = `${input.name}: ${input.description} (type: ${input.type})`;
        inputsList.appendChild(li);
    });

    const outputsList = document.getElementById('pipeline-outputs');
    outputsList.innerHTML = '';
    if (selectedPipeline.outputs) {
        selectedPipeline.outputs.forEach(output => {
            const li = document.createElement('li');
            li.textContent = `${output.name}: ${output.description} (type: ${output.type})`;
            outputsList.appendChild(li);
        });
    }

    pipelineInfo.style.display = 'block';
}

async function fetchPipelines() {
    try {
        const response = await fetch('/api/pipelines');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        availablePipelines = await response.json();

        const selector = document.getElementById('pipeline-selector');
        selector.innerHTML = '<option value="">Select a pipeline...</option>';
        availablePipelines.forEach(p => {
            const option = document.createElement('option');
            option.value = p.id;
            option.textContent = p.name;
            selector.appendChild(option);
        });
        selector.disabled = false;

    } catch (error) {
        console.error('Failed to fetch pipelines:', error);
        alert('Could not load pipelines. Please check the server.');
    }
}

async function fetchSubmissions() {
    try {
        const response = await fetch('/api/submissions');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        availableSubmissions = await response.json();

        const selector = document.getElementById('submission-selector');
        selector.innerHTML = '<option value="">Select a data submission...</option>';
        availableSubmissions.forEach(s => {
            const option = document.createElement('option');
            option.value = s.id;
            option.textContent = s.name;
            selector.appendChild(option);
        });
        selector.disabled = false;

    } catch (error) {
        console.error('Failed to fetch submissions:', error);
        alert('Could not load submissions. Please check the server.');
    }
}

async function handleFilesSelect(files) {
    if (!selectedPipeline || !selectedSubmission) {
        alert('Please select a pipeline and a data submission before uploading files.');
        return;
    }

    console.log(`Uploading ${files.length} file(s) for submission ${selectedSubmission.name} and pipeline ${selectedPipeline.name}...`);

    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });

    try {
        const response = await fetch(`/api/submissions/${selectedSubmission.id}/create-job`, {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            createStatusCard(result.jobId, result.filenames, selectedPipeline, selectedSubmission.id);
        } else {
            console.error('Upload failed:', result.error);
            alert(`Upload Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Network error during upload:', error);
        alert('A network error occurred during upload.');
    }
}

export function initializeJobSubmissionPage() {
    const dropZoneContainer = document.getElementById('drop-zone-container');
    const pipelineSelector = document.getElementById('pipeline-selector');
    const submissionSelector = document.getElementById('submission-selector');

    createDropZone(dropZoneContainer, handleFilesSelect);
    // Initially disable dropzone
    dropZoneContainer.querySelector('.drop-zone').classList.add('disabled');

    pipelineSelector.addEventListener('change', (e) => {
        const pipelineId = e.target.value;
        selectedPipeline = availablePipelines.find(p => p.id === pipelineId);
        updatePipelineInfo();
        checkEnableDropZone();
    });

    submissionSelector.addEventListener('change', (e) => {
        const submissionId = e.target.value;
        selectedSubmission = availableSubmissions.find(s => s.id == submissionId);
        checkEnableDropZone();
    });

    function checkEnableDropZone() {
        if (selectedPipeline && selectedSubmission) {
            dropZoneContainer.querySelector('.drop-zone').classList.remove('disabled');
        } else {
            dropZoneContainer.querySelector('.drop-zone').classList.add('disabled');
        }
    }

    fetchPipelines();
    fetchSubmissions();
}
