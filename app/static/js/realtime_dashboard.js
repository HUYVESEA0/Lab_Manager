/**
 * Real-time Dashboard Enhancement
 * Socket.IO integration for live updates
 */

// Real-time features enhancement for existing dashboard
class RealTimeDashboard {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.init();
    }

    init() {
        this.initializeSocketIO();
        this.setupRealTimeHandlers();
    }

    initializeSocketIO() {
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                this.isConnected = true;
                console.log('✅ Real-time connection established');
                this.updateConnectionStatus(true);
                this.socket.emit('join_admin_dashboard');
            });
            
            this.socket.on('disconnect', () => {
                this.isConnected = false;
                console.log('❌ Real-time connection lost');
                this.updateConnectionStatus(false);
            });
            
            this.socket.on('system_metrics_update', (data) => {
                this.handleRealTimeUpdate(data);
            });
            
            this.socket.on('connect_error', (error) => {
                console.error('Socket connection error:', error);
                this.updateConnectionStatus(false);
            });
        } else {
            console.warn('Socket.IO not available');
        }
    }

    updateConnectionStatus(connected) {
        // Update status indicator in dashboard
        const statusIndicator = document.querySelector('.system-status');
        const liveBadge = document.querySelector('.status-badge');
        
        if (statusIndicator) {
            if (connected) {
                statusIndicator.classList.remove('offline');
                statusIndicator.classList.add('online');
                const statusText = statusIndicator.querySelector('span');
                if (statusText) {
                    statusText.textContent = 'Hệ thống hoạt động - Kết nối real-time';
                }
            } else {
                statusIndicator.classList.remove('online');
                statusIndicator.classList.add('offline');
                const statusText = statusIndicator.querySelector('span');
                if (statusText) {
                    statusText.textContent = 'Hệ thống hoạt động - Kết nối bị gián đoạn';
                }
            }
        }
        
        if (liveBadge) {
            if (connected) {
                liveBadge.className = 'status-badge online';
                liveBadge.innerHTML = '<i class="fas fa-circle"></i> Live';
            } else {
                liveBadge.className = 'status-badge offline';
                liveBadge.innerHTML = '<i class="fas fa-circle"></i> Offline';
            }
        }
    }

    handleRealTimeUpdate(data) {
        console.log('📊 Received real-time update:', data);
        
        try {
            // Update system performance metrics
            if (data.system) {
                this.updateSystemMetrics(data.system);
            }
            
            // Update user activity
            if (data.users) {
                this.updateUserActivity(data.users);
            }
            
            // Update timestamp
            this.updateTimestamp();
            
            // Show real-time indicator
            this.showRealTimeIndicator();
            
        } catch (error) {
            console.error('Error processing real-time update:', error);
        }
    }

    updateSystemMetrics(systemData) {
        // Update CPU
        if (systemData.cpu) {
            this.updateMetricCard('cpu', systemData.cpu.percent, systemData.cpu.status);
        }
        
        // Update Memory
        if (systemData.memory) {
            this.updateMetricCard('memory', systemData.memory.percent, systemData.memory.status);
        }
        
        // Update Disk
        if (systemData.disk) {
            this.updateMetricCard('disk', systemData.disk.percent, systemData.disk.status);
        }
    }

    updateMetricCard(type, percent, status) {
        // Update percentage display
        const valueElement = document.querySelector(`.metric-value[data-metric="${type}"]`);
        if (valueElement) {
            this.animateNumberChange(valueElement, percent + '%');
        }
        
        // Update progress bar
        const progressBar = document.querySelector(`.metric-bar[data-metric="${type}"] .bar-fill`);
        if (progressBar) {
            progressBar.style.width = percent + '%';
            progressBar.className = `bar-fill ${status}`;
        }
        
        // Update status text
        const statusElement = document.querySelector(`.metric-status[data-metric="${type}"]`);
        if (statusElement) {
            const statusTexts = {
                'good': 'Normal',
                'warning': 'High', 
                'critical': 'Critical'
            };
            statusElement.textContent = statusTexts[status] || 'Unknown';
            statusElement.className = `metric-status ${status}`;
        }
    }

    updateUserActivity(userData) {
        // Update user counts with animation
        this.updateCountDisplay('.total-users-count', userData.total_users);
        this.updateCountDisplay('.active-users-count', userData.active_users);
        this.updateCountDisplay('.today-logins-count', userData.today_logins);
        this.updateCountDisplay('.active-sessions-count', userData.active_sessions);
        
        // Update recent activities
        if (userData.recent_activities) {
            this.updateActivityFeed(userData.recent_activities);
        }
    }

    updateCountDisplay(selector, newValue) {
        const element = document.querySelector(selector);
        if (element) {
            this.animateNumberChange(element, newValue);
        }
    }

    animateNumberChange(element, newValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const targetValue = parseInt(newValue) || 0;
        
        if (currentValue !== targetValue) {
            element.style.transform = 'scale(1.1)';
            element.style.transition = 'transform 0.2s ease';
            
            setTimeout(() => {
                element.textContent = newValue;
                element.style.transform = 'scale(1)';
            }, 100);
        }
    }

    updateActivityFeed(activities) {
        const feedContainer = document.querySelector('.activity-feed');
        if (!feedContainer) return;
        
        // Clear existing items
        feedContainer.innerHTML = '';
        
        // Add new activities with animation
        activities.slice(0, 5).forEach((activity, index) => {
            setTimeout(() => {
                const activityItem = this.createActivityItem(activity);
                feedContainer.appendChild(activityItem);
                
                // Animate in
                requestAnimationFrame(() => {
                    activityItem.style.opacity = '1';
                    activityItem.style.transform = 'translateY(0)';
                });
            }, index * 100);
        });
    }

    createActivityItem(activity) {
        const item = document.createElement('div');
        item.className = 'activity-item';
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        item.style.transition = 'all 0.3s ease';
        
        item.innerHTML = `
            <div class="activity-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="activity-content">
                <div class="activity-text">
                    <strong>${activity.user}</strong> ${activity.action}
                </div>
                <div class="activity-time">${activity.time}</div>
            </div>
        `;
        
        return item;
    }

    updateTimestamp() {
        const timeElement = document.querySelector('#current-time');
        if (timeElement) {
            const now = new Date();
            const timeString = now.toLocaleTimeString('vi-VN');
            timeElement.textContent = timeString;
        }
    }

    showRealTimeIndicator() {
        // Show a brief flash to indicate real-time update
        const indicator = document.querySelector('.status-badge.online');
        if (indicator) {
            indicator.style.animation = 'pulse 0.5s ease';
            setTimeout(() => {
                indicator.style.animation = '';
            }, 500);
        }
    }

    setupRealTimeHandlers() {
        // Refresh button with real-time connection
        const refreshBtn = document.querySelector('[onclick="refreshDashboard()"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                if (this.isConnected) {
                    // Request immediate update
                    this.socket.emit('request_immediate_update');
                }
            });
        }
    }
}

// Initialize real-time dashboard
let realTimeDashboard = null;

document.addEventListener('DOMContentLoaded', function() {
    realTimeDashboard = new RealTimeDashboard();
});

// Export for global access
window.RealTimeDashboard = RealTimeDashboard;
