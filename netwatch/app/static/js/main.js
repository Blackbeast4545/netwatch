// Initialize socket with explicit configuration
const socket = io({
    transports: ['websocket'],
    upgrade: false,
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    secure: true,
    rejectUnauthorized: false
});

let packetChart, trafficChart;
let map;
let markers = {};

function formatBytes(bytes) {
    if (bytes === 0) return '0 B/s';
    const k = 1024;
    const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Debug logging function
function debugLog(message) {
    const debugOutput = document.getElementById('debug-output');
    const timestamp = new Date().toLocaleTimeString();
    debugOutput.innerHTML += `[${timestamp}] ${message}\n`;
    console.log(`[${timestamp}] ${message}`);
}

// Socket event handlers
socket.on('connect', () => {
    console.log('WebSocket Connected');
    const statusElement = document.getElementById('connection-status');
    statusElement.textContent = 'Connected';
    statusElement.className = 'stat-value connected';
});

socket.on('disconnect', () => {
    console.log('WebSocket Disconnected');
    const statusElement = document.getElementById('connection-status');
    statusElement.textContent = 'Disconnected';
    statusElement.className = 'stat-value disconnected';
});

socket.on('connect_error', (error) => {
    console.error('Connection Error:', error);
    const statusElement = document.getElementById('connection-status');
    statusElement.textContent = 'Connection Error';
    statusElement.className = 'stat-value disconnected';
});

socket.on('reconnect_attempt', () => {
    console.log('Attempting to reconnect...');
    const statusElement = document.getElementById('connection-status');
    statusElement.textContent = 'Reconnecting...';
    statusElement.className = 'stat-value';
});

socket.on('error', (error) => {
    debugLog(`WebSocket error: ${error}`);
});

// Initialize charts when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded');
    initializeCharts();
});

function initializeCharts() {
    console.log('Initializing charts...');
    
    // Initialize Packet Distribution Chart
    const packetCtx = document.getElementById('packetChart').getContext('2d');
    packetChart = new Chart(packetCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'TCP',
                    data: [],
                    borderColor: '#FF6384',
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'UDP',
                    data: [],
                    borderColor: '#36A2EB',
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'ICMP',
                    data: [],
                    borderColor: '#FFCE56',
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Other',
                    data: [],
                    borderColor: '#4BC0C0',
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            animation: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Packet Distribution'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Initialize Network Traffic Chart
    const trafficCtx = document.getElementById('trafficChart').getContext('2d');
    trafficChart = new Chart(trafficCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Upload',
                    data: [],
                    borderColor: '#2ecc71',
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Download',
                    data: [],
                    borderColor: '#e74c3c',
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            animation: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Network Traffic'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatBytes(value);
                        }
                    }
                }
            }
        }
    });
}

function initMap() {
    // Initialize the map
    map = L.map('mapContainer').setView([0, 0], 2);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

function updateMapMarkers(connections) {
    try {
        // Clear existing markers
        Object.values(markers).forEach(marker => map.removeLayer(marker));
        markers = {};

        connections.forEach(conn => {
            if (conn.location) {
                const location = conn.location;
                const markerKey = `${location.latitude},${location.longitude}`;

                if (!markers[markerKey]) {
                    // Create marker with popup
                    const marker = L.marker([location.latitude, location.longitude])
                        .bindPopup(`
                            <strong>${location.city}, ${location.country}</strong><br>
                            Remote IP: ${conn.remote_addr}<br>
                            Process: ${conn.process}<br>
                            Status: ${conn.status}
                        `);
                    
                    marker.addTo(map);
                    markers[markerKey] = marker;
                } else {
                    // Update existing marker popup
                    const existingPopup = markers[markerKey].getPopup();
                    const existingContent = existingPopup.getContent();
                    markers[markerKey].setPopupContent(existingContent + `<br>Remote IP: ${conn.remote_addr}`);
                }
            }
        });
    } catch (error) {
        console.error('Error updating map markers:', error);
    }
}

// Make sure map is initialized when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing map...');
    initMap();
});

