/**
 * Lab Sessions Management JavaScript
 * Handles API interactions for lab session operations
 */

class LabSessionManager {
    constructor() {
        this.api = new LabManagerAPI();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDataOnPageLoad();
    }

    setupEventListeners() {
        // Registration form
        const registerForm = document.getElementById('register-session-form');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegistration(e));
        }

        // Verification form
        const verifyForm = document.getElementById('verify-session-form');
        if (verifyForm) {
            verifyForm.addEventListener('submit', (e) => this.handleVerification(e));
        }

        // Result submission form
        const resultForm = document.getElementById('lab-result-form');
        if (resultForm) {
            resultForm.addEventListener('submit', (e) => this.handleResultSubmission(e));
        }

        // Refresh buttons
        document.querySelectorAll('.refresh-sessions').forEach(btn => {
            btn.addEventListener('click', () => this.refreshSessions());
        });
    }

    loadDataOnPageLoad() {
        const currentPage = document.body.dataset.page;
        
        switch(currentPage) {
            case 'lab-sessions':
                this.loadAvailableSessions();
                break;
            case 'my-sessions':
                this.loadMySessions();
                break;
            case 'admin-lab-sessions':                // API calls removed - using server-side data
                console.log('✅ Admin lab sessions loaded from server-side');
                break;
            case 'session-attendees':
                this.loadSessionAttendees();
                break;
        }
    }

    async loadAvailableSessions() {
        try {
            const response = await this.api.get('/lab-sessions?available_only=true');
            const data = await response.json();
            
            if (response.ok) {
                this.renderAvailableSessions(data.sessions);
            } else {
                console.error('Failed to load sessions:', data.error);
                this.showError('Failed to load available sessions');
            }
        } catch (error) {
            console.error('Error loading sessions:', error);
            this.showError('Network error while loading sessions');
        }
    }

    async loadMySessions() {
        try {
            const response = await this.api.get('/lab-sessions/my-sessions');
            const data = await response.json();
            
            if (response.ok) {
                this.renderMySessions(data.registered_sessions, data.lab_history);
            } else {
                console.error('Failed to load my sessions:', data.error);
                this.showError('Failed to load your sessions');
            }
        } catch (error) {
            console.error('Error loading my sessions:', error);
            this.showError('Network error while loading your sessions');
        }    }    
      
    // API functions removed - now using server-side data only
    // All lab session loading is handled by backend routes

    async loadSessionAttendees() {
        const sessionId = document.body.dataset.sessionId;
        if (!sessionId) return;

        try {
            const response = await this.api.get(`/lab-sessions/${sessionId}/attendees`);
            const data = await response.json();
            
            if (response.ok) {
                this.renderSessionAttendees(data.registrations, data.entries);
            } else {
                console.error('Failed to load attendees:', data.error);
                this.showError('Failed to load session attendees');
            }
        } catch (error) {
            console.error('Error loading attendees:', error);
            this.showError('Network error while loading attendees');
        }
    }

    async handleRegistration(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const sessionId = formData.get('session_id');
        const notes = formData.get('notes');

        try {
            const response = await this.api.post('/lab-sessions/register', {
                session_id: parseInt(sessionId),
                notes: notes
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showSuccess('Registration successful!');
                // Redirect or refresh page
                setTimeout(() => {
                    window.location.href = '/lab/sessions';
                }, 1500);
            } else {
                this.showError(data.error || 'Registration failed');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showError('Network error during registration');
        }
    }

    async handleVerification(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const sessionId = document.body.dataset.sessionId;
        const verificationCode = formData.get('verification_code');

        try {
            const response = await this.api.post(`/lab-sessions/${sessionId}/verify`, {
                verification_code: verificationCode
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showSuccess('Verification successful!');
                // Redirect to active session
                setTimeout(() => {
                    window.location.href = `/lab/active/${data.entry_id}`;
                }, 1500);
            } else {
                this.showError(data.error || 'Verification failed');
            }
        } catch (error) {
            console.error('Verification error:', error);
            this.showError('Network error during verification');
        }
    }

    async handleResultSubmission(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const entryId = document.body.dataset.entryId;
        const labResult = formData.get('lab_result');

        try {
            const response = await this.api.post(`/lab-sessions/entries/${entryId}/submit`, {
                lab_result: labResult
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showSuccess('Lab result submitted successfully!');
                // Redirect to my sessions
                setTimeout(() => {
                    window.location.href = '/lab/my-sessions';
                }, 1500);
            } else {
                this.showError(data.error || 'Submission failed');
            }
        } catch (error) {
            console.error('Submission error:', error);
            this.showError('Network error during submission');
        }
    }

    renderAvailableSessions(sessions) {
        const container = document.getElementById('available-sessions-container');
        if (!container) return;

        if (sessions.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No available sessions at the moment.</div>';
            return;
        }

        const html = sessions.map(session => `
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">${this.escapeHtml(session.tieu_de)}</h5>
                    <p class="card-text">${this.escapeHtml(session.mo_ta || '')}</p>
                    <div class="row">
                        <div class="col-md-6">
                            <strong>Location:</strong> ${this.escapeHtml(session.dia_diem)}<br>
                            <strong>Time:</strong> ${this.formatDateTime(session.gio_bat_dau)} - ${this.formatTime(session.gio_ket_thuc)}
                        </div>
                        <div class="col-md-6">
                            <strong>Capacity:</strong> ${session.so_dang_ky}/${session.so_luong_toi_da}<br>
                            <strong>Status:</strong> 
                            <span class="badge badge-${session.co_the_dang_ky ? 'success' : 'secondary'}">
                                ${session.co_the_dang_ky ? 'Available' : 'Full'}
                            </span>
                        </div>
                    </div>
                    ${session.co_the_dang_ky ? 
                        `<a href="/lab/register/${session.id}" class="btn btn-primary mt-2">Register</a>` :
                        `<button class="btn btn-secondary mt-2" disabled>Full</button>`
                    }
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }    renderMySessions(registeredSessions, labHistory) {
        // Render registered sessions
        const registeredContainer = document.getElementById('registered-sessions-container');
        if (registeredContainer) {
            if (registeredSessions.length === 0) {
                registeredContainer.innerHTML = '<div class="alert alert-info">You have no registered sessions.</div>';
            } else {
                const html = registeredSessions.map(session => `
                    <div class="card mb-3">
                        <div class="card-body">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <h5 class="card-title">${this.escapeHtml(session.tieu_de)}</h5>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <strong>Location:</strong> ${this.escapeHtml(session.dia_diem)}<br>
                                            <strong>Time:</strong> ${this.formatDateTime(session.gio_bat_dau)} - ${this.formatTime(session.gio_ket_thuc)}
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Status:</strong> 
                                            ${session.dang_dien_ra ? 
                                                '<span class="badge badge-success">In Progress</span>' :
                                                session.co_the_dang_ky ? 
                                                    '<span class="badge badge-info">Upcoming</span>' :
                                                    '<span class="badge badge-secondary">Ended</span>'
                                            }
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4 text-right">
                                    ${session.dang_dien_ra ? 
                                        `<a href="/lab/verify/${session.id}" class="btn btn-success">Join Session</a>` :
                                        session.co_the_dang_ky ? 
                                            `<span class="badge badge-warning">Upcoming</span>` :
                                            `<span class="badge badge-secondary">Ended</span>`
                                    }
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
                registeredContainer.innerHTML = html;
            }
        }

        // Render lab history in table format
        const historyContainer = document.getElementById('lab-history-container');
        if (historyContainer) {
            if (labHistory.length === 0) {
                historyContainer.innerHTML = `
                    <tr>
                        <td colspan="${window.current_user && window.current_user.is_admin_manager ? '6' : '5'}" class="text-center">
                            <div class="alert alert-info mb-0">No lab history available.</div>
                        </td>
                    </tr>
                `;
            } else {
                const html = labHistory.map(entry => `
                    <tr>
                        <td>
                            <strong>${this.escapeHtml(entry.tieu_de)}</strong><br>
                            <small class="text-muted">${this.escapeHtml(entry.dia_diem)}</small>
                        </td>
                        <td>${this.escapeHtml(entry.dia_diem)}</td>
                        <td>${this.formatDateTime(entry.thoi_gian_vao)}</td>
                        <td>
                            ${entry.thoi_gian_ra ? 
                                this.formatDateTime(entry.thoi_gian_ra) : 
                                '<span class="text-warning">In Progress</span>'
                            }
                        </td>
                        <td>
                            ${entry.ket_qua ? 
                                `<button class="btn btn-sm btn-outline-primary" onclick="labSessionManager.showResultModal('${this.escapeHtml(entry.ket_qua)}', '${this.escapeHtml(entry.tieu_de)}')">
                                    <i class="fas fa-file-alt"></i> View
                                </button>` :
                                '<span class="text-muted">Not submitted</span>'
                            }
                        </td>
                        ${window.current_user && window.current_user.is_admin_manager ? 
                            `<td>
                                <a href="/lab/admin/attendees/${entry.ca_thuc_hanh_ma}" class="btn btn-sm btn-info">
                                    <i class="fas fa-users"></i> Attendees
                                </a>
                            </td>` : ''
                        }
                    </tr>
                `).join('');
                historyContainer.innerHTML = html;
            }
        }
    }

    renderAdminLabSessions(sessions) {
        const container = document.getElementById('admin-sessions-container');
        if (!container) return;

        if (sessions.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No lab sessions found.</div>';
            return;
        }

        const html = sessions.map(session => `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <h5 class="card-title">${this.escapeHtml(session.tieu_de)}</h5>
                            <p class="card-text">${this.escapeHtml(session.mo_ta || '')}</p>
                            <div class="row">
                                <div class="col-md-6">
                                    <strong>Location:</strong> ${this.escapeHtml(session.dia_diem)}<br>
                                    <strong>Time:</strong> ${this.formatDateTime(session.gio_bat_dau)} - ${this.formatTime(session.gio_ket_thuc)}
                                </div>
                                <div class="col-md-6">
                                    <strong>Registrations:</strong> ${session.so_dang_ky}/${session.so_luong_toi_da}<br>
                                    <strong>Status:</strong> 
                                    <span class="badge badge-${session.dang_hoat_dong ? 'success' : 'secondary'}">
                                        ${session.dang_hoat_dong ? 'Active' : 'Inactive'}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 text-right">
                            <div class="btn-group-vertical" role="group">
                                <a href="/lab/admin/edit/${session.id}" class="btn btn-sm btn-outline-primary">Edit</a>
                                <a href="/lab/admin/attendees/${session.id}" class="btn btn-sm btn-outline-info">Attendees</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    renderSessionAttendees(registrations, entries) {
        // Render registrations
        const regContainer = document.getElementById('registrations-container');
        if (regContainer) {
            if (registrations.length === 0) {
                regContainer.innerHTML = '<div class="alert alert-info">No registrations found.</div>';
            } else {
                const html = registrations.map(reg => `
                    <tr>
                        <td>${this.escapeHtml(reg.user.ten_nguoi_dung)}</td>
                        <td>${this.escapeHtml(reg.user.email)}</td>
                        <td>${this.escapeHtml(reg.ghi_chu || '')}</td>
                        <td>
                            <span class="badge badge-${reg.trang_thai_tham_gia === 'da_tham_gia' ? 'success' : 'warning'}">
                                ${reg.trang_thai_tham_gia === 'da_tham_gia' ? 'Attended' : 'Registered'}
                            </span>
                        </td>
                    </tr>
                `).join('');
                regContainer.innerHTML = html;
            }
        }

        // Render actual entries
        const entriesContainer = document.getElementById('entries-container');
        if (entriesContainer) {
            if (entries.length === 0) {
                entriesContainer.innerHTML = '<div class="alert alert-info">No attendance entries found.</div>';
            } else {
                const html = entries.map(entry => `
                    <tr>
                        <td>${this.escapeHtml(entry.user.ten_nguoi_dung)}</td>
                        <td>${this.escapeHtml(entry.user.email)}</td>
                        <td>${this.formatDateTime(entry.thoi_gian_vao)}</td>
                        <td>${entry.thoi_gian_ra ? this.formatDateTime(entry.thoi_gian_ra) : 'In Progress'}</td>
                        <td>${this.escapeHtml(entry.ket_qua || 'Not submitted')}</td>
                    </tr>
                `).join('');
                entriesContainer.innerHTML = html;
            }
        }
    }

    renderPagination(pagination) {
        const paginationContainer = document.getElementById('sessions-pagination');
        const paginationList = document.getElementById('pagination-list');
        
        if (!paginationContainer || !paginationList || !pagination) return;
        
        if (pagination.pages <= 1) {
            paginationContainer.style.display = 'none';
            return;
        }
        
        paginationContainer.style.display = 'block';
        let html = '';
        
        // Previous button
        if (pagination.has_prev) {
            html += `<li class="page-item">
                <a class="page-link" href="#" data-page="${pagination.page - 1}">Previous</a>
            </li>`;
        } else {
            html += `<li class="page-item disabled">
                <span class="page-link">Previous</span>
            </li>`;
        }
        
        // Page numbers
        const startPage = Math.max(1, pagination.page - 2);
        const endPage = Math.min(pagination.pages, pagination.page + 2);
        
        if (startPage > 1) {
            html += `<li class="page-item">
                <a class="page-link" href="#" data-page="1">1</a>
            </li>`;
            if (startPage > 2) {
                html += `<li class="page-item disabled">
                    <span class="page-link">...</span>
                </li>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `<li class="page-item ${i === pagination.page ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>`;
        }
        
        if (endPage < pagination.pages) {
            if (endPage < pagination.pages - 1) {
                html += `<li class="page-item disabled">
                    <span class="page-link">...</span>
                </li>`;
            }
            html += `<li class="page-item">
                <a class="page-link" href="#" data-page="${pagination.pages}">${pagination.pages}</a>
            </li>`;
        }
        
        // Next button
        if (pagination.has_next) {
            html += `<li class="page-item">
                <a class="page-link" href="#" data-page="${pagination.page + 1}">Next</a>
            </li>`;
        } else {
            html += `<li class="page-item disabled">
                <span class="page-link">Next</span>
            </li>`;
        }
        
        paginationList.innerHTML = html;
        
        // Add click handlers
        paginationList.querySelectorAll('a[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(link.dataset.page);                // Using server-side pagination
                const currentUrl = new URL(window.location);
                currentUrl.searchParams.set('page', page);
                window.location.href = currentUrl.toString();
            });
        });
    }

    refreshSessions() {
        this.loadDataOnPageLoad();
        this.showSuccess('Sessions refreshed');
    }

    formatDateTime(isoString) {
        const date = new Date(isoString);
        return date.toLocaleString();
    }

    formatTime(isoString) {
        const date = new Date(isoString);
        return date.toLocaleTimeString();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showError(message) {
        this.showMessage(message, 'danger');
    }

    showMessage(message, type) {
        // Try to use existing flash message system
        if (typeof showFlashMessage === 'function') {
            showFlashMessage(message, type);
        } else {
            // Fallback to console
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    showResultModal(result, sessionTitle) {
        const modal = document.getElementById('resultModal');
        const titleElement = document.getElementById('resultModalLabel');
        const contentElement = document.getElementById('resultModalContent');
        
        if (modal && titleElement && contentElement) {
            titleElement.textContent = `Lab Result: ${sessionTitle}`;
            contentElement.textContent = result;
            $(modal).modal('show'); // Using jQuery for Bootstrap modal
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (typeof LabManagerAPI !== 'undefined') {
        window.labSessionManager = new LabSessionManager();
    } else {
        console.error('LabManagerAPI not available');
    }
});
