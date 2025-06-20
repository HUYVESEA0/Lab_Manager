/**
 * Lab Sessions Admin Management JavaScript
 * Enhanced functionality for admin lab session management
 */

class LabSessionAdminManager {
    constructor() {
        this.selectedSessions = new Set();
        this.api = new LabManagerAPI();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupBulkOperations();
        this.setupQuickActions();
    }

    setupEventListeners() {
        // Refresh button
        document.getElementById('refresh-sessions')?.addEventListener('click', () => {
            this.refreshSessions();
        });

        // Export buttons
        document.getElementById('export-excel')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.exportData('excel');
        });

        document.getElementById('export-csv')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.exportData('csv');
        });

        document.getElementById('export-pdf')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.exportData('pdf');
        });

        // Quick create form
        document.getElementById('quick-create-form')?.addEventListener('submit', (e) => {
            this.handleQuickCreate(e);
        });

        // Bulk delete confirmation
        document.getElementById('confirm-bulk-delete')?.addEventListener('click', () => {
            this.confirmBulkDelete();
        });
    }

    setupBulkOperations() {
        // Select all toggle
        document.getElementById('select-all-sessions')?.addEventListener('click', () => {
            this.toggleSelectAll();
        });

        // Bulk action buttons
        document.getElementById('bulk-activate')?.addEventListener('click', () => {
            this.bulkActivate();
        });

        document.getElementById('bulk-deactivate')?.addEventListener('click', () => {
            this.bulkDeactivate();
        });

        document.getElementById('bulk-delete')?.addEventListener('click', () => {
            this.showBulkDeleteModal();
        });

        document.getElementById('bulk-export')?.addEventListener('click', () => {
            this.exportSelected();
        });
    }

    setupQuickActions() {
        // Duplicate session
        document.getElementById('duplicate-session')?.addEventListener('click', () => {
            this.duplicateSelected();
        });
    }

    // Session selection management
    toggleSessionSelection(sessionId, checkbox) {
        if (checkbox.checked) {
            this.selectedSessions.add(sessionId);
        } else {
            this.selectedSessions.delete(sessionId);
        }
        this.updateBulkActionsUI();
    }

    toggleSelectAll() {
        const checkboxes = document.querySelectorAll('.session-checkbox input[type="checkbox"]');
        const allSelected = Array.from(checkboxes).every(cb => cb.checked);
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = !allSelected;
            const sessionId = parseInt(checkbox.dataset.sessionId);
            if (checkbox.checked) {
                this.selectedSessions.add(sessionId);
            } else {
                this.selectedSessions.delete(sessionId);
            }
        });
        
        this.updateBulkActionsUI();
    }

    updateBulkActionsUI() {
        const count = this.selectedSessions.size;
        const bulkActions = document.getElementById('bulk-actions');
        const selectedCount = document.getElementById('selected-count');
        const bulkButtons = document.querySelectorAll('#bulk-actions button');
        const duplicateBtn = document.getElementById('duplicate-session');
        
        selectedCount.textContent = count;
        
        if (count > 0) {
            bulkActions.classList.add('show');
            bulkButtons.forEach(btn => btn.disabled = false);
            duplicateBtn.disabled = count !== 1; // Only allow duplicating one session
        } else {
            bulkActions.classList.remove('show');
            bulkButtons.forEach(btn => btn.disabled = true);
            duplicateBtn.disabled = true;
        }
    }

    // Enhanced session rendering
    renderEnhancedSessions(sessions) {
        const container = document.getElementById('admin-sessions-container');
        if (!container) return;

        if (sessions.length === 0) {
            container.innerHTML = this.getEmptyState();
            return;
        }

        const html = sessions.map(session => this.renderSessionCard(session)).join('');
        container.innerHTML = html;

        // Reattach event listeners for checkboxes
        document.querySelectorAll('.session-checkbox input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const sessionId = parseInt(e.target.dataset.sessionId);
                this.toggleSessionSelection(sessionId, e.target);
            });
        });
    }

    renderSessionCard(session) {
        const startDate = new Date(session.gio_bat_dau);
        const endDate = new Date(session.gio_ket_thuc);
        const now = new Date();
        
        // Determine session status
        let status = 'inactive';
        let statusText = 'Inactive';
        
        if (session.dang_hoat_dong) {
            if (startDate > now) {
                status = 'upcoming';
                statusText = 'Upcoming';
            } else if (startDate <= now && endDate >= now) {
                status = 'active';
                statusText = 'In Progress';
            } else {
                status = 'completed';
                statusText = 'Completed';
            }
        }

        // Calculate capacity percentage
        const capacityPercent = session.so_luong_toi_da > 0 ? 
            (session.so_dang_ky / session.so_luong_toi_da) * 100 : 0;

        return `
            <div class="session-card" data-session-id="${session.id}">
                <div class="card-body">
                    <div class="session-checkbox">
                        <input type="checkbox" class="form-check-input" data-session-id="${session.id}">
                    </div>
                    
                    <div class="session-header">
                        <h5 class="card-title mb-0">${this.escapeHtml(session.tieu_de)}</h5>
                        <span class="session-status ${status}">${statusText}</span>
                    </div>
                    
                    ${session.mo_ta ? `<p class="text-muted mb-3">${this.escapeHtml(session.mo_ta)}</p>` : ''}
                    
                    <div class="session-meta">
                        <div class="session-meta-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>${this.escapeHtml(session.dia_diem)}</span>
                        </div>
                        <div class="session-meta-item">
                            <i class="fas fa-calendar"></i>
                            <span>${this.formatDate(startDate)}</span>
                        </div>
                        <div class="session-meta-item">
                            <i class="fas fa-clock"></i>
                            <span>${this.formatTime(startDate)} - ${this.formatTime(endDate)}</span>
                        </div>
                        <div class="session-meta-item">
                            <i class="fas fa-user"></i>
                            <span>Created by: User ${session.nguoi_tao_ma}</span>
                        </div>
                    </div>
                    
                    <div class="progress-container">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="text-muted">Capacity</span>
                            <span class="text-muted">${session.so_dang_ky}/${session.so_luong_toi_da}</span>
                        </div>
                        <div class="capacity-progress">
                            <div class="progress-bar" style="width: ${Math.min(capacityPercent, 100)}%"></div>
                        </div>
                        <div class="capacity-text">
                            ${capacityPercent.toFixed(0)}% filled
                            ${capacityPercent >= 100 ? '(Full)' : `(${session.so_luong_toi_da - session.so_dang_ky} spots left)`}
                        </div>
                    </div>
                    
                    <div class="session-actions">
                        <a href="/lab/admin/edit/${session.id}" class="btn btn-outline-primary btn-action">
                            <i class="fas fa-edit"></i> Edit
                        </a>
                        <a href="/lab/admin/attendees/${session.id}" class="btn btn-outline-info btn-action">
                            <i class="fas fa-users"></i> Attendees (${session.so_dang_ky})
                        </a>
                        <button class="btn btn-outline-secondary btn-action" onclick="labSessionAdminManager.showSessionDetails(${session.id})">
                            <i class="fas fa-info-circle"></i> Details
                        </button>
                        <button class="btn btn-outline-warning btn-action" onclick="labSessionAdminManager.duplicateSession(${session.id})">
                            <i class="fas fa-copy"></i> Duplicate
                        </button>
                        <button class="btn btn-outline-danger btn-action" onclick="labSessionAdminManager.deleteSession(${session.id})">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    getEmptyState() {
        return `
            <div class="empty-state">
                <i class="fas fa-flask"></i>
                <h4>No Lab Sessions Found</h4>
                <p>No lab sessions match your current filters.</p>
                <a href="{{ url_for('lab.create_lab_session') }}" class="btn btn-success">
                    <i class="fas fa-plus"></i> Create Your First Session
                </a>
            </div>
        `;
    }

    // Bulk operations
    async bulkActivate() {
        if (this.selectedSessions.size === 0) return;
        
        try {
            const response = await this.api.post('/lab-sessions/bulk-action', {
                action: 'activate',
                session_ids: Array.from(this.selectedSessions)
            });
            
            if (response.ok) {
                this.showSuccess(`Successfully activated ${this.selectedSessions.size} sessions`);
                this.refreshSessions();
                this.clearSelection();
            } else {
                const data = await response.json();
                this.showError(data.error || 'Failed to activate sessions');
            }
        } catch (error) {
            this.showError('Network error during bulk activation');
        }
    }

    async bulkDeactivate() {
        if (this.selectedSessions.size === 0) return;
        
        try {
            const response = await this.api.post('/lab-sessions/bulk-action', {
                action: 'deactivate',
                session_ids: Array.from(this.selectedSessions)
            });
            
            if (response.ok) {
                this.showSuccess(`Successfully deactivated ${this.selectedSessions.size} sessions`);
                this.refreshSessions();
                this.clearSelection();
            } else {
                const data = await response.json();
                this.showError(data.error || 'Failed to deactivate sessions');
            }
        } catch (error) {
            this.showError('Network error during bulk deactivation');
        }
    }

    showBulkDeleteModal() {
        if (this.selectedSessions.size === 0) return;
        
        document.getElementById('delete-count').textContent = this.selectedSessions.size;
        $('#bulkDeleteModal').modal('show');
    }

    async confirmBulkDelete() {
        try {
            const response = await this.api.post('/lab-sessions/bulk-action', {
                action: 'delete',
                session_ids: Array.from(this.selectedSessions)
            });
            
            if (response.ok) {
                this.showSuccess(`Successfully deleted ${this.selectedSessions.size} sessions`);
                this.refreshSessions();
                this.clearSelection();
                $('#bulkDeleteModal').modal('hide');
            } else {
                const data = await response.json();
                this.showError(data.error || 'Failed to delete sessions');
            }
        } catch (error) {
            this.showError('Network error during bulk deletion');
        }
    }

    // Quick create session
    async handleQuickCreate(event) {
        event.preventDefault();
        
        const formData = {
            tieu_de: document.getElementById('quick-title').value,
            mo_ta: document.getElementById('quick-description').value,
            date: document.getElementById('quick-date').value,
            start_time: document.getElementById('quick-start-time').value,
            end_time: document.getElementById('quick-end-time').value,
            dia_diem: document.getElementById('quick-location').value,
            so_luong_toi_da: parseInt(document.getElementById('quick-max-students').value)
        };

        try {
            const response = await this.api.post('/lab-sessions/admin', formData);
            
            if (response.ok) {
                const data = await response.json();
                this.showSuccess('Session created successfully!');
                $('#quickCreateModal').modal('hide');
                document.getElementById('quick-create-form').reset();
                this.refreshSessions();
            } else {
                const data = await response.json();
                this.showError(data.error || 'Failed to create session');
            }
        } catch (error) {
            this.showError('Network error during session creation');
        }
    }    // Export functionality - using server-side export
    async exportData(format) {
        try {
            // Use server-side export route instead of API
            const exportUrl = `/admin/lab-sessions/export?format=${format}`;
            window.open(exportUrl, '_blank');
            this.showSuccess(`Sessions exported as ${format.toUpperCase()}`);
        } catch (error) {
            this.showError('Network error during export');
        }
    }    async exportSelected() {
        if (this.selectedSessions.size === 0) return;
        
        try {
            // Use server-side export with selected session IDs
            const sessionIds = Array.from(this.selectedSessions).join(',');
            const exportUrl = `/admin/lab-sessions/export?format=excel&session_ids=${sessionIds}`;
            window.open(exportUrl, '_blank');
            this.showSuccess('Selected sessions exported');
        } catch (error) {
            this.showError('Network error during export');
        }
    }

    // Session management
    async duplicateSession(sessionId) {
        try {
            const response = await this.api.post(`/lab-sessions/${sessionId}/duplicate`);
            
            if (response.ok) {
                const data = await response.json();
                this.showSuccess('Session duplicated successfully!');
                this.refreshSessions();
            } else {
                const data = await response.json();
                this.showError(data.error || 'Failed to duplicate session');
            }
        } catch (error) {
            this.showError('Network error during duplication');
        }
    }

    async duplicateSelected() {
        if (this.selectedSessions.size !== 1) return;
        
        const sessionId = Array.from(this.selectedSessions)[0];
        await this.duplicateSession(sessionId);
    }

    async deleteSession(sessionId) {
        if (!confirm('Are you sure you want to delete this session?')) return;
        
        try {
            const response = await this.api.delete(`/lab-sessions/${sessionId}`);
            
            if (response.ok) {
                this.showSuccess('Session deleted successfully!');
                this.refreshSessions();
            } else {
                const data = await response.json();
                this.showError(data.error || 'Failed to delete session');
            }
        } catch (error) {
            this.showError('Network error during deletion');
        }
    }

    async showSessionDetails(sessionId) {
        try {
            const response = await this.api.get(`/lab-sessions/${sessionId}`);
            
            if (response.ok) {
                const session = await response.json();
                this.renderSessionDetails(session);
                $('#sessionDetailsModal').modal('show');
            } else {
                this.showError('Failed to load session details');
            }
        } catch (error) {
            this.showError('Network error while loading details');
        }
    }

    renderSessionDetails(session) {
        const startDate = new Date(session.gio_bat_dau);
        const endDate = new Date(session.gio_ket_thuc);
        
        const content = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Basic Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>Title:</strong></td>
                            <td>${this.escapeHtml(session.tieu_de)}</td>
                        </tr>
                        <tr>
                            <td><strong>Location:</strong></td>
                            <td>${this.escapeHtml(session.dia_diem)}</td>
                        </tr>
                        <tr>
                            <td><strong>Date:</strong></td>
                            <td>${this.formatDate(startDate)}</td>
                        </tr>
                        <tr>
                            <td><strong>Time:</strong></td>
                            <td>${this.formatTime(startDate)} - ${this.formatTime(endDate)}</td>
                        </tr>
                        <tr>
                            <td><strong>Max Students:</strong></td>
                            <td>${session.so_luong_toi_da}</td>
                        </tr>
                        <tr>
                            <td><strong>Status:</strong></td>
                            <td>${session.dang_hoat_dong ? 'Active' : 'Inactive'}</td>
                        </tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Registration Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>Registered:</strong></td>
                            <td>${session.dang_ky ? session.dang_ky.length : 0}</td>
                        </tr>
                        <tr>
                            <td><strong>Capacity:</strong></td>
                            <td>${session.so_luong_toi_da}</td>
                        </tr>
                        <tr>
                            <td><strong>Available Spots:</strong></td>
                            <td>${session.so_luong_toi_da - (session.dang_ky ? session.dang_ky.length : 0)}</td>
                        </tr>
                        <tr>
                            <td><strong>Created:</strong></td>
                            <td>${session.ngay_tao ? this.formatDateTime(new Date(session.ngay_tao)) : 'N/A'}</td>
                        </tr>
                    </table>
                </div>
            </div>
            ${session.mo_ta ? `
                <div class="mt-3">
                    <h6>Description</h6>
                    <p>${this.escapeHtml(session.mo_ta)}</p>
                </div>
            ` : ''}
        `;
        
        document.getElementById('session-details-content').innerHTML = content;
        document.getElementById('edit-session-link').href = `/lab/admin/edit/${session.id}`;
    }

    // Utility methods
    clearSelection() {
        this.selectedSessions.clear();
        document.querySelectorAll('.session-checkbox input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        this.updateBulkActionsUI();
    }    refreshSessions() {
        // Refresh using server-side reload instead of API
        window.location.reload();
        this.clearSelection();
    }

    formatDate(date) {
        return date.toLocaleDateString('en-US', {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatDateTime(date) {
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showSuccess(message) {
        // You can implement a toast notification system here
        console.log('Success:', message);
        // For now, use a simple alert
        alert('Success: ' + message);
    }

    showError(message) {
        // You can implement a toast notification system here
        console.error('Error:', message);
        // For now, use a simple alert
        alert('Error: ' + message);
    }
}

// Override the original renderAdminLabSessions method to use enhanced rendering
if (typeof LabSessionManager !== 'undefined') {
    LabSessionManager.prototype.renderAdminLabSessions = function(sessions) {
        if (window.labSessionAdminManager) {
            window.labSessionAdminManager.renderEnhancedSessions(sessions);
        }
    };
}
