let myChart = null;
let activeFilename = "";

window.addEventListener('DOMContentLoaded', () => {
    renderAnalyticsChart(0, 0);
    const dropzone = document.getElementById('dropzone');
    dropzone.addEventListener('dragover', (e) => { e.preventDefault(); });
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        if (e.dataTransfer.files.length > 0) { handleFileDrop(e.dataTransfer.files[0]); }
    });
});

function injectMockLog(type) {
    let mockText = ""; let filename = "";
    if (type === 'timeout') {
        mockText = "INFO: Initializing container layer runs...\nERROR: [DOCKER_BUILD] Connection to artifact repository endpoint failed download sequence.\nFATAL ERROR: ET_TIMEOUT connection gateway dropped downstream repository mirrors network connection loops.";
        filename = "network_timeout.log";
    } else {
        mockText = "INFO: Spawning isolated validation runner units...\nFAIL: test_auth_token_validation\nAssertionError: assert 401 == 200\nExecution frame context dropped at line 42 in components/auth/core/test_suites.py runtime block.";
        filename = "unit_assertion.log";
    }
    const blob = new Blob([mockText], { type: 'text/plain' });
    const file = new File([blob], filename, { type: "text/plain" });
    handleFileDrop(file);
}

async function handleFileDrop(file) {
    if (!file) return;
    activeFilename = file.name;
    const formData = new FormData();
    formData.append("file", file);
    try {
        const response = await fetch('http://127.0.0.1:8000/api/triage', { method: 'POST', body: formData });
        if (!response.ok) { throw new Error(`Server status: ${response.status}`); }
        const data = await response.json();
        populateDashboard(data);
        updateLedgerUI(data.ledger_history);
    } catch (error) {
        console.error("Failure:", error);
        alert("Could not reach backend triage microservice pipeline. Ensure server is running on port 8000.");
    }
}

function populateDashboard(data) {
    document.getElementById('outputInspector').style.display = "block";
    document.getElementById('out-file').innerText = data.filename;
    document.getElementById('out-cause').innerText = data.analysis.root_cause;
    document.getElementById('out-fix').innerText = data.analysis.suggested_fix;
    document.getElementById('out-snippet').innerText = data.analysis.extracted_snippet;
    document.getElementById('kpi-tier').innerText = data.analytics.routing_tier;
    document.getElementById('kpi-conf').innerText = `${data.confidence_score}%`;
    document.getElementById('kpi-memory').innerText = `${data.hindsight_memory.historical_occurrence_count}x`;
    document.getElementById('kpi-saved').innerText = `-${data.analytics.tokens_saved_percent}%`;
    
    const banner = document.getElementById('retry-gate-banner');
    if (data.retry_recommended) {
        banner.innerText = "🟢 SAFE TO AUTO-RETRY: Transient environmental anomaly caught by CascadeFlow.";
        banner.style.backgroundColor = "rgba(57, 255, 20, 0.08)"; banner.style.border = "1px solid #39ff14"; banner.style.color = "#39ff14";
    } else {
        banner.innerText = "🔴 AUTOMATED RE-RUN BLOCKED: Hard functional regression signature discovered.";
        banner.style.backgroundColor = "rgba(255, 49, 49, 0.08)"; banner.style.border = "1px solid #ff3131"; banner.style.color = "#ff3131";
    }
    renderAnalyticsChart(data.analytics.tokens_saved_percent, data.hindsight_memory.historical_occurrence_count);
}

// FEATURE LAYER: DYNAMIC RE-DRAW LOOP FOR THE SIDEBAR LEDGER CONTAINERS
function updateLedgerUI(historyList) {
    const listContainer = document.getElementById('ledger-list');
    if (!historyList || historyList.length === 0) return;
    
    listContainer.innerHTML = ""; // Clear loader elements
    historyList.forEach(item => {
        let colorMarker = item.severity === 'CRITICAL' ? '#ff3131' : '#9d4edd';
        listContainer.innerHTML += `
            <div class="ledger-item">
                <span style="color: var(--text-muted)">[${item.time}]</span>
                <span style="color: #fff; font-weight: 500; max-width: 110px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${item.file}</span>
                <span style="color: ${colorMarker}; font-weight: bold; font-size: 11px;">${item.severity}</span>
            </div>
        `;
    });
}

function renderAnalyticsChart(savedPercent, recurrences) {
    const ctx = document.getElementById('metricsChart').getContext('2d');
    if (myChart) { myChart.destroy(); }
    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Token Size Reduction Ratio (%)', 'Hindsight Tracked Incidents (Count)'],
            datasets: [{
                data: [savedPercent, recurrences],
                backgroundColor: ['rgba(57, 255, 20, 0.4)', 'rgba(157, 78, 221, 0.4)'],
                borderColor: ['#39ff14', '#9d4edd'],
                borderWidth: 2, barThickness: 45
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b' } },
                x: { grid: { display: false }, ticks: { color: '#f8fafc' } }
            }
        }
    });
}

function generateGitHubIssueMarkdown() {
    const cause = document.getElementById('out-cause').innerText;
    const fix = document.getElementById('out-fix').innerText;
    const file = document.getElementById('out-file').innerText;
    if (!file) { alert("Please triage a crash log before exporting templates!"); return; }
    const markdownTemplate = `### 🚨 CI/CD Pipeline Triage Failure Report\n**Logged Target:** \`${file}\`\n\n#### Root Cause:\n> ${cause}\n\n#### Recommended Patch:\n- [ ] ${fix}`;
    navigator.clipboard.writeText(markdownTemplate); alert("📋 GitHub Markdown Template Copied!");
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input'); const history = document.getElementById('chat-history'); const queryText = input.value.trim();
    if (!queryText) return;
    history.innerHTML += `<div style="margin-top: 4px; color: #fff;"><strong>You:</strong> ${queryText}</div>`;
    history.scrollTop = history.scrollHeight; input.value = "";
    try {
        const response = await fetch('http://127.0.0.1:8000/api/chat', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: queryText, filename: activeFilename })
        });
        const data = await response.json();
        history.innerHTML += `<div style="margin-top: 4px; color: var(--neon-cyan);"><strong>Agent:</strong> ${data.reply}</div>`;
        history.scrollTop = history.scrollHeight;
    } catch (error) {
        console.error("Chat fetch failure:", error);
        history.innerHTML += `<div style="margin-top: 4px; color: var(--neon-red);"><strong>System Error:</strong> Network connection dropped.</div>`;
    }
}
