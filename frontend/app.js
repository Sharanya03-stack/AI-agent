// UI Viewport Tab Switching Logic Engine
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
        
        link.classList.add('active');
        document.getElementById(link.dataset.tab).classList.add('active');
    });
});

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const loader = document.getElementById('loader');
const analysisBox = document.getElementById('analysis-box');
let compressionChart = null;

// Dynamic Historical Memory Registry Matrix
let historicalIncidents = [];

dropzone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => { if(e.target.files.length > 0) processLogData(e.target.files[0]); });

dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.style.borderColor = '#00f0ff'; });
dropzone.addEventListener('dragleave', () => { dropzone.style.borderColor = 'rgba(255,255,255,0.1)'; });
dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.style.borderColor = 'rgba(255,255,255,0.1)';
    if(e.dataTransfer.files.length > 0) processLogData(e.dataTransfer.files[0]);
});

async function processLogData(file) {
    loader.style.display = 'block';
    analysisBox.style.display = 'none';
    document.getElementById('kpi-status').innerText = "Processing...";
    document.getElementById('kpi-status').style.color = "var(--neon-cyan)";

    const payload = new FormData();
    payload.append('file', file);

    try {
        const response = await fetch('http://127.0.0.1:8000/api/triage', { method: 'POST', body: payload });
        if(!response.ok) throw new Error(`HTTP System Breach Error Code: ${response.status}`);
        
        const data = await response.json();
        
        // CRITICAL FIX: Make the analytics panel container visible BEFORE loading text data or rendering Chart layouts
        analysisBox.style.display = 'grid';

        // Aligned perfectly with our upgraded index.html IDs
        document.getElementById('lbl-filename').innerText = data.filename;
        document.getElementById('kpi-severity').innerText = data.error_severity;
        document.getElementById('kpi-tier').innerText = data.analytics.routing_tier;
        document.getElementById('lbl-root-cause').innerText = data.analysis.root_cause;
        document.getElementById('lbl-fix').innerText = data.analysis.suggested_fix;
        document.getElementById('lbl-snippet').innerText = data.analysis.extracted_snippet;

        // Toggle badge components depending on recommendation parameters
        const badge = document.getElementById('badge-retry');
        if(data.retry_recommended) {
            badge.innerText = "✓ Safe to Auto-Retry";
            badge.className = "tag-pill tag-green";
        } else {
            badge.innerText = "⚠ Retry Blocked";
            badge.className = "tag-pill tag-red";
        }

        // Keep local tracking database updated for historical overview
        updateMemoryLedgerUI(data);

        // Build Data Visualization Chart using Chart.js layers
        renderChartMetrics(data.analytics.tokens_saved_percent);

        document.getElementById('kpi-status').innerText = "Diagnostics Complete";
        document.getElementById('kpi-status').style.color = "var(--neon-green)";

    } catch (error) {
        console.error("UI Processing Trace Interrupted:", error);
        alert(`Failed to handle build execution stream logs. Trace data: ${error.message}`);
        document.getElementById('kpi-status').innerText = "System Failure Code";
        document.getElementById('kpi-status').style.color = "var(--neon-red)";
    } finally {
        loader.style.display = 'none';
    }
}

function renderChartMetrics(savedPercent) {
    const ctx = document.getElementById('chart-compression').getContext('2d');
    const displayPercent = Math.max(0, Math.min(100, savedPercent));
    
    if(compressionChart) compressionChart.destroy();

    compressionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [displayPercent, 100 - displayPercent],
                backgroundColor: ['#00f0ff', '#121824'],
                borderWidth: 0,
                hoverOffset: 0
            }]
        },
        options: {
            cutout: '82%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { tooltip: { enabled: false } }
        }
    });

    document.getElementById('lbl-chart-desc').innerHTML = `Pruned and optimized <b style="color: #00f0ff">${displayPercent}%</b> of raw system metadata logs before routing context data frames to downstream models.`;
}

function updateMemoryLedgerUI(data) {
    const targetSignature = data.hindsight_memory.historical_occurrence_count > 1 ? "Network Gateway Timeout" : data.analysis.root_cause.split(" (")[0];
    
    // Check if incident already added into memory tracking arrays
    const recordIndex = historicalIncidents.findIndex(item => item.sig === targetSignature);
    const timestampStr = new Date().toISOString().replace('T', ' ').substring(0, 19);

    if(recordIndex !== -1) {
        historicalIncidents[recordIndex].count = data.hindsight_memory.historical_occurrence_count;
        historicalIncidents[recordIndex].time = timestampStr;
    } else {
        historicalIncidents.unshift({
            sig: targetSignature,
            count: data.hindsight_memory.historical_occurrence_count,
            time: timestampStr,
            handler: data.hindsight_memory.assigned_resolution_owner
        });
    }

    const tbody = document.getElementById('memory-table-body');
    if (tbody) {
        tbody.innerHTML = historicalIncidents.map(incident => `
            <tr>
                <td style="font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:#38bdf8; text-align:left;">${incident.sig}</td>
                <td style="font-weight:700; text-align:center; color:#fff;">${incident.count}x</td>
                <td style="font-size:0.85rem; color:#94a3b8; text-align:left;">${incident.time}</td>
                <td style="text-align:left;"><span class="tag-pill tag-green" style="font-size:0.7rem; text-transform:none;">${incident.handler}</span></td>
            </tr>
        `).join('');
    }
}

function copyText(elementId) {
    const text = document.getElementById(elementId).innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert("Copied to system clipboard matrix!");
    });
}


