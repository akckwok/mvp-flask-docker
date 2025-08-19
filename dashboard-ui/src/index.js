import './styles.css';
import './App.js';
import { initializeJobSubmissionPage } from './pages/JobSubmission.js';
import { initializeAllJobsPage } from './pages/AllJobs.js';

document.addEventListener('DOMContentLoaded', () => {
    initializeJobSubmissionPage();
    initializeAllJobsPage();
});
