// Filename: frontend/app.js

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const loader = document.getElementById('loader');
const analysisBox = document.getElementById('analysis-box');

// Click dropzone to open standard file select explorer
dropzone.addEventListener('click', () => fileInput.click());

// Handle file loading when selected via file dialog window
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        processLogFile(e.target.files[0]);
    }
});

// Drag and drop event handlers
dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.style.borderColor = '#39ff14'; // Glow neon green when file is hovering over
});

dropzone.style.transition = "all 0.3s ease";
dropzone.addEventListener('dragleave', () => {
    dropzone.style.borderColor = '#00f0ff'; // Revert back to cyan when file leaves
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.style.borderColor = '#00f0ff';
    if (e.dataTransfer.files.length > 0) {
        processLogFile(e.dataTransfer.files[0]);
    }
});

// Primary communication function sending file data to Python backend
async function processLogFile(file) {
    // Show user a responsive processing state
    loader.style.display = 'block';
    analysisBox.style.display = 'none';
    
    // Package file into a multi-part form payload matches our FastAPI requirement
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Send actual HTTP POST request directly into local backend server
        const response = await fetch('http://127.0.0.1:8000/api/triage', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned error code status: ${response.status}`);
        }

        const data = await response.json();
        
        // Dynamically update view objects with AI telemetry parameters
        document.getElementById('log-name').innerText = data.filename;
        document.getElementById('val-severity').innerText = data.error_severity;
        document.getElementById('val-tier').innerText = data.analytics.routing_tier;
        
        // Populate core content structures
        document.getElementById('analysis-root-cause').innerText = data.analysis.root_cause;
        document.getElementById('analysis-fix').innerText = data.analysis.suggested_fix;
        document.getElementById('analysis-snippet').innerText = data.analysis.extracted_snippet;

        // Toggle retry alert indicator badge styling dynamically
        const retryBadge = document.getElementById('retry-badge');
        if (data.retry_recommended) {
            retryBadge.innerText = "✓ Safe to Auto-Retry Build";
            retryBadge.className = "badge badge-success";
        } else {
            retryBadge.innerText = "⚠ Do Not Auto-Retry: Logic Failure Blocked";
            retryBadge.className = "badge badge-danger";
        }

        // Display the fully generated insights dashboard viewport
        analysisBox.style.display = 'flex';

    } catch (error) {
        console.error("UI Transmission Pipeline Error:", error);
        alert(`Failed to analyze log file context. Ensure Python backend is running!\nDetails: ${error.message}`);
    } finally {
        // Remove processing state feedback indicators
        loader.style.display = 'none';
    }
}