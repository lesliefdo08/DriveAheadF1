// DriveAhead F1 Live Telemetry Dashboard with Real Race Data Integration

class F1TelemetryDashboard {
    constructor() {
        this.charts = {};
        this.isLiveSession = false;
        this.sessionType = null;
        this.sessionName = null;
        this.dataSource = 'simulation';
        this.telemetryData = {
            hamilton: {
                speed: 291,
                rpm: 10450,
                gear: 6,
                throttle: 85,
                brake: 0,
                lap: 8,
                currentTime: '1:24.052',
                bestTime: '1:23.781'
            },
            verstappen: {
                speed: 287,
                rpm: 10200,
                gear: 6,
                throttle: 92,
                brake: 0,
                lap: 8,
                currentTime: '1:23.052',
                bestTime: '1:22.565'
            }
        };
        this.init();
    }

    init() {
        this.createCharts();
        this.checkSessionStatus();
        this.startRealTimeUpdates();
        this.updateCarPositions();
    }

    async checkSessionStatus() {
        try {
            const response = await fetch('/api/session-status');
            const status = await response.json();
            
            this.isLiveSession = status.is_live;
            this.sessionType = status.session_type;
            this.sessionName = status.session_name;
            
            this.updateSessionStatusDisplay(status);
            
        } catch (error) {
            console.error('Error checking session status:', error);
        }
    }

