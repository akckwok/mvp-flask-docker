function displayLogs(card, jobId, pipelineName) {
    const logsContainer = card.querySelector('.logs pre code');
    const stageText = card.querySelector('.stage-text');
    const statusLight = card.querySelector('.status-light');

    function addLog(message) {
        logsContainer.textContent += `[${new Date().toLocaleTimeString()}] ${message}\n`;
        logsContainer.parentElement.scrollTop = logsContainer.parentElement.scrollHeight;
    }

    stageText.textContent = 'Running...';
    statusLight.classList.remove('bg-blue-500');
    statusLight.classList.add('bg-yellow-500');

    addLog(`Pipeline '${pipelineName}' for job '${jobId}' has started.`);
    addLog('The backend is now processing the request.');
    addLog('For actual logs, check the server console.');
    addLog('(Real-time log streaming is not implemented in this version)');
}

export function createStatusCard(jobId, filenames, pipeline, submissionId) {
    const cardId = `card-${jobId}`;
    const card = document.createElement('div');
    card.className = 'card bg-base-100 shadow-xl';
    card.id = cardId;

    const fileDisplay = filenames.length === 1 ? filenames[0] : `${filenames.length} files`;

    card.innerHTML = `
        <div class="card-body">
            <div class="flex justify-between items-start">
                <h2 class="card-title text-sm">Job: ${jobId.split('-')[0]}... (${fileDisplay})</h2>
                <span class="status-light badge badge-info badge-xs"></span>
            </div>
            <p class="text-sm"><strong>Pipeline:</strong> ${pipeline.name}</p>
            <div class="text-sm"><strong>Status:</strong> <span class="stage-text">Ready to run</span></div>
            <div class="card-actions justify-end">
                <button class="run-pipeline-btn btn btn-sm btn-primary">Run Pipeline</button>
            </div>
            <div class="logs hidden mt-4">
                <div class="mockup-code">
                    <pre><code></code></pre>
                </div>
            </div>
        </div>
    `;

    const container = document.getElementById('status-cards-container');
    container.prepend(card);

    const runButton = card.querySelector('.run-pipeline-btn');
    const logsWrapper = card.querySelector('.logs');
    const statusLight = card.querySelector('.status-light');
    statusLight.classList.add('bg-blue-500'); // Initial state

    runButton.addEventListener('click', async () => {
        runButton.classList.add('loading', 'btn-disabled');
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
                runButton.classList.add('hidden');
                logsWrapper.classList.remove('hidden');
                displayLogs(card, jobId, pipeline.name);
            } else {
                alert(`Error starting job: ${result.error}`);
                runButton.classList.remove('loading', 'btn-disabled');
                runButton.textContent = 'Run Pipeline';
            }
        } catch (error) {
            console.error('Network error when starting job:', error);
            alert('A network error occurred. Could not start the job.');
            runButton.classList.remove('loading', 'btn-disabled');
            runButton.textContent = 'Run Pipeline';
        }
    });
}
