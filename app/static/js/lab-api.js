/**
 * Lab Manager API Client
 * ===================
 * 
 * JavaScript client for interacting with the Lab Manager API endpoints.
 * Provides methods for all major API operations with proper error handling
 * and CSRF protection.
 */

class LabAPI {
    constructor() {
        this.baseURL = '';  // Use relative URLs
        this.csrfToken = null;
        this.init();
    }

    async init() {
        await this.loadCSRFToken();
    }    async loadCSRFToken() {
        try {
            // First try to get CSRF token from meta tag
            const metaToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            if (metaToken) {
                this.csrfToken = metaToken;
                return;
            }
            
            // Fallback to API call
            const response = await fetch('/csrf-token');
            if (response.ok) {
                const data = await response.json();
                this.csrfToken = data.csrf_token;
            }
        } catch (error) {
            console.warn('Failed to load CSRF token:', error);
        }
    }

    getHeaders(includeCSRF = true) {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (includeCSRF && this.csrfToken) {
            headers['X-CSRFToken'] = this.csrfToken;
        }
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(options.method !== 'GET'),
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);
            return response;
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    // System API endpoints
    async getSystemHealth() {
        return this.request('/api/system/health');
    }

    async getSystemMetrics() {
        return this.request('/api/system/metrics');
    }

    async getSystemStatus() {
        return this.request('/api/system/status');
    }

    // User API endpoints
    async getCurrentUser() {
        return this.request('/api/auth/current-user');
    }

    async getUserStats() {
        return this.request('/api/dashboard-data');
    }

    async getUserDashboardData() {
        return this.request('/api/dashboard-data');
    }

    async getUserProfile() {
        return this.request('/api/profile');
    }

    async updateUserProfile(profileData) {
        return this.request('/api/profile', {
            method: 'POST',
            body: JSON.stringify(profileData)
        });
    }

    async getUserSettings() {
        return this.request('/api/settings');
    }

    async updateUserSettings(settingsData) {
        return this.request('/api/settings', {
            method: 'POST',
            body: JSON.stringify(settingsData)
        });
    }

    // Lab Sessions API endpoints
    async getLabSessions(page = 1, perPage = 20) {
        return this.request(`/api/lab-sessions?page=${page}&per_page=${perPage}`);
    }

    async getLabSession(sessionId) {
        return this.request(`/api/lab-sessions/${sessionId}`);
    }

    async registerForSession(sessionId, notes = '') {
        return this.request(`/api/lab-sessions/${sessionId}/register`, {
            method: 'POST',
            body: JSON.stringify({ notes })
        });
    }

    async cancelRegistration(sessionId) {
        return this.request(`/api/lab-sessions/${sessionId}/cancel`, {
            method: 'POST'
        });
    }

    async checkInSession(sessionId, verificationCode) {
        return this.request(`/api/lab-sessions/${sessionId}/checkin`, {
            method: 'POST',
            body: JSON.stringify({ verification_code: verificationCode })
        });
    }

    async checkOutSession(entryId) {
        return this.request(`/api/lab-sessions/entry/${entryId}/checkout`, {
            method: 'POST'
        });
    }

    async getUserSessions(page = 1, perPage = 20) {
        return this.request(`/api/lab-sessions/my-sessions?page=${page}&per_page=${perPage}`);
    }

    // Admin API endpoints
    async getUsers(page = 1, perPage = 20) {
        return this.request(`/api/admin/users?page=${page}&per_page=${perPage}`);
    }

    async createUser(userData) {
        return this.request('/api/admin/users', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async updateUser(userId, userData) {
        return this.request(`/api/admin/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    async deleteUser(userId) {
        return this.request(`/api/admin/users/${userId}`, {
            method: 'DELETE'
        });
    }

    async promoteUser(userId, role) {
        return this.request('/api/admin/user-management', {
            method: 'POST',
            body: JSON.stringify({
                action: `promote_to_${role}`,
                user_id: userId
            })
        });
    }

    async demoteUser(userId) {
        return this.request('/api/admin/user-management', {
            method: 'POST',
            body: JSON.stringify({
                action: 'demote',
                user_id: userId
            })
        });
    }

    async getAdminStats() {
        return this.request('/api/admin/stats');
    }

    async getSystemSettings() {
        return this.request('/api/admin/settings');
    }

    async updateSystemSettings(settings) {
        return this.request('/api/admin/settings', {
            method: 'POST',
            body: JSON.stringify(settings)
        });
    }

    // Auth API endpoints
    async login(credentials) {
        return this.request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    }

    async logout() {
        return this.request('/api/auth/logout', {
            method: 'POST'
        });
    }

    async refreshToken() {
        return this.request('/api/auth/refresh', {
            method: 'POST'
        });
    }

    // Utility methods
    async uploadFile(endpoint, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        for (const [key, value] of Object.entries(additionalData)) {
            formData.append(key, value);
        }

        return this.request(endpoint, {
            method: 'POST',
            body: formData,
            headers: {
                // Don't set Content-Type for FormData, let browser set it
                ...(this.csrfToken && { 'X-CSRFToken': this.csrfToken })
            }
        });
    }

    // Error handling utilities
    async handleResponse(response) {
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    }

    // Batch operations
    async batchRequest(requests) {
        return Promise.allSettled(requests.map(req => this.request(req.endpoint, req.options)));
    }
}

// Create global instance
const labAPI = new LabAPI();

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LabAPI;
}