// Update the network_update socket handler
socket.on('network_update', (data) => {
    console.log('Received network update:', data);
    
    try {
        // Update current traffic rates
        const bytesSent = document.getElementById('bytes-sent');
        const bytesRecv = document.getElementById('bytes-recv');
        
        if (bytesSent && bytesRecv) {
            bytesSent.textContent = formatBytes(data.current_traffic.bytes_sent_rate);
            bytesRecv.textContent = formatBytes(data.current_traffic.bytes_recv_rate);
        }

        // Update packet distribution chart
        if (packetChart && data.packet_history && data.packet_history.length > 0) {
            const labels = data.packet_history.map(item => item.timestamp);
            packetChart.data.labels = labels;
            packetChart.data.datasets[0].data = data.packet_history.map(item => item.TCP);
            packetChart.data.datasets[1].data = data.packet_history.map(item => item.UDP);
            packetChart.data.datasets[2].data = data.packet_history.map(item => item.ICMP);
            packetChart.data.datasets[3].data = data.packet_history.map(item => item.Other);
            packetChart.update('none');
        }

        // Update traffic chart
        if (trafficChart && data.traffic_history && data.traffic_history.length > 0) {
            const labels = data.traffic_history.map(item => item.timestamp);
            trafficChart.data.labels = labels;
            trafficChart.data.datasets[0].data = data.traffic_history.map(item => item.bytes_sent);
            trafficChart.data.datasets[1].data = data.traffic_history.map(item => item.bytes_recv);
            trafficChart.update('none');
        }

        // Update connections table
        const tbody = document.querySelector('#connectionsTable tbody');
        if (tbody && data.connections) {
            tbody.innerHTML = '';
            data.connections.forEach(conn => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${conn.local_addr}</td>
                    <td>${conn.remote_addr}</td>
                    <td>${conn.status}</td>
                    <td>${conn.process}</td>
                    <td>${conn.timestamp}</td>
                `;
                row.classList.add('new-connection');
            });
        }

        // Update map markers
        if (data.connections) {
            updateMapMarkers(data.connections);
        }

        // Update system stats
        if (data.system_stats) {
            // Update CPU
            const cpuUsage = document.getElementById('cpu-usage');
            const cpuProgress = document.getElementById('cpu-progress');
            if (cpuUsage && cpuProgress) {
                cpuUsage.textContent = `${data.system_stats.cpu_percent}%`;
                cpuProgress.style.width = `${data.system_stats.cpu_percent}%`;
            }

            // Update Memory
            const memoryUsage = document.getElementById('memory-usage');
            const memoryProgress = document.getElementById('memory-progress');
            const memoryDetails = document.getElementById('memory-details');
            if (memoryUsage && memoryProgress && memoryDetails) {
                memoryUsage.textContent = `${data.system_stats.memory_percent}%`;
                memoryProgress.style.width = `${data.system_stats.memory_percent}%`;
                memoryDetails.textContent = `${data.system_stats.memory_used} / ${data.system_stats.memory_total}`;
            }

            // Update storage information
            if (data.system_stats && data.system_stats.disk_info) {
                const storageCards = document.getElementById('storage-cards');
                const storageDetails = document.getElementById('storage-details');
                
                if (storageCards && storageDetails) {
                    // Clear existing content
                    storageCards.innerHTML = '';
                    storageDetails.innerHTML = '';

                    // Create storage details table
                    let tableHTML = `
                        <table class="storage-details-table">
                            <thead>
                                <tr>
                                    <th>Device</th>
                                    <th>Mount Point</th>
                                    <th>Total</th>
                                    <th>Used</th>
                                    <th>Free</th>
                                    <th>Usage</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;

                    data.system_stats.disk_info.forEach(disk => {
                        // Add card for each disk
                        const cardHTML = `
                            <div class="storage-card">
                                <h4>${disk.mountpoint}</h4>
                                <div class="storage-progress-bar">
                                    <div class="storage-progress ${disk.percent > 90 ? 'critical' : disk.percent > 70 ? 'warning' : ''}" 
                                         style="width: ${disk.percent}%"></div>
                                </div>
                                <div class="storage-stats">
                                    <span>Used: ${disk.used}</span>
                                    <span>${disk.percent}%</span>
                                    <span>Total: ${disk.total}</span>
                                </div>
                            </div>
                        `;
                        storageCards.innerHTML += cardHTML;

                        // Add row to details table
                        tableHTML += `
                            <tr>
                                <td>${disk.device}</td>
                                <td>${disk.mountpoint}</td>
                                <td>${disk.total}</td>
                                <td>${disk.used}</td>
                                <td>${disk.free}</td>
                                <td>
                                    <div class="storage-progress-bar">
                                        <div class="storage-progress ${disk.percent > 90 ? 'critical' : disk.percent > 70 ? 'warning' : ''}" 
                                             style="width: ${disk.percent}%"></div>
                                    </div>
                                </td>
                            </tr>
                        `;
                    });

                    tableHTML += '</tbody></table>';
                    storageDetails.innerHTML = tableHTML;
                }
            }
        }

    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
});

// Handle alerts
socket.on('new_alert', (alert) => {
    const alertsList = document.getElementById('alertsList');
    const alertElement = document.createElement('div');
    alertElement.className = 'alert';
    alertElement.innerHTML = `
        <strong>${alert.title}</strong>
        <p>${alert.message}</p>
        <small>${alert.timestamp}</small>
    `;
    alertsList.prepend(alertElement);
});

// Handle filtering
document.getElementById('filterForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const filterData = Object.fromEntries(formData.entries());
    
    const response = await fetch('/filter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(filterData)
    });
    
    const result = await response.json();
    updateDashboard(result);
});

// Handle data export
async function exportData(type) {
    const response = await fetch('/export', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ type })
    });
    
    if (type === 'csv') {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `network_stats_${new Date().toISOString()}.csv`;
        a.click();
    }
}

// Add CSS to ensure the map container is visible
document.head.insertAdjacentHTML('beforeend', `
    <style>
        .map-widget {
            margin: 20px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        #mapContainer {
            min-height: 400px;
            width: 100%;
            border-radius: 8px;
            z-index: 1;
        }
    </style>
`); 