    updateSessionStatusDisplay(status) {
        // Add live session indicator to the page
        const existingIndicator = document.querySelector('.live-session-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }

        const indicator = document.createElement('div');
        indicator.className = 'live-session-indicator';
        
        if (status.is_live) {
            indicator.innerHTML = `
                <div class="live-badge live-active">
                    <span class="live-dot"></span>
                    🔴 LIVE ${status.session_name}
                </div>
                <div class="live-info">
                    Azerbaijan GP • Real telemetry data
                </div>
            `;
        } else {
            indicator.innerHTML = `
                <div class="live-badge live-simulation">
                    📊 SIMULATION MODE
                </div>
                <div class="live-info">
                    Live data available during Azerbaijan GP (Sep 13-15)
                </div>
            `;
        }
        
        document.querySelector('.telemetry-header').appendChild(indicator);
    }

    createCharts() {
        // Speed Chart
        this.charts.speed = new Chart(document.getElementById('speedChart'), {
            type: 'line',
            data: {
                labels: Array.from({length: 20}, (_, i) => i),
                datasets: [{
                    label: 'Hamilton',
                    data: this.generateSpeedData(),
                    borderColor: '#00d2be',
                    backgroundColor: 'rgba(0, 210, 190, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 0
                }, {
                    label: 'Verstappen',
                    data: this.generateSpeedData(5),
                    borderColor: '#0600ef',
                    backgroundColor: 'rgba(6, 0, 239, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                scales: {
                    x: { display: false },
                    y: { 
                        display: false,
                        min: 200,
                        max: 350
                    }
                },
                plugins: {
                    legend: { display: false }
                },
                elements: {
                    point: { radius: 0 }
                }
            }
        });

        // Throttle Chart
        this.charts.throttle = new Chart(document.getElementById('throttleChart'), {
            type: 'line',
            data: {
                labels: Array.from({length: 20}, (_, i) => i),
                datasets: [{
                    label: 'Hamilton',
                    data: this.generateThrottleData(),
                    borderColor: '#00d2be',
                    backgroundColor: 'rgba(0, 210, 190, 0.2)',
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: 0,
                    fill: true
                }, {
                    label: 'Verstappen',
                    data: this.generateThrottleData(10),
                    borderColor: '#0600ef',
                    backgroundColor: 'rgba(6, 0, 239, 0.2)',
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: 0,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                scales: {
                    x: { display: false },
                    y: { 
                        display: false,
                        min: 0,
                        max: 100
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });

        // Brake Chart
        this.charts.brake = new Chart(document.getElementById('brakeChart'), {
            type: 'line',
            data: {
                labels: Array.from({length: 20}, (_, i) => i),
                datasets: [{
                    label: 'Hamilton',
                    data: this.generateBrakeData(),
                    borderColor: '#dc143c',
                    backgroundColor: 'rgba(220, 20, 60, 0.3)',
                    borderWidth: 2,
                    tension: 0.2,
                    pointRadius: 0,
                    fill: true
                }, {
                    label: 'Verstappen',
                    data: this.generateBrakeData(5),
                    borderColor: '#ff6b00',
                    backgroundColor: 'rgba(255, 107, 0, 0.3)',
                    borderWidth: 2,
                    tension: 0.2,
                    pointRadius: 0,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                scales: {
                    x: { display: false },
                    y: { 
                        display: false,
                        min: 0,
                        max: 100
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    generateSpeedData(offset = 0) {
        return Array.from({length: 20}, (_, i) => {
            const base = 280 + offset;
            const variation = Math.sin((i + offset) * 0.5) * 30;
            const noise = (Math.random() - 0.5) * 10;
            return Math.max(200, Math.min(350, base + variation + noise));
        });
    }

    generateThrottleData(offset = 0) {
        return Array.from({length: 20}, (_, i) => {
            const base = 70;
            const variation = Math.sin((i + offset) * 0.3) * 25;
            const noise = (Math.random() - 0.5) * 15;
            return Math.max(0, Math.min(100, base + variation + noise));
        });
    }

    generateBrakeData(offset = 0) {
        return Array.from({length: 20}, (_, i) => {
            const brakeZones = [3, 7, 12, 16]; // Brake zones
            let brake = 0;
            
            brakeZones.forEach(zone => {
                if (Math.abs((i + offset) % 20 - zone) < 1) {
                    brake = 60 + Math.random() * 30;
                }
            });
            
            return brake;
        });
    }

    startRealTimeUpdates() {
        setInterval(() => {
            this.updateTelemetryData();
            this.updateDisplayValues();
            this.updateCharts();
        }, 100); // Update every 100ms for smooth animations
    }

    async updateTelemetryData() {
        try {
            // Get telemetry data from backend (live or algorithmic)
            const response = await fetch('/api/telemetry');
            const data = await response.json();
            
            if (data && !data.error) {
                // Check if we have metadata about data source
                if (data._meta) {
                    this.dataSource = data._meta.data_source;
                    this.updateDataSourceIndicator(data._meta);
                    
                    // Check for live session status changes
                    if (data._meta.session_type !== this.sessionType) {
                        this.sessionType = data._meta.session_type;
                        this.sessionName = data._meta.session_name;
                        this.isLiveSession = data._meta.data_source === 'live';
                        this.updateSessionStatusDisplay({
                            is_live: this.isLiveSession,
                            session_type: this.sessionType,
                            session_name: this.sessionName
                        });
                    }
                }
                
                // Update Hamilton data
                if (data['Lewis Hamilton']) {
                    const ham = data['Lewis Hamilton'];
                    this.updateDriverData('ham', ham.speed, ham.rpm, ham.gear, ham.throttle, ham.brake);
                    
                    // Update additional live data if available
                    if (ham.lap_time) {
                        this.telemetryData.hamilton.currentTime = ham.lap_time;
                    }
                    if (ham.position) {
                        this.updateDriverPosition('hamilton', ham.position);
                    }
                }
                
                // Update Verstappen data  
                if (data['Max Verstappen']) {
                    const ver = data['Max Verstappen'];
                    this.updateDriverData('ver', ver.speed, ver.rpm, ver.gear, ver.throttle, ver.brake);
                    
                    // Update additional live data if available
                    if (ver.lap_time) {
                        this.telemetryData.verstappen.currentTime = ver.lap_time;
                    }
                    if (ver.position) {
                        this.updateDriverPosition('verstappen', ver.position);
                    }
                }
                
                // If live data, add extra visual indicators
                if (this.dataSource === 'live') {
                    console.log('🔴 LIVE TELEMETRY UPDATE:', this.sessionName);
                }
            }
        } catch (error) {
            console.error('Failed to fetch telemetry data:', error);
            // Generate fallback realistic data
            this.generateRealisticData();
        }
    }

    updateDataSourceIndicator(meta) {
        const indicator = document.querySelector('.data-source-indicator');
        if (indicator) {
            indicator.remove();
        }

        const newIndicator = document.createElement('div');
        newIndicator.className = 'data-source-indicator';
        
        if (meta.data_source === 'live') {
            newIndicator.innerHTML = `
                <span class="data-badge live">🔴 LIVE DATA</span>
                <small>Real F1 telemetry • ${meta.session_name}</small>
            `;
        } else if (meta.data_source === 'algorithmic_simulation') {
            newIndicator.innerHTML = `
                <span class="data-badge simulation">📊 ALGORITHMIC</span>
                <small>Advanced simulation • ${meta.note || 'High accuracy modeling'}</small>
            `;
        } else {
            newIndicator.innerHTML = `
                <span class="data-badge fallback">⚠️ FALLBACK</span>
                <small>Backup mode • ${meta.error || 'Limited data'}</small>
            `;
        }
        
        document.querySelector('.telemetry-header').appendChild(newIndicator);
    }

    updateDriverPosition(driver, position) {
        const positionElement = document.querySelector(`.${driver}-position`);
        if (positionElement) {
            positionElement.textContent = `P${position}`;
        }
    }

    updateDriverData(prefix, speed, rpm, gear, throttle, brake) {
        // Update speed
        const speedEl = document.getElementById(`${prefix}-speed`);
        if (speedEl) speedEl.textContent = Math.round(speed);

        // Update RPM  
        const rpmEl = document.getElementById(`${prefix}-rpm`);
        if (rpmEl) rpmEl.textContent = Math.round(rpm).toLocaleString();

        // Update gear
        const gearEl = document.getElementById(`${prefix}-gear`);
        if (gearEl) gearEl.textContent = gear;

        // Update throttle bar
        const throttleEl = document.getElementById(`${prefix}-throttle`);
        if (throttleEl) {
            throttleEl.style.width = `${Math.round(throttle)}%`;
            throttleEl.parentElement.nextElementSibling.textContent = `${Math.round(throttle)}%`;
        }

        // Update brake bar
        const brakeEl = document.getElementById(`${prefix}-brake`);
        if (brakeEl) {
            brakeEl.style.width = `${Math.round(brake)}%`;
            brakeEl.parentElement.nextElementSibling.textContent = `${Math.round(brake)}%`;
        }
    }

    generateRealisticData() {
        // Simulate realistic F1 telemetry changes
        const drivers = ['hamilton', 'verstappen'];
        
        drivers.forEach(driver => {
            const data = this.telemetryData[driver];
            
            // Update speed (realistic F1 speed patterns)
            const speedVariation = (Math.random() - 0.5) * 20;
            data.speed = Math.max(200, Math.min(350, data.speed + speedVariation));
            
            // Update RPM based on speed and gear
            const targetRPM = (data.speed / data.gear) * 45 + Math.random() * 500;
            data.rpm = Math.max(8000, Math.min(12000, targetRPM));
            
            // Update throttle (varies with speed patterns)
            const throttleTarget = Math.random() > 0.3 ? 70 + Math.random() * 30 : Math.random() * 20;
            data.throttle = Math.max(0, Math.min(100, throttleTarget));
            
            // Update brake (opposite to throttle, realistic braking zones)
            data.brake = data.throttle < 30 && Math.random() > 0.7 ? Math.random() * 80 : 0;
            
            // Update gear based on speed
            if (data.speed > 320) data.gear = 8;
            else if (data.speed > 280) data.gear = 7;
            else if (data.speed > 240) data.gear = 6;
            else if (data.speed > 200) data.gear = 5;
            else data.gear = 4;
            
            // Update lap times (simulate progression)
            if (Math.random() > 0.99) { // Occasionally update lap time
                const lapTime = this.generateLapTime(driver);
                data.currentTime = lapTime;
                
                // Update best time if current is faster
                if (this.compareLapTimes(lapTime, data.bestTime) < 0) {
                    data.bestTime = lapTime;
                }
            }
        });
    }

    generateLapTime(driver) {
        const baseTime = driver === 'hamilton' ? 83.5 : 82.8; // Base lap time in seconds
        const variation = (Math.random() - 0.5) * 2; // ±1 second variation
        const totalSeconds = baseTime + variation;
        
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = (totalSeconds % 60).toFixed(3);
        
        return `${minutes}:${seconds.padStart(6, '0')}`;
    }

    compareLapTimes(time1, time2) {
        const toSeconds = (time) => {
            const [min, sec] = time.split(':');
            return parseInt(min) * 60 + parseFloat(sec);
        };
        
        return toSeconds(time1) - toSeconds(time2);
    }

    updateDisplayValues() {
        const drivers = ['hamilton', 'verstappen'];
        
        drivers.forEach(driver => {
            const prefix = driver === 'hamilton' ? 'ham' : 'ver';
            const data = this.telemetryData[driver];
            
            // Update speed
            const speedElement = document.getElementById(`${prefix}-speed`);
            if (speedElement) {
                speedElement.textContent = Math.round(data.speed);
                this.animateValueChange(speedElement);
            }
            
            // Update RPM
            const rpmElement = document.getElementById(`${prefix}-rpm`);
            if (rpmElement) {
                rpmElement.textContent = Math.round(data.rpm).toLocaleString();
                this.animateValueChange(rpmElement);
            }
            
            // Update gear
            const gearElement = document.getElementById(`${prefix}-gear`);
            if (gearElement) {
                gearElement.textContent = data.gear;
                this.animateValueChange(gearElement);
            }
            
            // Update throttle
            const throttleBar = document.getElementById(`${prefix}-throttle`);
            const throttlePercentage = throttleBar?.nextElementSibling;
            if (throttleBar && throttlePercentage) {
                throttleBar.style.width = `${data.throttle}%`;
                throttlePercentage.textContent = `${Math.round(data.throttle)}%`;
            }
            
            // Update brake
            const brakeBar = document.getElementById(`${prefix}-brake`);
            const brakePercentage = brakeBar?.nextElementSibling;
            if (brakeBar && brakePercentage) {
                brakeBar.style.width = `${data.brake}%`;
                brakePercentage.textContent = `${Math.round(data.brake)}%`;
            }
            
            // Update lap times
            const currentTimeElement = document.getElementById(`${prefix}-current-time`);
            if (currentTimeElement) {
                currentTimeElement.textContent = data.currentTime;
            }
            
            const bestTimeElement = document.getElementById(`${prefix}-best-time`);
            if (bestTimeElement) {
                bestTimeElement.textContent = data.bestTime;
            }
        });
    }

    animateValueChange(element) {
        element.style.transform = 'scale(1.1)';
        element.style.color = '#00ff41';
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
            element.style.color = '';
        }, 150);
    }

    updateCharts() {
        // Update speed chart
        if (this.charts.speed) {
            this.charts.speed.data.datasets[0].data.shift();
            this.charts.speed.data.datasets[0].data.push(this.telemetryData.hamilton.speed);
            this.charts.speed.data.datasets[1].data.shift();
            this.charts.speed.data.datasets[1].data.push(this.telemetryData.verstappen.speed);
            this.charts.speed.update('none');
        }
        
        // Update throttle chart
        if (this.charts.throttle) {
            this.charts.throttle.data.datasets[0].data.shift();
            this.charts.throttle.data.datasets[0].data.push(this.telemetryData.hamilton.throttle);
            this.charts.throttle.data.datasets[1].data.shift();
            this.charts.throttle.data.datasets[1].data.push(this.telemetryData.verstappen.throttle);
            this.charts.throttle.update('none');
        }
        
        // Update brake chart
        if (this.charts.brake) {
            this.charts.brake.data.datasets[0].data.shift();
            this.charts.brake.data.datasets[0].data.push(this.telemetryData.hamilton.brake);
            this.charts.brake.data.datasets[1].data.shift();
            this.charts.brake.data.datasets[1].data.push(this.telemetryData.verstappen.brake);
            this.charts.brake.update('none');
        }
    }

    updateCarPositions() {
        setInterval(() => {
            const hamiltonCar = document.querySelector('.car-position.hamilton');
            const verstappenCar = document.querySelector('.car-position.verstappen');
            
            if (hamiltonCar && verstappenCar) {
                // Simulate car movement around track
                const time = Date.now() / 1000;
                
                // Hamilton position
                const hamAngle = (time * 0.5) % (2 * Math.PI);
                const hamRadius = 80;
                const hamX = 200 + hamRadius * Math.cos(hamAngle);
                const hamY = 150 + hamRadius * Math.sin(hamAngle);
                hamiltonCar.setAttribute('cx', hamX);
                hamiltonCar.setAttribute('cy', hamY);
                
                // Verstappen position (slightly ahead)
                const verAngle = ((time * 0.5) + 0.3) % (2 * Math.PI);
                const verRadius = 75;
                const verX = 200 + verRadius * Math.cos(verAngle);
                const verY = 150 + verRadius * Math.sin(verAngle);
                verstappenCar.setAttribute('cx', verX);
                verstappenCar.setAttribute('cy', verY);
            }
        }, 50);
    }
}

// Initialize the dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new F1TelemetryDashboard();
});

// Add some interactive features
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('driver-panel')) {
        e.target.style.transform = 'scale(1.02)';
        setTimeout(() => {
            e.target.style.transform = '';
        }, 200);
    }
});

// Keyboard shortcuts for demo purposes
document.addEventListener('keydown', (e) => {
    switch(e.key) {
        case '1':
            // Toggle Hamilton data highlight
            const hamPanel = document.querySelector('.left-panel');
            hamPanel.style.border = '2px solid #00d2be';
            setTimeout(() => hamPanel.style.border = '', 1000);
            break;
        case '2':
            // Toggle Verstappen data highlight
            const verPanel = document.querySelector('.right-panel');
            verPanel.style.border = '2px solid #0600ef';
            setTimeout(() => verPanel.style.border = '', 1000);
            break;
        case 'd':
            // Toggle DRS animation
            const drsZone = document.querySelector('.drs-zone');
            if (drsZone) {
                drsZone.style.opacity = drsZone.style.opacity === '0.8' ? '0.3' : '0.8';
            }
            break;
    }
});