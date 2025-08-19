function renderSubmissions(submissions) {
    const tbody = document.querySelector('#submissions-table tbody');
    tbody.innerHTML = '';

    if (submissions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">No submissions found.</td></tr>';
        return;
    }

    submissions.forEach(submission => {
        const row = `
            <tr>
                <td>${submission.id}</td>
                <td>${submission.name}</td>
                <td>${submission.project_name}</td>
                <td>${submission.extracted_by}</td>
                <td>${new Date(submission.submission_date).toLocaleDateString()}</td>
                <td><button class="btn-run-pipeline" data-submission-id="${submission.id}">Run Pipeline</button></td>
            </tr>
        `;
        tbody.insertAdjacentHTML('beforeend', row);
    });
}

async function fetchSubmissions() {
    try {
        const response = await fetch('/api/submissions');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const submissions = await response.json();
        renderSubmissions(submissions);
    } catch (error) {
        console.error('Failed to fetch submissions:', error);
        const tbody = document.querySelector('#submissions-table tbody');
        tbody.innerHTML = `<tr><td colspan="5">Error loading submissions.</td></tr>`;
    }
}

export function initializeSubmissionsPage() {
    fetchSubmissions();

    const tbody = document.querySelector('#submissions-table tbody');
    tbody.addEventListener('click', async (event) => {
        if (event.target.classList.contains('btn-run-pipeline')) {
            const submissionId = event.target.dataset.submissionId;
            const pipelineId = prompt('Enter the ID of the pipeline to run:');
            if (pipelineId) {
                try {
                    const response = await fetch(`/api/submissions/${submissionId}/run-pipeline`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ pipeline_id: pipelineId })
                    });
                    const result = await response.json();
                    if (response.ok) {
                        alert(`Job started successfully! Job ID: ${result.job_id}`);
                    } else {
                        alert(`Error: ${result.error}`);
                    }
                } catch (error) {
                    console.error('Failed to run pipeline:', error);
                    alert('An error occurred while trying to run the pipeline.');
                }
            }
        }
    });
}
