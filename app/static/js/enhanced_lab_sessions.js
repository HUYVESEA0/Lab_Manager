/**
 * Enhanced Lab Sessions Management JavaScript
 * Advanced features for the enhanced lab sessions interface
 */

class EnhancedLabSessionManager {
    constructor() {
        this.baseApiUrl = '/api/v1';
        this.currentFilters = {};
        this.selectedSessions = new Set();
        this.currentPage = 1;
        this.realTimeEnabled = true;
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeDataLoading();
        this.setupRealTimeUpdates();
        this.setupKeyboardShortcuts();
    }

    setupEventListeners() {
        // Search with debouncing
        this.setupSearchHandler();
        
        // Filter handlers
        this.setupFilterHandlers();
        
        // Action button handlers
        this.setupActionHandlers();
        
        // Bulk action handlers
        this.setupBulkActionHandlers();
        
        // Export handlers
        this.setupExportHandlers();
        
        // Modal handlers
        this.setupModalHandlers();
        
        // Session card handlers
        this.setupSessionCardHandlers();
    }

    setupSearchHandler() {
        const searchInput = document.getElementById('search-sessions');
        let searchTimeout;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.currentFilters.search = e.target.value.trim();
                this.currentPage = 1;
                this.loadSessions();
            }, 300);
        });

        // Advanced search features
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                e.target.value = '';
                delete this.currentFilters.search;
                this.loadSessions();
            }
        });
    }

    setupFilterHandlers() {
        const filterToggle = document.getElementById('filter-toggle');
        const advancedFilters = document.getElementById('advanced-filters');

        filterToggle.addEventListener('click', () => {
            const isVisible = advancedFilters.style.display !== 'none';
            advancedFilters.style.display = isVisible ? 'none' : 'block';
            
            const chevron = filterToggle.querySelector('.fa-chevron-down');
            chevron.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
            
            // Animate the transition
            if (!isVisible) {
                advancedFilters.style.maxHeight = '0px';
                advancedFilters.style.overflow = 'hidden';
                setTimeout(() => {
                    advancedFilters.style.maxHeight = '500px';
                    advancedFilters.style.transition = 'max-height 0.3s ease-out';
                }, 10);
            }
        });

        // Filter input handlers
        const filterInputs = [
            'status-filter', 'difficulty-filter', 'date-filter', 
            'room-filter', 'tags-filter', 'sort-by', 'sort-order'
        ];

        filterInputs.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', () => {
                    this.updateFilters();
                });
            }
        });
    }

    setupActionHandlers() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-sessions');
        refreshBtn.addEventListener('click', () => {
            this.refreshSessions();
        });

        // Export button
        const exportBtn = document.getElementById('export-sessions');
        exportBtn.addEventListener('click', () => {
            this.showExportModal();
        });
    }

    setupBulkActionHandlers() {
        const bulkActions = ['bulk-activate', 'bulk-deactivate', 'bulk-duplicate', 'bulk-delete'];
        
        bulkActions.forEach(actionId => {
            const button = document.getElementById(actionId);
            if (button) {
                button.addEventListener('click', () => {
                    const action = actionId.replace('bulk-', '');
                    this.performBulkAction(action);
                });
            }
        });
    }

    setupExportHandlers() {
        const confirmExportBtn = document.getElementById('confirm-export');
        if (confirmExportBtn) {
            confirmExportBtn.addEventListener('click', () => {
                this.performExport();
            });
        }
    }

    setupModalHandlers() {
        // Close modals on background click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-enhanced')) {
                this.closeModal(e.target.id);
            }
        });

        // Close modals on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModals = document.querySelectorAll('.modal-enhanced.show');
                openModals.forEach(modal => {
                    this.closeModal(modal.id);
                });
            }
        });
    }

    setupSessionCardHandlers() {
        // Event delegation for dynamically created session cards
        document.addEventListener('click', (e) => {
            // Handle session selection checkboxes
            if (e.target.type === 'checkbox' && e.target.closest('.session-checkbox')) {
                const sessionId = parseInt(e.target.closest('.session-card').dataset.sessionId);
                this.toggleSessionSelection(sessionId, e.target.checked);
            }

            // Handle session card clicks (for selection)
            if (e.target.closest('.session-card') && !e.target.closest('.session-actions') && !e.target.closest('.session-checkbox')) {
                const sessionCard = e.target.closest('.session-card');
                const checkbox = sessionCard.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    const sessionId = parseInt(sessionCard.dataset.sessionId);
                    this.toggleSessionSelection(sessionId, checkbox.checked);
                }
            }
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + R: Refresh
            if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
                e.preventDefault();
                this.refreshSessions();
            }

            // Ctrl/Cmd + A: Select all visible sessions
            if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
                e.preventDefault();
                this.selectAllVisibleSessions();
            }

            // Delete key: Delete selected sessions
            if (e.key === 'Delete' && this.selectedSessions.size > 0) {
                e.preventDefault();
                this.performBulkAction('delete');
            }

            // Ctrl/Cmd + D: Duplicate selected sessions
            if ((e.ctrlKey || e.metaKey) && e.key === 'd' && this.selectedSessions.size > 0) {
                e.preventDefault();
                this.performBulkAction('duplicate');
            }
        });
    }

    async initializeDataLoading() {
        try {
            await Promise.all([
                this.loadSessions(),
                this.loadStatistics(),
                this.loadTemplates()
            ]);
        } catch (error) {
            console.error('Error initializing data:', error);
            this.showNotification('Failed to load initial data', 'error');
        }
    }

    setupRealTimeUpdates() {
        if (this.realTimeEnabled) {
            // Refresh statistics every 30 seconds
            this.refreshInterval = setInterval(() => {
                this.loadStatistics();
            }, 30000);

            // Refresh sessions every 2 minutes
            setInterval(() => {
                this.loadSessions(true); // Silent refresh
            }, 120000);
        }
    }

    async loadSessions(silent = false) {
        if (!silent) {
            this.showLoadingState();
        }

        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: 12,
                ...this.currentFilters
            });

            const response = await fetch(`${this.baseApiUrl}/lab-sessions/enhanced?${params}`);
            const data = await response.json();

            if (response.ok) {
                this.renderSessions(data.sessions, !silent);
                this.renderPagination(data.pagination);
                
                if (!silent) {
                    this.hideLoadingState();
                }
            } else {
                throw new Error(data.error || 'Failed to load sessions');
            }
        } catch (error) {
            console.error('Error loading sessions:', error);
            if (!silent) {
                this.showNotification('Failed to load sessions', 'error');
                this.hideLoadingState();
            }
        }
    }

    async loadStatistics() {
        try {
            const response = await fetch(`${this.baseApiUrl}/lab-sessions/analytics`);
            const data = await response.json();

            if (response.ok) {
                this.updateStatistics(data.overview);
                this.updateTrends(data);
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    async loadTemplates() {
        try {
            const response = await fetch(`${this.baseApiUrl}/lab-sessions/templates`);
            const data = await response.json();

            if (response.ok) {
                this.renderTemplates(data.templates);
            }
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    }

    updateStatistics(stats) {
        // Update basic statistics
        this.animateNumberUpdate('total-sessions', stats.total_sessions || 0);
        this.animateNumberUpdate('active-sessions', stats.active_sessions || 0);
        this.animateNumberUpdate('today-sessions', stats.today_sessions || 0);
        this.animateNumberUpdate('total-attendees', stats.total_attendees || 0);
    }

    updateTrends(data) {
        // Update trend indicators
        const trendElements = document.querySelectorAll('.stat-trend');
        trendElements.forEach((element, index) => {
            // Simulate trend calculation
            const isUp = Math.random() > 0.5;
            const percentage = Math.floor(Math.random() * 20) + 1;
            
            element.className = `stat-trend ${isUp ? 'up' : 'down'}`;
            element.innerHTML = `<i class="fas fa-arrow-${isUp ? 'up' : 'down'}"></i> ${isUp ? '+' : '-'}${percentage}%`;
        });
    }

    animateNumberUpdate(elementId, newValue) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const currentValue = parseInt(element.textContent) || 0;
        const duration = 1000; // 1 second
        const steps = 30;
        const stepValue = (newValue - currentValue) / steps;
        const stepDuration = duration / steps;

        let currentStep = 0;
        const timer = setInterval(() => {
            currentStep++;
            const value = Math.round(currentValue + (stepValue * currentStep));
            element.textContent = value;

            if (currentStep >= steps) {
                clearInterval(timer);
                element.textContent = newValue;
            }
        }, stepDuration);
    }

    renderSessions(sessions, animate = true) {
        const grid = document.getElementById('sessions-grid');
        
        if (sessions.length === 0) {
            grid.innerHTML = this.getEmptyStateHTML();
            return;
        }

        const html = sessions.map((session, index) => 
            this.createSessionCard(session, animate ? index * 100 : 0)
        ).join('');
        
        grid.innerHTML = html;

        // Apply animations if requested
        if (animate) {
            const cards = grid.querySelectorAll('.session-card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        }
    }

    createSessionCard(session, animationDelay = 0) {
        const statusClass = this.getStatusClass(session.trang_thai);
        const completionPercentage = Math.min((session.so_dang_ky / session.so_luong_toi_da) * 100, 100);
        const tags = session.tags || [];
        const isSelected = this.selectedSessions.has(session.id);
        const difficultyColor = this.getDifficultyColor(session.muc_do_kho);

        return `
            <div class="session-card" data-session-id="${session.id}" style="animation-delay: ${animationDelay}ms">
                <div class="session-header" style="background: ${this.getSessionHeaderGradient(session)}">
                    <div class="session-status ${statusClass}">
                        ${this.getStatusLabel(session.trang_thai)}
                    </div>
                    <div class="session-title">${this.escapeHtml(session.tieu_de)}</div>
                    <div class="session-rating" style="position: absolute; bottom: 10px; right: 10px; color: rgba(255,255,255,0.9);">
                        ${session.avg_rating ? `⭐ ${session.avg_rating.toFixed(1)}` : ''}
                    </div>
                </div>
                <div class="session-body">
                    <div class="session-meta">
                        <div class="meta-item">
                            <i class="fas fa-calendar meta-icon"></i>
                            <span>${this.formatDate(session.gio_bat_dau)}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-clock meta-icon"></i>
                            <span>${this.formatTime(session.gio_bat_dau)} - ${this.formatTime(session.gio_ket_thuc)}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-map-marker-alt meta-icon"></i>
                            <span>${this.escapeHtml(session.dia_diem)}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-signal meta-icon" style="color: ${difficultyColor}"></i>
                            <span style="color: ${difficultyColor}">${this.getDifficultyLabel(session.muc_do_kho)}</span>
                        </div>
                    </div>
                    
                    <div class="session-description">
                        ${this.escapeHtml(session.mo_ta || 'No description available')}
                    </div>
                    
                    ${tags.length > 0 ? `
                        <div class="session-tags">
                            ${tags.map(tag => `<span class="tag">${this.escapeHtml(tag)}</span>`).join('')}
                        </div>
                    ` : ''}
                    
                    <div class="session-progress">
                        <div class="progress-label">
                            <span>Registrations</span>
                            <span>${session.so_dang_ky}/${session.so_luong_toi_da}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${completionPercentage}%"></div>
                        </div>
                    </div>

                    ${session.completion_rate !== undefined ? `
                        <div class="session-metrics">
                            <div class="metric">
                                <i class="fas fa-chart-line"></i>
                                <span>Completion: ${session.completion_rate.toFixed(1)}%</span>
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="session-actions">
                        <button class="btn-enhanced btn-outline-primary btn-sm" onclick="window.enhancedLabManager.viewSessionDetails(${session.id})">
                            <i class="fas fa-eye"></i>
                            View
                        </button>
                        <a href="/lab/admin/edit/${session.id}" class="btn-enhanced btn-outline-success btn-sm">
                            <i class="fas fa-edit"></i>
                            Edit
                        </a>
                        <button class="btn-enhanced btn-outline-danger btn-sm" onclick="window.enhancedLabManager.deleteSession(${session.id})">
                            <i class="fas fa-trash"></i>
                            Delete
                        </button>
                        <label class="session-checkbox">
                            <input type="checkbox" ${isSelected ? 'checked' : ''}>
                        </label>
                    </div>
                </div>
            </div>
        `;
    }

    getSessionHeaderGradient(session) {
        const gradients = [
            'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
            'linear-gradient(135deg, #ff8a80 0%, #ea80fc 100%)'
        ];
        
        // Use session ID to consistently assign gradient
        return gradients[session.id % gradients.length];
    }

    getDifficultyColor(difficulty) {
        const colors = {
            'de_dang': '#28a745',
            'trung_binh': '#ffc107',
            'kho': '#dc3545'
        };
        return colors[difficulty] || '#6c757d';
    }

    getEmptyStateHTML() {
        return `
            <div class="empty-state" style="grid-column: 1 / -1; text-align: center; padding: 4rem 2rem;">
                <i class="fas fa-flask" style="font-size: 4rem; color: #e9ecef; margin-bottom: 1rem;"></i>
                <h3>No sessions found</h3>
                <p class="text-muted">Try adjusting your filters or create a new session.</p>
                <a href="/lab/admin/create" class="btn-enhanced btn-primary" style="margin-top: 1rem;">
                    <i class="fas fa-plus"></i>
                    Create Session
                </a>
            </div>
        `;
    }

    showLoadingState() {
        const grid = document.getElementById('sessions-grid');
        grid.innerHTML = Array(6).fill(0).map(() => 
            '<div class="session-card skeleton" style="height: 350px;"></div>'
        ).join('');
    }

    hideLoadingState() {
        // Loading state is replaced by renderSessions
    }

    updateFilters() {
        this.currentFilters = {
            status: document.getElementById('status-filter').value,
            difficulty: document.getElementById('difficulty-filter').value,
            date: document.getElementById('date-filter').value,
            room: document.getElementById('room-filter').value,
            tags: document.getElementById('tags-filter').value,
            sort_by: document.getElementById('sort-by').value,
            sort_order: document.getElementById('sort-order').value
        };
        
        // Remove empty filters
        Object.keys(this.currentFilters).forEach(key => {
            if (!this.currentFilters[key]) {
                delete this.currentFilters[key];
            }
        });
        
        this.currentPage = 1;
        this.loadSessions();
    }

    toggleSessionSelection(sessionId, isSelected) {
        if (isSelected) {
            this.selectedSessions.add(sessionId);
        } else {
            this.selectedSessions.delete(sessionId);
        }
        
        this.updateBulkActionsBar();
        this.updateSessionCardSelection(sessionId, isSelected);
    }

    updateSessionCardSelection(sessionId, isSelected) {
        const card = document.querySelector(`[data-session-id="${sessionId}"]`);
        if (card) {
            card.classList.toggle('selected', isSelected);
        }
    }

    selectAllVisibleSessions() {
        const sessionCards = document.querySelectorAll('.session-card[data-session-id]');
        sessionCards.forEach(card => {
            const sessionId = parseInt(card.dataset.sessionId);
            const checkbox = card.querySelector('input[type="checkbox"]');
            
            if (checkbox) {
                checkbox.checked = true;
                this.selectedSessions.add(sessionId);
                card.classList.add('selected');
            }
        });
        
        this.updateBulkActionsBar();
        this.showNotification(`Selected ${sessionCards.length} sessions`, 'info');
    }

    updateBulkActionsBar() {
        const bulkActions = document.getElementById('bulk-actions');
        const count = this.selectedSessions.size;
        
        if (count > 0) {
            bulkActions.classList.add('show');
            document.getElementById('selected-count').textContent = count;
        } else {
            bulkActions.classList.remove('show');
        }
    }

    async refreshSessions() {
        const refreshBtn = document.getElementById('refresh-sessions');
        const originalContent = refreshBtn.innerHTML;
        
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Refreshing...';
        refreshBtn.disabled = true;
        
        try {
            await this.loadSessions();
            await this.loadStatistics();
            this.showNotification('Sessions refreshed successfully', 'success');
        } catch (error) {
            this.showNotification('Failed to refresh sessions', 'error');
        } finally {
            refreshBtn.innerHTML = originalContent;
            refreshBtn.disabled = false;
        }
    }

    async performBulkAction(action) {
        if (this.selectedSessions.size === 0) {
            this.showNotification('No sessions selected', 'warning');
            return;
        }

        const actionLabels = {
            'activate': 'activate',
            'deactivate': 'deactivate',
            'duplicate': 'duplicate',
            'delete': 'delete'
        };

        const confirmed = confirm(`Are you sure you want to ${actionLabels[action]} ${this.selectedSessions.size} sessions?`);
        if (!confirmed) return;

        try {
            const response = await fetch(`${this.baseApiUrl}/lab-sessions/bulk-actions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    action: action,
                    session_ids: Array.from(this.selectedSessions)
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.showNotification(data.message, 'success');
                this.selectedSessions.clear();
                this.updateBulkActionsBar();
                await this.loadSessions();
            } else {
                throw new Error(data.error || 'Failed to perform action');
            }
        } catch (error) {
            console.error('Error performing bulk action:', error);
            this.showNotification(error.message, 'error');
        }
    }

    showExportModal() {
        this.showModal('export-modal');
    }

    async performExport() {
        const format = document.getElementById('export-format').value;
        const includeAttendees = document.getElementById('include-attendees').checked;
        const selectedOnly = document.getElementById('selected-only').checked;

        const exportBtn = document.getElementById('confirm-export');
        const originalContent = exportBtn.innerHTML;
        
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
        exportBtn.disabled = true;

        try {
            const response = await fetch(`${this.baseApiUrl}/lab-sessions/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    format: format,
                    include_attendees: includeAttendees,
                    session_ids: selectedOnly ? Array.from(this.selectedSessions) : []
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `lab_sessions_${new Date().toISOString().split('T')[0]}.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.closeModal('export-modal');
                this.showNotification('Export completed successfully', 'success');
            } else {
                const data = await response.json();
                throw new Error(data.error || 'Export failed');
            }
        } catch (error) {
            console.error('Error exporting:', error);
            this.showNotification(error.message, 'error');
        } finally {
            exportBtn.innerHTML = originalContent;
            exportBtn.disabled = false;
        }
    }

    async viewSessionDetails(sessionId) {
        try {
            const response = await fetch(`${this.baseApiUrl}/lab-sessions/${sessionId}`);
            const data = await response.json();

            if (response.ok) {
                this.renderSessionModal(data.session);
                this.showModal('session-modal');
            } else {
                throw new Error(data.error || 'Failed to load session details');
            }
        } catch (error) {
            console.error('Error loading session details:', error);
            this.showNotification(error.message, 'error');
        }
    }

    renderSessionModal(session) {
        const modalBody = document.getElementById('session-modal-body');
        const editLink = document.getElementById('edit-session-link');
        
        editLink.href = `/lab/admin/edit/${session.id}`;
        
        modalBody.innerHTML = `
            <div class="session-detail-grid">
                <div class="detail-section">
                    <h4><i class="fas fa-info-circle"></i> Basic Information</h4>
                    <div class="detail-item">
                        <strong>Title:</strong> ${this.escapeHtml(session.tieu_de)}
                    </div>
                    <div class="detail-item">
                        <strong>Description:</strong> ${this.escapeHtml(session.mo_ta || 'No description')}
                    </div>
                    <div class="detail-item">
                        <strong>Location:</strong> ${this.escapeHtml(session.dia_diem)}
                    </div>
                    <div class="detail-item">
                        <strong>Difficulty:</strong> 
                        <span style="color: ${this.getDifficultyColor(session.muc_do_kho)}">
                            ${this.getDifficultyLabel(session.muc_do_kho)}
                        </span>
                    </div>
                    <div class="detail-item">
                        <strong>Verification Code:</strong> 
                        <code style="background: #f8f9fa; padding: 0.25rem 0.5rem; border-radius: 4px;">
                            ${session.ma_xac_thuc || 'Not set'}
                        </code>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4><i class="fas fa-calendar"></i> Schedule</h4>
                    <div class="detail-item">
                        <strong>Date:</strong> ${this.formatDate(session.gio_bat_dau)}
                    </div>
                    <div class="detail-item">
                        <strong>Time:</strong> ${this.formatTime(session.gio_bat_dau)} - ${this.formatTime(session.gio_ket_thuc)}
                    </div>
                    <div class="detail-item">
                        <strong>Duration:</strong> ${this.calculateDuration(session.gio_bat_dau, session.gio_ket_thuc)}
                    </div>
                    <div class="detail-item">
                        <strong>Status:</strong> 
                        <span class="badge ${this.getStatusClass(session.trang_thai)}">
                            ${this.getStatusLabel(session.trang_thai)}
                        </span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4><i class="fas fa-users"></i> Registration & Attendance</h4>
                    <div class="detail-item">
                        <strong>Capacity:</strong> ${session.so_luong_toi_da} students
                    </div>
                    <div class="detail-item">
                        <strong>Registered:</strong> ${session.so_dang_ky || 0} students
                    </div>
                    <div class="detail-item">
                        <strong>Completion Rate:</strong> ${session.completion_rate?.toFixed(1) || 0}%
                    </div>
                    <div class="detail-item">
                        <strong>Average Rating:</strong> 
                        ${session.avg_rating ? `${session.avg_rating.toFixed(1)}/5 ⭐` : 'No ratings yet'}
                    </div>
                </div>

                ${session.tags && session.tags.length > 0 ? `
                    <div class="detail-section">
                        <h4><i class="fas fa-tags"></i> Tags</h4>
                        <div class="session-tags">
                            ${session.tags.map(tag => `<span class="tag">${this.escapeHtml(tag)}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}

                ${session.yeu_cau_thiet_bi && session.yeu_cau_thiet_bi.length > 0 ? `
                    <div class="detail-section">
                        <h4><i class="fas fa-tools"></i> Required Equipment</h4>
                        <ul style="margin: 0; padding-left: 1.5rem;">
                            ${session.yeu_cau_thiet_bi.map(eq => `<li>${this.escapeHtml(eq)}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    calculateDuration(startTime, endTime) {
        const start = new Date(startTime);
        const end = new Date(endTime);
        const durationMs = end - start;
        const hours = Math.floor(durationMs / (1000 * 60 * 60));
        const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
        
        return `${hours}h ${minutes}m`;
    }

    async deleteSession(sessionId) {
        const confirmed = confirm('Are you sure you want to delete this session? This action cannot be undone.');
        if (!confirmed) return;

        try {
            const response = await fetch(`${this.baseApiUrl}/lab-sessions/${sessionId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.showNotification('Session deleted successfully', 'success');
                this.selectedSessions.delete(sessionId);
                this.updateBulkActionsBar();
                await this.loadSessions();
            } else {
                throw new Error(data.error || 'Failed to delete session');
            }
        } catch (error) {
            console.error('Error deleting session:', error);
            this.showNotification(error.message, 'error');
        }
    }

    renderPagination(pagination) {
        const container = document.getElementById('pagination-container');
        
        if (pagination.pages <= 1) {
            container.innerHTML = '';
            return;
        }

        let html = '';
        
        // Previous button
        if (pagination.has_prev) {
            html += `<button class="pagination-btn" onclick="window.enhancedLabManager.changePage(${pagination.page - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>`;
        }
        
        // Page numbers with smart ellipsis
        const { startPage, endPage } = this.calculatePaginationRange(pagination.page, pagination.pages);
        
        if (startPage > 1) {
            html += `<button class="pagination-btn" onclick="window.enhancedLabManager.changePage(1)">1</button>`;
            if (startPage > 2) {
                html += `<span class="pagination-ellipsis">...</span>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `<button class="pagination-btn ${i === pagination.page ? 'active' : ''}" 
                     onclick="window.enhancedLabManager.changePage(${i})">${i}</button>`;
        }
        
        if (endPage < pagination.pages) {
            if (endPage < pagination.pages - 1) {
                html += `<span class="pagination-ellipsis">...</span>`;
            }
            html += `<button class="pagination-btn" onclick="window.enhancedLabManager.changePage(${pagination.pages})">${pagination.pages}</button>`;
        }
        
        // Next button
        if (pagination.has_next) {
            html += `<button class="pagination-btn" onclick="window.enhancedLabManager.changePage(${pagination.page + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>`;
        }
        
        container.innerHTML = html;
    }

    calculatePaginationRange(currentPage, totalPages) {
        const delta = 2; // Number of pages to show on each side of current page
        const rangeStart = Math.max(1, currentPage - delta);
        const rangeEnd = Math.min(totalPages, currentPage + delta);
        
        return { startPage: rangeStart, endPage: rangeEnd };
    }

    changePage(page) {
        this.currentPage = page;
        this.loadSessions();
        
        // Scroll to top of sessions
        document.getElementById('sessions-grid').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }

    // Modal utilities
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }

    // Utility functions
    getCsrfToken() {
        return document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
    }

    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    getStatusClass(status) {
        const statusMap = {
            'scheduled': 'status-upcoming',
            'ongoing': 'status-active',
            'completed': 'status-completed',
            'cancelled': 'status-cancelled'
        };
        return statusMap[status] || 'status-upcoming';
    }

    getStatusLabel(status) {
        const labelMap = {
            'scheduled': 'Upcoming',
            'ongoing': 'Ongoing',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        };
        return labelMap[status] || 'Unknown';
    }

    getDifficultyLabel(difficulty) {
        const labelMap = {
            'de_dang': 'Easy',
            'trung_binh': 'Medium',
            'kho': 'Hard'
        };
        return labelMap[difficulty] || 'Medium';
    }

    formatDate(isoString) {
        return new Date(isoString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            weekday: 'short'
        });
    }

    formatTime(isoString) {
        return new Date(isoString).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }

    // Cleanup
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.body.dataset.page === 'enhanced-lab-sessions') {
        window.enhancedLabManager = new EnhancedLabSessionManager();
    }
});

// Export for global access
window.EnhancedLabSessionManager = EnhancedLabSessionManager;
