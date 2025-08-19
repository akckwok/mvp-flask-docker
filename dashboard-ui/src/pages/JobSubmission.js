import { createDropZone } from '../components/DropZone.js';
import { createStatusCard } from '../components/StatusCard.js';

let availablePipelines = [];
let selectedPipeline = null;

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

async function handleFilesSelect(files) {
    if (!selectedPipeline) {
        alert('Please select a pipeline before uploading files.');
        return;
    }

    console.log(`Uploading ${files.length} file(s) for pipeline ${selectedPipeline.name}...`);

    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            createStatusCard(result.jobId, result.filenames, selectedPipeline);
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

    createDropZone(dropZoneContainer, handleFilesSelect);
    // Initially disable dropzone
    dropZoneContainer.querySelector('.drop-zone').classList.add('disabled');


    pipelineSelector.addEventListener('change', (e) => {
        const pipelineId = e.target.value;
        selectedPipeline = availablePipelines.find(p => p.id === pipelineId);
        updatePipelineInfo();

        if (selectedPipeline) {
            dropZoneContainer.querySelector('.drop-zone').classList.remove('disabled');
        } else {
            dropZoneContainer.querySelector('.drop-zone').classList.add('disabled');
        }
    });

    fetchPipelines();
}
