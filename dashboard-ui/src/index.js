import { initializeRouter } from './App.js';
import { initializeJobSubmissionPage } from './pages/JobSubmission.js';
import { initializeAllJobsPage } from './pages/AllJobs.js';

document.addEventListener('DOMContentLoaded', () => {
    initializeRouter();
    initializeJobSubmissionPage();
    initializeAllJobsPage();
});
