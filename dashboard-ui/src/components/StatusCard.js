// This function creates the status card and handles its UI updates,
// including polling for real-time job progress.
export function createStatusCard(jobId, file, pipelines) {
    const cardId = `card-${jobId}`;
    const card = document.createElement('div');
    card.className = 'status-card';
    card.id = cardId;
    let pollingInterval = null; // To hold the interval ID

    // Initial HTML for the card
    card.innerHTML = `
        <div class="card-header">
            <strong>File:</strong> ${file.name}
            <span class="status-bubble preparing">Preparing</span>
        </div>
        <div class="card-body">
            <div class="pipeline-selector">
                <select class="pipeline-dropdown">
                    <option value="" disabled selected>Select a pipeline...</option>
                    ${pipelines.map(p => `<option value="${p}">${p}</option>`).join('')}
                </select>
                <button class="run-pipeline-btn">Run Pipeline</button>
            </div>
            <div class="progress-container" style="display: none;">
                <div class="process-title-container">
                    <span class="process-title">Initializing...</span>
                    <button class="toggle-progress-btn">Hide</button>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
                <div class="progress-percentage">0%</div>
            </div>
        </div>
    `;

    const container = document.getElementById('status-cards-container');
    container.prepend(card);

    // Get references to all UI elements
    const runButton = card.querySelector('.run-pipeline-btn');
    const pipelineDropdown = card.querySelector('.pipeline-dropdown');
    const statusBubble = card.querySelector('.status-bubble');
    const pipelineSelector = card.querySelector('.pipeline-selector');
    const progressContainer = card.querySelector('.progress-container');
    const processTitle = card.querySelector('.process-title');
    const progressBarFill = card.querySelector('.progress-fill');
    const progressPercentage = card.querySelector('.progress-percentage');
    const toggleBtn = card.querySelector('.toggle-progress-btn');

    // --- Helper Functions ---

    function updateStatusBubble(status) {
        statusBubble.className = 'status-bubble'; // Reset classes
        let statusText = 'Unknown';
        switch (status) {
            case 'preparing': statusBubble.classList.add('preparing'); statusText = 'Preparing'; break;
            case 'running': statusBubble.classList.add('in-progress'); statusText = 'In Progress'; break;
            case 'completed': statusBubble.classList.add('completed'); statusText = 'Completed'; break;
            case 'error': statusBubble.classList.add('error'); statusText = 'Error'; break;
        }
        statusBubble.textContent = statusText;
    }

    function startPolling() {
        pollingInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/job-status/${jobId}`);
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }

                const data = await response.json();

                // Update UI with new data
                processTitle.textContent = data.process_title;
                progressBarFill.style.width = `${data.progress}%`;
                progressPercentage.textContent = `${data.progress}%`;
                updateStatusBubble(data.status);

                // Stop polling if the job is finished
                if (data.status === 'completed' || data.status === 'error') {
                    clearInterval(pollingInterval);
                    if (data.status === 'completed') {
                        progressBarFill.style.backgroundColor = '#2ecc71'; // Green fill
                    } else {
                        progressBarFill.style.backgroundColor = '#e74c3c'; // Red fill
                    }
                }
            } catch (error) {
                console.error('Polling error:', error);
                clearInterval(pollingInterval);
                updateStatusBubble('error');
                processTitle.textContent = 'Connection error.';
            }
        }, 2000); // Poll every 2 seconds
    }

    // --- Event Listeners ---

    runButton.addEventListener('click', async () => {
        const selectedPipeline = pipelineDropdown.value;
        if (!selectedPipeline) {
            alert('Please select a pipeline first.');
            return;
        }

        runButton.disabled = true;
        pipelineDropdown.disabled = true;
        runButton.textContent = 'Starting...';

        try {
            const response = await fetch('/api/run-job', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jobId: jobId, pipelineName: selectedPipeline }),
            });

            if (!response.ok) throw new Error('Failed to start job');

            // Show progress UI and start polling for updates
            pipelineSelector.style.display = 'none';
            progressContainer.style.display = 'block';
            updateStatusBubble('running');
            startPolling();

        } catch (error) {
            console.error('Error starting job:', error);
            alert('Could not start the job. Please check the server.');
            updateStatusBubble('error');
            runButton.disabled = false;
            pipelineDropdown.disabled = false;
            runButton.textContent = 'Run Pipeline';
        }
    });

    toggleBtn.addEventListener('click', () => {
        const bar = card.querySelector('.progress-bar');
        const percentage = card.querySelector('.progress-percentage');
        const isHidden = bar.style.display === 'none';
        bar.style.display = isHidden ? 'block' : 'none';
        percentage.style.display = isHidden ? 'block' : 'none';
        toggleBtn.textContent = isHidden ? 'Hide' : 'Show';
    });

    // --- Styles (injected once) ---
    if (!document.getElementById('status-card-styles')) {
        const style = document.createElement('style');
        style.id = 'status-card-styles';
        style.textContent = `
            .status-card { background-color: white; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .card-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; background-color: #f7f7f7; border-bottom: 1px solid #e0e0e0; font-size: 0.9rem; }
            .card-body { padding: 15px; }
            .pipeline-selector { display: flex; gap: 10px; align-items: center; }
            .pipeline-dropdown { flex-grow: 1; padding: 8px; border-radius: 4px; border: 1px solid #ccc; }
            .run-pipeline-btn { padding: 8px 15px; border: none; background-color: #007bff; color: white; border-radius: 4px; cursor: pointer; transition: background-color 0.2s; }
            .run-pipeline-btn:hover:not(:disabled) { background-color: #0056b3; }
            .run-pipeline-btn:disabled { background-color: #a0a0a0; cursor: not-allowed; }
            .status-bubble { padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; color: white; }
            .status-bubble.preparing { background-color: #f39c12; }
            .status-bubble.in-progress { background-color: #3498db; }
            .status-bubble.completed { background-color: #2ecc71; }
            .status-bubble.error { background-color: #e74c3c; }
            .progress-container { margin-top: 15px; }
            .process-title-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
            .process-title { font-size: 0.9rem; color: #555; }
            .toggle-progress-btn { background: none; border: none; color: #007bff; cursor: pointer; font-size: 0.8rem; }
            .progress-bar { width: 100%; height: 20px; background-color: #e0e0e0; border-radius: 10px; overflow: hidden; }
            .progress-fill { width: 0%; height: 100%; background-color: #3498db; transition: width 0.3s ease-in-out; }
            .progress-percentage { text-align: center; font-size: 0.8rem; font-weight: bold; margin-top: 5px; }
        `;
        document.head.appendChild(style);
    }
}
