export function createStatusCard(file, dockerCommand) {
    const cardId = `card-${Date.now()}`;
    const card = document.createElement('div');
    card.className = 'status-card';
    card.id = cardId;

    card.innerHTML = `
        <div class="card-header">
            <strong>File:</strong> ${file.name}
            <span class="status-light" style="background-color: #f39c12;"></span>
        </div>
        <div class="card-body">
            <div class="status-stage"><strong>Status:</strong> <span class="stage-text">Uploading...</span></div>
            <div class="logs">
                <pre><code></code></pre>
            </div>
        </div>
    `;

    const container = document.getElementById('status-cards-container');
    container.prepend(card);

    const logsContainer = card.querySelector('pre code');
    const stageText = card.querySelector('.stage-text');
    const statusLight = card.querySelector('.status-light');

    function addLog(message) {
        logsContainer.textContent += `[${new Date().toLocaleTimeString()}] ${message}\n`;
        logsContainer.parentElement.scrollTop = logsContainer.parentElement.scrollHeight;
    }

    // --- Simulation ---
    addLog('Starting upload...');
    setTimeout(() => {
        stageText.textContent = 'Processing...';
        addLog(`Upload complete. File size: ${(file.size / 1024).toFixed(2)} KB.`);
        addLog('Backend processing started.');
        addLog(`Mock command: ${dockerCommand}`);
    }, 1500); // Simulate upload time

    setTimeout(() => {
        stageText.textContent = 'Generating logs...';
        addLog('...');
        addLog('Step 1/3: Analyzing file metadata.');
    }, 3000);

    setTimeout(() => {
        addLog('Step 2/3: Running pipeline...');
        addLog('...');
    }, 4500);

    setTimeout(() => {
        stageText.textContent = 'Complete';
        statusLight.style.backgroundColor = '#2ecc71'; // Green light
        addLog('Step 3/3: Process complete.');
        addLog('--- Finished ---');
    }, 6000);


    // Add styling for the card
    const style = document.createElement('style');
    style.textContent = `
        .status-card {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 15px;
            background-color: #f7f7f7;
            border-bottom: 1px solid #e0e0e0;
            font-size: 0.9rem;
        }
        .status-light {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }
        .card-body {
            padding: 15px;
        }
        .status-stage {
            margin-bottom: 15px;
        }
        .logs {
            background-color: #2c3e50;
            color: #ecf0f1;
            font-family: 'Courier New', Courier, monospace;
            padding: 15px;
            border-radius: 4px;
            max-height: 200px;
            overflow-y: auto;
            font-size: 0.85rem;
        }
        .logs pre {
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    `;
    card.appendChild(style);
}
