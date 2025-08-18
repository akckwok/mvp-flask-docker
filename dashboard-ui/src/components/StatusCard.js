// This function contains the logic for faking the pipeline progress.
// It will be called after the user clicks "Run Pipeline".
function runPipelineAndSimulate(card, jobId, pipelineName, dockerCommand) {
    const logsContainer = card.querySelector('.logs pre code');
    const stageText = card.querySelector('.stage-text');
    const statusLight = card.querySelector('.status-light');

    function addLog(message) {
        logsContainer.textContent += `[${new Date().toLocaleTimeString()}] ${message}\n`;
        logsContainer.parentElement.scrollTop = logsContainer.parentElement.scrollHeight;
    }

    // --- Simulation ---
    stageText.textContent = 'Processing...';
    statusLight.style.backgroundColor = '#f39c12'; // Orange for processing

    addLog(`Starting pipeline: ${pipelineName}...`);
    addLog(`Mock command: ${dockerCommand}`);

    setTimeout(() => {
        addLog('...');
        addLog('Step 1/3: Analyzing file metadata.');
    }, 1500);

    setTimeout(() => {
        addLog('Step 2/3: Running pipeline...');
        addLog('...');
    }, 3000);

    setTimeout(() => {
        stageText.textContent = 'Complete';
        statusLight.style.backgroundColor = '#2ecc71'; // Green for complete
        addLog('Step 3/3: Process complete.');
        addLog('--- Finished ---');
    }, 4500);
}

// This function creates the initial status card with a pipeline selector.
export function createStatusCard(jobId, file, pipelines) {
    const cardId = `card-${jobId}`;
    const card = document.createElement('div');
    card.className = 'status-card';
    card.id = cardId;

    // Create the HTML for the dropdown options
    const pipelineOptions = pipelines.map(p => `<option value="${p}">${p}</option>`).join('');

    card.innerHTML = `
        <div class="card-header">
            <strong>File:</strong> ${file.name}
            <span class="status-light" style="background-color: #bdc3c7;"></span> <!-- Grey for awaiting -->
        </div>
        <div class="card-body">
            <div class="status-stage"><strong>Status:</strong> <span class="stage-text">Awaiting Selection</span></div>
            <div class="pipeline-selector">
                <select class="pipeline-dropdown">
                    <option value="" disabled selected>Select a pipeline...</option>
                    ${pipelineOptions}
                </select>
                <button class="run-pipeline-btn">Run Pipeline</button>
            </div>
            <div class="logs" style="display: none;">
                <pre><code></code></pre>
            </div>
        </div>
    `;

    const container = document.getElementById('status-cards-container');
    container.prepend(card);

    const runButton = card.querySelector('.run-pipeline-btn');
    const pipelineDropdown = card.querySelector('.pipeline-dropdown');
    const logsWrapper = card.querySelector('.logs');

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
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jobId: jobId,
                    pipelineName: selectedPipeline,
                }),
            });

            const result = await response.json();

            if (response.ok) {
                // Hide selector and show logs
                card.querySelector('.pipeline-selector').style.display = 'none';
                logsWrapper.style.display = 'block';
                // Start the visual simulation with the command from the server
                runPipelineAndSimulate(card, jobId, selectedPipeline, result.docker_command_simulation);
            } else {
                alert(`Error starting job: ${result.error}`);
                runButton.disabled = false;
                pipelineDropdown.disabled = false;
                runButton.textContent = 'Run Pipeline';
            }
        } catch (error) {
            console.error('Network error when starting job:', error);
            alert('A network error occurred. Could not start the job.');
            runButton.disabled = false;
            pipelineDropdown.disabled = false;
            runButton.textContent = 'Run Pipeline';
        }
    });

    if (!document.getElementById('status-card-styles')) {
        const style = document.createElement('style');
        style.id = 'status-card-styles';
        style.textContent = `
            .status-card {
                background-color: white; border: 1px solid #e0e0e0; border-radius: 8px;
                margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            .card-header {
                display: flex; justify-content: space-between; align-items: center;
                padding: 12px 15px; background-color: #f7f7f7; border-bottom: 1px solid #e0e0e0;
                font-size: 0.9rem;
            }
            .status-light { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
            .card-body { padding: 15px; }
            .status-stage { margin-bottom: 15px; }
            .pipeline-selector { display: flex; gap: 10px; align-items: center; }
            .pipeline-dropdown { flex-grow: 1; padding: 8px; border-radius: 4px; border: 1px solid #ccc; }
            .run-pipeline-btn {
                padding: 8px 15px; border: none; background-color: #007bff; color: white;
                border-radius: 4px; cursor: pointer; transition: background-color 0.2s;
            }
            .run-pipeline-btn:hover:not(:disabled) { background-color: #0056b3; }
            .run-pipeline-btn:disabled { background-color: #a0a0a0; cursor: not-allowed; }
            .logs {
                background-color: #2c3e50; color: #ecf0f1; font-family: 'Courier New', Courier, monospace;
                padding: 15px; border-radius: 4px; max-height: 200px; overflow-y: auto; font-size: 0.85rem;
            }
            .logs pre { margin: 0; white-space: pre-wrap; word-wrap: break-word; }
        `;
        document.head.appendChild(style);
    }
}
