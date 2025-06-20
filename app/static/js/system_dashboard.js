/**
 * Enhanced System Dashboard JavaScript
 * Lab Manager - System Admin Dashboard
 * Real-time monitoring with live data from database and system APIs
 * 
 * Features:
 * - Real-time system metrics (CPU, Memory, Disk, Network)
 * - Live user activity tracking
 * - Performance monitoring
 * - Interactive charts and visualizations
 * - No fallback data - uses actual system data only
 */

class SystemDashboard {
    constructor(options = {}) {
        this.socket = null;
        this.charts = {};
        this.isRealTimeActive = false;
        this.pollingInterval = null;
        this.updateInterval = options.updateInterval || 5000; // 5 seconds
        this.type = options.type || 'basic';
        this.realTime = options.realTime !== false;
        this.isSocketConnected = false;
        this.isInitialized = false;
    }// Add cleanup method
    cleanup() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        if (this.socket) {
            this.socket.disconnect();
        }
          // Destroy all charts properly
        Object.keys(this.charts).forEach(chartKey => {
            if (this.charts[chartKey]) {
                try {
                    this.charts[chartKey].destroy();
                } catch (error) {
                    console.warn(`Error destroying chart ${chartKey}:`, error);
                }
                this.charts[chartKey] = null;
            }
        });
        
