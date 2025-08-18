import { initializeRouter } from './App.js';
import { initializeJobSubmissionPage } from './pages/JobSubmission.js';

document.addEventListener('DOMContentLoaded', () => {
    initializeRouter();
    initializeJobSubmissionPage();
});
