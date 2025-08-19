async function fetchJobs() {
    try {
        const response = await fetch('/api/jobs');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const jobs = await response.json();
        return jobs;
    } catch (error) {
        console.error('Failed to fetch jobs:', error);
        return [];
    }
}

function createJobCard(job) {
    const card = document.createElement('div');
    card.className = 'job-card';

    const jobId = job.jobId || 'N/A';
    const status = job.status || 'N/A';
    const pipeline = job.pipeline || 'N/A';
    const files = job.files ? job.files.map(f => f.original_filename).join(', ') : 'N/A';

    card.innerHTML = `
        <h3>Job ID: ${jobId}</h3>
        <p><strong>Status:</strong> ${status}</p>
        <p><strong>Pipeline:</strong> ${pipeline}</p>
        <p><strong>Files:</strong> ${files}</p>
    `;
    return card;
}

export async function initializeAllJobsPage() {
    const jobsListContainer = document.getElementById('all-jobs-container');
    if (!jobsListContainer) return;

    jobsListContainer.innerHTML = '<p>Loading jobs...</p>';
    const jobs = await fetchJobs();

    if (jobs.length === 0) {
        jobsListContainer.innerHTML = '<p>No jobs found.</p>';
        return;
    }

    jobsListContainer.innerHTML = '';
    jobs.forEach(job => {
        const card = createJobCard(job);
        jobsListContainer.appendChild(card);
    });
}