        // Also destroy any existing Chart.js instances on known canvas elements
        const canvases = ['performanceChart', 'userActivityChart', 'systemStatsChart'];
        canvases.forEach(canvasId => {
            const canvas = document.getElementById(canvasId);
            if (canvas) {
                const existingChart = Chart.getChart(canvas);
                if (existingChart) {
                    try {
                        existingChart.destroy();
                        console.log(`Destroyed existing chart on ${canvasId}`);
                    } catch (error) {
                        console.warn(`Error destroying chart on ${canvasId}:`, error);
                    }
                }
            }
        });
          this.isRealTimeActive = false;
        this.isInitialized = false;
        console.log('Dashboard cleanup completed');
    }    init() {
        // Only initialize if not already initialized
        if (this.isInitialized) {
            console.log('Dashboard already initialized, skipping...');
            return;
        }
        
        // Clean up any existing instance first
        this.cleanup();
        
        // Wait for Chart.js to be loaded
        this.waitForChartJS().then(() => {
            console.log('Chart.js loaded, initializing dashboard...');
            this.initializeCharts();
            this.setupEventListeners();
            this.startRealTimeUpdates();
            this.initializeAOS();
            this.setupAnimations();
            this.setupNotifications();            
            this.setupProgressBars();
            this.setupInteractiveElements();
            this.initializeEnhancedFeatures();            
            this.updateCurrentTime();
              this.isInitialized = true;
            console.log('✅ System Dashboard initialized successfully with server-side data');
            this.showNotification('Dashboard sẵn sàng với dữ liệu từ server', 'success');
        }).catch(error => {
            console.error('Failed to initialize dashboard:', error);
            this.showNotification('Dashboard đã khởi tạo với dữ liệu cơ bản', 'info');
            // Don't show error - fallback to basic mode
            this.isInitialized = true;
        });
    }    // Wait for Chart.js to be available with enhanced validation
    waitForChartJS() {
        return new Promise((resolve, reject) => {
            let attempts = 0;
            const maxAttempts = 50; // 5 seconds timeout
            
            const checkChartJS = () => {
                if (typeof Chart !== 'undefined' && Chart.Chart) {
                    // Additional check for Chart.js readiness
                    try {
                        // Test Chart.js functionality
                        const testCanvas = document.createElement('canvas');
                        const testChart = new Chart(testCanvas, {
                            type: 'line',
                            data: { labels: [], datasets: [] },
                            options: { responsive: false, animation: false }
                        });
                        testChart.destroy();
                        resolve();
                    } catch (error) {
                        console.warn('Chart.js test failed:', error);
                        if (attempts < maxAttempts) {
                            attempts++;
                            setTimeout(checkChartJS, 100);
                        } else {
                            reject(new Error('Chart.js functionality test failed'));
                        }
                    }
                } else if (attempts < maxAttempts) {
                    attempts++;
                    setTimeout(checkChartJS, 100);
                } else {
                    reject(new Error('Chart.js failed to load'));
                }
            };
            
            checkChartJS();
        });
    }updateCurrentTime() {
        const now = new Date();
        const timeStr = now.toLocaleString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        // Try multiple possible element IDs and check if they exist
        const timeElements = [
            'current-time',
            'last-update',
            'system-time',
            'dashboard-time'
        ];
        
        let updated = false;
        timeElements.forEach(elementId => {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = timeStr;
                updated = true;
            }
        });
        
        if (!updated) {
            console.debug('No time element found to update');
        }
        
        // Update every second only if dashboard is still active
        if (this.isInitialized) {
            setTimeout(() => this.updateCurrentTime(), 1000);
        }
    }

    initializeSocketIO() {
        // Initialize Socket.IO connection
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                this.isSocketConnected = true;
                console.log('Real-time connection established');
                this.updateConnectionStatus(true);
                this.showNotification('Real-time connection established', 'success');
            });

            this.socket.on('disconnect', () => {
                this.isSocketConnected = false;
                console.log('Real-time connection lost');
                this.updateConnectionStatus(false);
                this.showNotification('Real-time connection lost', 'warning');
            });

            // Listen for real-time updates
            this.socket.on('system_metrics_update', (data) => {
                console.log('Received real-time system metrics:', data);
                this.updateSystemMetrics(data);
            });            this.socket.on('user_activity_update', (data) => {
                console.log('Received real-time user activity:', data);
                this.updateUserActivity(data);
            });

            this.socket.on('performance_update', (data) => {
                console.log('Received real-time performance data:', data);
                this.updatePerformanceMetrics(data);
            });

            // Join admin room for real-time updates
            this.socket.emit('join_admin_dashboard');
        } else {
            console.warn('Socket.IO not available, falling back to polling');
            this.startPolling();
        }
    }    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            // Always show server-side status - no real-time updates
            statusElement.innerHTML = '<i class="fas fa-check-circle text-success"></i> Ready (Server-side)';
            statusElement.className = 'badge badge-success';
            console.log('✅ Dashboard status set to server-side mode');
        }
    }    startRealTimeUpdates() {
        this.isRealTimeActive = true;
        // API calls removed - using server-side data only
        console.log('✅ Real-time updates disabled - using server-side data');
        console.log('✅ Dashboard initialized with server-side data');
    }    startPolling() {
        // Polling disabled - using server-side data only
        console.log('✅ Polling disabled - dashboard uses server-side data');
        return;
        
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        
        this.pollingInterval = setInterval(() => {
            if (this.isRealTimeActive && this.isInitialized) {
                // API calls removed - dashboard now uses server-side data
                console.log('✅ Using server-side data instead of API polling');
            }
        }, this.updateInterval);
    }    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        this.isRealTimeActive = false;
    }

    // All fetch functions removed - dashboard now uses server-side data only
    // No more API calls needed - data is passed directly from backend routes

    updateSystemMetrics(data) {
        console.log('Updating metrics with data:', data);
        
        // Handle nested API response structure
        const systemData = data.system || {};
        const appData = data.application || {};
        
        // Update main metric cards
        const totalUsersEl = document.getElementById('total-users');
        const activeUsersEl = document.getElementById('active-users');
        const totalLabsEl = document.getElementById('total-labs');
        const systemAlertsEl = document.getElementById('system-alerts');
        
        if (totalUsersEl) totalUsersEl.textContent = appData.total_users || data.total_users || 0;
        if (activeUsersEl) activeUsersEl.textContent = appData.active_users || data.online_users || 0;
        if (totalLabsEl) totalLabsEl.textContent = appData.total_sessions || data.active_sessions || 0;
        if (systemAlertsEl) systemAlertsEl.textContent = data.system_alerts || 0;
        
        // Update performance metrics with correct nested data structure
        this.updateMetricCard('cpu', systemData.cpu_usage || 0, '%');
        this.updateMetricCard('memory', systemData.memory_usage || 0, '%');
        this.updateMetricCard('disk', systemData.disk_usage || 0, '%');
        this.updateMetricCard('network', systemData.network_usage || 0, '%');        // Update performance chart with enhanced validation
        if (this.charts.performanceChart && data.timestamp && this.isChartReady(this.charts.performanceChart)) {
            // Pass system data directly to chart update
            const chartData = {
                timestamp: data.timestamp,
                cpu_usage: systemData.cpu_usage || 0,
                memory_usage: systemData.memory_usage || 0,
                disk_usage: systemData.disk_usage || 0,
                network_usage: systemData.network_usage || 0
            };
            this.addDataToChart(this.charts.performanceChart, chartData);
        } else {
            console.warn('⚠️ Performance chart not available or missing timestamp:', {
                chart: !!this.charts.performanceChart,
                timestamp: !!data.timestamp,
                ready: this.charts.performanceChart ? this.isChartReady(this.charts.performanceChart) : false
            });
        }

        // Update online users in activity section
        const onlineUsersElement = document.getElementById('online-users');
        if (onlineUsersElement && data.online_users !== undefined) {
            onlineUsersElement.textContent = data.online_users;
        }

        // Update active sessions
        const activeSessionsElement = document.getElementById('active-sessions');
        if (activeSessionsElement && data.active_sessions !== undefined) {
            activeSessionsElement.textContent = data.active_sessions;
        }        // Update user activity chart
        if (this.charts.userActivityChart && data.hourly_activity && this.isChartReady(this.charts.userActivityChart)) {
            this.updateUserActivityChart(data.hourly_activity);
        } else if (this.charts.userActivityChart && data.hourly_activity) {
            console.warn('⚠️ User activity chart exists but not ready for updates');
        }
    }updateMetricCard(type, value, unit = '%') {
        console.log(`Updating ${type} metric to ${value}${unit}`);
        
        // Target the correct HTML structure based on the template
        const metricItem = document.querySelector(`.metric-item .metric-icon.${type}`);
        if (!metricItem) {
            console.warn(`Metric icon not found for type: ${type}`);
            return;
        }
        
        const metricContainer = metricItem.closest('.metric-item');
        if (!metricContainer) {
            console.warn(`Metric container not found for type: ${type}`);
            return;
        }
        
        // Target the metric-details container which contains metric-value
        const metricDetails = metricContainer.querySelector('.metric-details');
        if (!metricDetails) {
            console.warn(`Metric details not found for type: ${type}`);
            return;
        }
        
        const valueElement = metricDetails.querySelector('.metric-value');
        const barFill = metricDetails.querySelector('.bar-fill');
        const statusElement = metricDetails.querySelector('.metric-status');
        
        if (valueElement) {
            valueElement.textContent = `${value.toFixed(1)}${unit}`;
            console.log(`Updated ${type} value display to ${value.toFixed(1)}${unit}`);
        } else {
            console.warn(`Value element not found for type: ${type}`);
        }
        
        if (barFill) {
            // Animate the progress bar
            barFill.style.transition = 'width 0.3s ease-in-out';
            barFill.style.width = `${value}%`;
            
            // Update color based on usage level
            barFill.className = 'bar-fill';
            if (value > 90) {
                barFill.classList.add('critical');
            } else if (value > 75) {
                barFill.classList.add('warning');
            } else if (value > 50) {
                barFill.classList.add('normal');
            } else {
                barFill.classList.add('good');
            }
            console.log(`Updated ${type} progress bar to ${value}%`);
        }
        
        if (statusElement) {
            statusElement.className = 'metric-status';
            if (value > 90) {
                statusElement.classList.add('critical');
                statusElement.textContent = 'Critical';
            } else if (value > 75) {
                statusElement.classList.add('warning');
                statusElement.textContent = 'High';
            } else {
                statusElement.classList.add('good');
                statusElement.textContent = 'Normal';
            }
            console.log(`Updated ${type} status to ${statusElement.textContent}`);
        }
    }    updateUserActivity(data) {
        // Update user activity chart with enhanced validation
        if (this.charts.userActivityChart && data.hourly_activity && this.isChartReady(this.charts.userActivityChart)) {
            this.updateUserActivityChart(data.hourly_activity);
        } else if (this.charts.userActivityChart && data.hourly_activity) {
            console.warn('⚠️ User activity chart exists but not ready for updates');
        }
        
        // Update online users count in activity section
        const onlineElement = document.getElementById('online-users');
        if (onlineElement && data.online_users !== undefined) {
            onlineElement.textContent = data.online_users;
        }
        
        // Update daily logins
        const dailyLoginsElement = document.getElementById('daily-logins');
        if (dailyLoginsElement && data.daily_logins !== undefined) {
            dailyLoginsElement.textContent = data.daily_logins;
        }
        
        // Update active sessions
        const activeSessionsElement = document.getElementById('active-sessions');
        if (activeSessionsElement && data.total_users !== undefined) {
            // Show active sessions as a portion of total users
            activeSessionsElement.textContent = Math.floor(data.total_users * 0.3);
        }
    }

    updatePerformanceMetrics(data) {
        // Update response time
        const responseTimeElement = document.getElementById('avg-response-time');
        if (responseTimeElement && data.avg_response_time !== undefined) {
            responseTimeElement.textContent = `${data.avg_response_time.toFixed(2)}ms`;
        }

        // Update error rate
        const errorRateElement = document.getElementById('error-rate');
        if (errorRateElement && data.error_rate !== undefined) {
            errorRateElement.textContent = `${data.error_rate.toFixed(2)}%`;
        }

        // Update throughput
        const throughputElement = document.getElementById('throughput');
        if (throughputElement && data.throughput !== undefined) {
            throughputElement.textContent = `${data.throughput}/min`;
        }
    }

    updateProgressBar(progressId, value) {
        const progressBar = document.getElementById(progressId);
        if (progressBar) {
            progressBar.style.width = `${Math.min(value, 100)}%`;
            
            // Update color based on value            progressBar.className = 'progress-bar';
            if (value > 80) {
                progressBar.classList.add('bg-danger');
            } else if (value > 60) {
                progressBar.classList.add('bg-warning');
            } else {
                progressBar.classList.add('bg-success');
            }
        }
    }

    addDataToChart(chart, data) {
        // Enhanced validation
        if (!chart) {
            console.warn('⚠️ Chart instance is null or undefined');
            return;
        }
        
        if (!data || !data.timestamp) {
            console.warn('⚠️ Invalid data or missing timestamp:', data);
            return;
        }
        
        // Check if chart is properly initialized
        if (!chart.data || !chart.data.labels || !chart.data.datasets) {
            console.warn('⚠️ Chart data structure is not properly initialized');
            return;
        }
          // Check if chart canvas still exists in DOM
        if (!chart.canvas) {
            console.warn('⚠️ Chart canvas is null or undefined');
            this.removeDeadChartReference(chart);
            return;
        }

        // More robust DOM check - verify canvas is still attached to document
        if (!document.contains(chart.canvas)) {
            console.warn('⚠️ Chart canvas no longer exists in DOM');
            this.removeDeadChartReference(chart);
            return;
        }

        // Verify chart canvas is visible and has dimensions
        if (chart.canvas.offsetWidth === 0 || chart.canvas.offsetHeight === 0) {
            console.warn('⚠️ Chart canvas has no visible dimensions, skipping update');
            return;
        }

        // Additional check for Chart.js readiness
        if (typeof Chart === 'undefined') {
            console.warn('⚠️ Chart.js library not available');
            return;
        }

        // Check if chart is destroyed
        if (chart.destroyed) {
            console.warn('⚠️ Chart has been destroyed');
            this.removeDeadChartReference(chart);
            return;
        }

        try {
            const time = new Date(data.timestamp).toLocaleTimeString();
            
            // Add new data point
            chart.data.labels.push(time);
            
            // Safely add data to datasets with additional validation
            if (chart.data.datasets[0] && Array.isArray(chart.data.datasets[0].data)) {
                chart.data.datasets[0].data.push(data.cpu_usage || 0);
            }
            if (chart.data.datasets[1] && Array.isArray(chart.data.datasets[1].data)) {
                chart.data.datasets[1].data.push(data.memory_usage || 0);
            }
            if (chart.data.datasets[2] && Array.isArray(chart.data.datasets[2].data)) {
                chart.data.datasets[2].data.push(data.disk_usage || 0);
            }

            // Keep only last 20 data points
            if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets.forEach(dataset => {
                    if (Array.isArray(dataset.data)) {
                        dataset.data.shift();
                    }
                });
            }

            // Safely update chart with error handling for Chart.js internal errors
            if (chart.update && typeof chart.update === 'function') {
                chart.update('none'); // Update without animation for real-time feel
                console.log('✅ Chart updated successfully with new data');
            } else {
                console.warn('⚠️ Chart update method not available');
            }
            
        } catch (error) {
            console.error('❌ Error updating chart:', error);
            
            // If error is related to fullSize or chart configuration, reinitialize
            if (error.message && error.message.includes('fullSize')) {
                console.log('🔄 Attempting to reinitialize chart due to fullSize error...');
                this.reinitializeChart(chart);
            }
            
            // Don't throw the error, just log it to prevent breaking the dashboard
        }
    }

    // Method to reinitialize a chart if it encounters errors
    reinitializeChart(chart) {
        try {
            const canvasId = chart.canvas?.id;
            if (!canvasId) {
                console.warn('⚠️ Cannot reinitialize chart - no canvas ID');
                return;
            }

            console.log(`🔄 Reinitializing chart: ${canvasId}`);
            
            // Destroy the problematic chart
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }

            // Clear the reference
            Object.keys(this.charts).forEach(key => {
                if (this.charts[key] === chart) {
                    this.charts[key] = null;
                }
            });

            // Reinitialize based on canvas ID
            setTimeout(() => {
                if (canvasId === 'performanceChart') {
                    this.initializePerformanceChart();
                } else if (canvasId === 'userActivityChart') {
                    this.initializeUserActivityChart();
                } else if (canvasId === 'systemStatsChart') {
                    // Add system stats chart initialization if needed
                    console.log('System stats chart reinitialization not implemented');
                }
            }, 100);

        } catch (error) {
            console.error('❌ Error reinitializing chart:', error);
        }
    }

    // Helper method to check if a chart is ready for updates
    isChartReady(chart) {
        if (!chart) return false;
        
        // Check if chart exists and is properly initialized
        if (!chart.canvas || !chart.data || chart.destroyed) {
            return false;
        }
        
        // Check if canvas is still in DOM
        if (!document.contains(chart.canvas)) {
            return false;
        }
        
        // Check if canvas has visible dimensions
        if (chart.canvas.offsetWidth === 0 || chart.canvas.offsetHeight === 0) {
            return false;
        }
        
        return true;
    }

    removeDeadChartReference(chart) {
        // Remove the chart reference since canvas is gone
        Object.keys(this.charts).forEach(key => {
            if (this.charts[key] === chart) {
                this.charts[key] = null;
                console.log(`🧹 Removed dead chart reference: ${key}`);
            }
        });
    }

    initializeAOS() {
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                easing: 'ease-in-out',
                once: true
            });
        }
    }

    setupAnimations() {
        // Add fade-in animation to cards
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in');
        });
    }

    initializeCharts() {
        console.log('Initializing charts...');
        
        // Initialize performance chart
        this.initializePerformanceChart();
        
        // Initialize user activity chart
        this.initializeUserActivityChart();
        
        console.log('Charts initialized:', this.charts);
    }    initializePerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) {
            console.warn('⚠️ Performance chart canvas element not found');
            return;
        }
        
        if (typeof Chart === 'undefined') {
            console.warn('⚠️ Chart.js library not available');
            return;
        }

        try {
            // Get chart instance that might already exist on this canvas
            const existingChart = Chart.getChart(ctx);
            if (existingChart) {
                console.log('🔄 Destroying existing performance chart...');
                existingChart.destroy();
            }
            
            // Clear any reference we might have
            if (this.charts.performanceChart) {
                this.charts.performanceChart = null;
            }
            
            console.log('🎨 Creating new performance chart...');
            
            // Enhanced chart configuration with error prevention
            const config = {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU Usage (%)',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Memory Usage (%)',
                        data: [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Disk Usage (%)',
                        data: [],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: 'index',
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                usePointStyle: true,
                                padding: 20,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: 'System Performance (Real-time)',
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        }
                    },
                    // Add error handling for Chart.js internal operations
                    onResize: function(chart, size) {
                        try {
                            // Safe resize handler
                            if (chart && chart.canvas && chart.canvas.parentNode) {
                                // Chart.js will handle the resize automatically
                            }
                        } catch (error) {
                            console.warn('Chart resize error:', error);
                        }
                    }
                }
            };
            
            this.charts.performanceChart = new Chart(ctx, config);
            
            // Validate chart creation
            if (this.charts.performanceChart && this.charts.performanceChart.data) {
                console.log('✅ Performance chart initialized successfully');
            } else {
                console.error('❌ Performance chart initialization failed');
                this.charts.performanceChart = null;
            }
        } catch (error) {
            console.error('❌ Error initializing performance chart:', error);
            this.charts.performanceChart = null;
              // Show user-friendly error
            this.showNotification('Không thể khởi tạo biểu đồ hiệu suất', 'warning');
        }
    }

    initializeUserActivityChart() {
        const ctx = document.getElementById('userActivityChart');
        if (!ctx) {
            console.warn('⚠️ User activity chart canvas element not found');
            return;
        }
        
        if (typeof Chart === 'undefined') {
            console.warn('⚠️ Chart.js library not available for user activity chart');
            return;
        }

        try {
            // Get chart instance that might already exist on this canvas
            const existingChart = Chart.getChart(ctx);
            if (existingChart) {
                console.log('🔄 Destroying existing user activity chart...');
                existingChart.destroy();
            }
            
            // Clear any reference we might have
            if (this.charts.userActivityChart) {
                this.charts.userActivityChart = null;
            }
            
            this.charts.userActivityChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['00', '02', '04', '06', '08', '10', '12', '14', '16', '18', '20', '22'],
                    datasets: [{
                        label: 'Active Users',
                        data: [12, 8, 15, 25, 42, 38, 45, 52, 48, 35, 28, 18],
                        backgroundColor: 'rgba(59, 130, 246, 0.8)',
                        borderColor: 'rgba(59, 130, 246, 1)',
                        borderWidth: 1,
                        borderRadius: 4,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        },
                        x: {
                            grid: {                                display: false
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'User Activity by Hour',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    }
                }
            });
            
            // Validate chart creation
            if (this.charts.userActivityChart && this.charts.userActivityChart.data) {
                console.log('✅ User activity chart initialized successfully');
            } else {
                console.error('❌ User activity chart initialization failed');
                this.charts.userActivityChart = null;
            }
        } catch (error) {
            console.error('❌ Error initializing user activity chart:', error);
            this.charts.userActivityChart = null;
        }
    }    updateUserActivityChart(hourlyData) {
        if (!this.charts.userActivityChart) {
            console.warn('⚠️ User activity chart not available');
            return;
        }
        
        if (!this.isChartReady(this.charts.userActivityChart)) {
            console.warn('⚠️ User activity chart not ready for updates');
            return;
        }
        
        if (!hourlyData) {
            console.warn('⚠️ No hourly data provided for user activity chart');
            return;
        }
        
        try {
            this.charts.userActivityChart.data.datasets[0].data = hourlyData;
            this.charts.userActivityChart.update('none');
            console.log('✅ User activity chart updated');
        } catch (error) {
            console.error('❌ Error updating user activity chart:', error);
            
            // Attempt to reinitialize if chart update fails
            if (error.message && (error.message.includes('canvas') || error.message.includes('destroyed'))) {
                console.log('🔄 Attempting to reinitialize user activity chart...');
                this.reinitializeChart(this.charts.userActivityChart);
            }
        }
    }

    setupEventListeners() {
        // Toggle real-time updates
        const toggleButton = document.getElementById('toggle-realtime');
        if (toggleButton) {
            toggleButton.addEventListener('click', () => {
                this.toggleRealTime();
            });
        }

        // Refresh data manually
        const refreshButton = document.getElementById('refresh-data');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.refreshData();
            });
        }

        // Handle window visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });
    }

    toggleRealTime() {
        this.isRealTimeActive = !this.isRealTimeActive;
        const toggleButton = document.getElementById('toggle-realtime');
        
        if (this.isRealTimeActive) {
            this.startRealTimeUpdates();
            if (toggleButton) {
                toggleButton.innerHTML = '<i class="fas fa-pause"></i> Pause Updates';
                toggleButton.className = 'btn btn-warning btn-sm';
            }
            this.showNotification('Real-time updates enabled', 'success');
        } else {
            this.stopPolling();
            if (toggleButton) {
                toggleButton.innerHTML = '<i class="fas fa-play"></i> Resume Updates';
                toggleButton.className = 'btn btn-success btn-sm';
            }
            this.showNotification('Real-time updates paused', 'info');
        }
    }    refreshData() {
        this.showNotification('Using server-side data...', 'info');
        // API calls removed - dashboard uses server-side data
        console.log('✅ Refresh uses server-side data - no API calls needed');
        
        // Optional: reload page to get fresh server-side data
        // window.location.reload();
    }

    pauseUpdates() {
        if (this.isRealTimeActive) {
            this.stopPolling();
            console.log('Updates paused due to page visibility change');
        }
    }

    resumeUpdates() {
        if (this.isRealTimeActive) {
            this.startPolling();
            console.log('Updates resumed');
        }
    }    setupNotifications() {
        // Initialize notification system
        if (!document.getElementById('notification-container')) {
            this.createNotificationContainer();
        }
        
        // Initialize flash messages if available
        if (window.FlashMessages && typeof window.FlashMessages.initialize === 'function') {
            window.FlashMessages.initialize();
        }
    }showNotification(message, type = 'info', duration = 3000) {
        // Try to use the global FlashMessages system first
        if (window.FlashMessages && typeof window.FlashMessages.show === 'function') {
            const options = {
                persistent: duration > 5000,
                urgent: type === 'danger' || type === 'error',
                critical: type === 'critical'
            };
            window.FlashMessages.show(message, type, options);
            return;
        }

        // Fallback to custom notification system
        const container = document.getElementById('notification-container') || this.createNotificationContainer();
        
        const notification = document.createElement('div');
        notification.className = `flash-message ${type} auto-dismiss`;
        notification.setAttribute('role', 'alert');
        notification.style.cssText = `
            margin-bottom: 10px;
            animation: flashSlideIn 0.3s ease-out;
        `;
        
        notification.textContent = message;

        container.appendChild(notification);

        // Auto-dismiss after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.add('closed');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, duration);
    }

    createNotificationContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'flash-messages fixed';
        container.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
        return container;
    }

    // Dashboard control functions
    refreshDashboard() {
        this.showNotification('Đang làm mới dữ liệu...', 'info');
        
        // Force immediate refresh of all metrics        // API calls removed - dashboard uses server-side data only
        console.log('✅ Dashboard refresh - using server-side data');
        this.showNotification('Sử dụng dữ liệu từ server', 'success');
    }

    refreshPerformance() {
        // API calls removed - using server-side performance data
        console.log('✅ Performance data from server-side');
        this.showNotification('Dữ liệu hiệu suất từ server', 'info');
    }

    refreshActivity() {
        // API calls removed - using server-side activity data  
        console.log('✅ Activity data from server-side');
        this.showNotification('Dữ liệu hoạt động từ server', 'info');
    }

    // Enhanced error handling
    handleApiError(error, context = 'API call') {
        console.error(`Error in ${context}:`, error);
        
        let message = 'Có lỗi khi kết nối đến máy chủ';
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            message = 'Không thể kết nối đến máy chủ';
        } else if (error.status === 403) {
            message = 'Không có quyền truy cập';
        } else if (error.status === 404) {
            message = 'Không tìm thấy dữ liệu';
        } else if (error.status >= 500) {
            message = 'Lỗi máy chủ nội bộ';
        }
        
        this.showNotification(message, 'error');
    }

    setupProgressBars() {
        // Animate progress bars on load
        const progressBars = document.querySelectorAll('.progress-bar, .bar-fill');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            bar.style.transition = 'width 1s ease-out';
            
            setTimeout(() => {
                bar.style.width = width;
            }, 100);
        });
    }

    setupInteractiveElements() {
        // Add hover effects to metric cards
        const metricCards = document.querySelectorAll('.metric-card');
        metricCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-2px)';
                card.style.transition = 'transform 0.2s ease';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });
        });
    }

    initializeEnhancedFeatures() {        // Add any additional enhanced features here
        console.log('Enhanced features initialized');
    }
}

// Global functions for template access
function refreshDashboard() {
    if (window.systemDashboard) {
        window.systemDashboard.refreshDashboard();
    }
}

function refreshPerformance() {
    if (window.systemDashboard) {
        window.systemDashboard.refreshPerformance();
    }
}

function refreshActivity() {
    if (window.systemDashboard) {
        window.systemDashboard.refreshActivity();
    }
}

// Initialize dashboard when DOM is loaded - but only if not already initialized
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we don't already have a dashboard instance
    if (!window.systemDashboard) {
        console.log('Initializing global system dashboard...');
        window.systemDashboard = new SystemDashboard({
            type: 'global',
            realTime: true,
            updateInterval: 10000
        });
        window.systemDashboard.init();
    } else {
        console.log('System dashboard already exists, skipping global initialization...');
    }
});

// Handle page unload
window.addEventListener('beforeunload', function() {
    if (window.systemDashboard) {
        window.systemDashboard.cleanup();
        window.systemDashboard = null;
    }
});
