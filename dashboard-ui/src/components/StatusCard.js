function displayLogs(card, jobId, pipelineName) {
    const logsContainer = card.querySelector('.logs pre code');
    const stageText = card.querySelector('.stage-text');
    const statusLight = card.querySelector('.status-light');

    function addLog(message) {
        logsContainer.textContent += `[${new Date().toLocaleTimeString()}] ${message}\n`;
        logsContainer.parentElement.scrollTop = logsContainer.parentElement.scrollHeight;
    }

    stageText.textContent = 'Running...';
    statusLight.style.backgroundColor = '#f39c12';

    addLog(`Pipeline '${pipelineName}' for job '${jobId}' has started.`);
    addLog('The backend is now processing the request.');
    addLog('For actual logs, check the server console.');
    addLog('(Real-time log streaming is not implemented in this version)');
}

export function createStatusCard(jobId, filenames, pipeline, submissionId) {
    const cardId = `card-${jobId}`;
    const card = document.createElement('div');
    card.className = 'status-card';
    card.id = cardId;

    const fileDisplay = filenames.length === 1 ? filenames[0] : `${filenames.length} files`;

    card.innerHTML = `
        <div class="card-header">
            <strong>Job:</strong> ${jobId.split('-')[0]}... (${fileDisplay})
            <span class="status-light" style="background-color: #3498db;"></span>
        </div>
        <div class="card-body">
            <div class="status-stage"><strong>Status:</strong> <span class="stage-text">Ready to run</span></div>
            <p><strong>Pipeline:</strong> ${pipeline.name}</p>
            <button class="run-pipeline-btn">Run Pipeline</button>
            <div class="logs" style="display: none;">
                <pre><code></code></pre>
            </div>
        </div>
    `;

    const container = document.getElementById('status-cards-container');
    container.prepend(card);

    const runButton = card.querySelector('.run-pipeline-btn');
    const logsWrapper = card.querySelector('.logs');

    runButton.addEventListener('click', async () => {
        runButton.disabled = true;
        runButton.textContent = 'Starting...';

        try {
            const response = await fetch('/api/run-job', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jobId: jobId,
                    pipelineId: pipeline.id,
                    submissionId: submissionId
                }),
            });

            const result = await response.json();

            if (response.ok) {
                runButton.style.display = 'none';
                logsWrapper.style.display = 'block';
                displayLogs(card, jobId, pipeline.name);
            } else {
                alert(`Error starting job: ${result.error}`);
                runButton.disabled = false;
                runButton.textContent = 'Run Pipeline';
            }
        } catch (error) {
            console.error('Network error when starting job:', error);
            alert('A network error occurred. Could not start the job.');
            runButton.disabled = false;
            runButton.textContent = 'Run Pipeline';
        }
    });

    if (!document.getElementById('status-card-styles')) {
        const style = document.createElement('style');
        style.id = 'status-card-styles';
        style.textContent = `
            .status-card { background-color: white; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .card-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; background-color: #f7f7f7; border-bottom: 1px solid #e0e0e0; font-size: 0.9rem; }
            .status-light { width: 12px; height: 12px; border-radius: 50%; }
            .card-body { padding: 15px; }
            .status-stage { margin-bottom: 15px; }
            .run-pipeline-btn { padding: 8px 15px; border: none; background-color: #27ae60; color: white; border-radius: 4px; cursor: pointer; transition: background-color 0.2s; }
            .run-pipeline-btn:hover:not(:disabled) { background-color: #229954; }
            .run-pipeline-btn:disabled { background-color: #a0a0a0; cursor: not-allowed; }
            .logs { background-color: #2c3e50; color: #ecf0f1; font-family: 'Courier New', Courier, monospace; padding: 15px; border-radius: 4px; max-height: 200px; overflow-y: auto; font-size: 0.85rem; }
            .logs pre { margin: 0; white-space: pre-wrap; word-wrap: break-word; }
        `;
        document.head.appendChild(style);
    }
}
