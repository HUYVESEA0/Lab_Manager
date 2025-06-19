/**
 * Advanced User Creation Component
 * Provides modern UI for creating users with validation
 */

class UserCreationManager {
    constructor() {
        this.apiEndpoint = '/api/users';
        this.validateTimeout = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupPasswordStrengthIndicator();
        this.setupRealTimeValidation();
    }

    setupEventListeners() {
        // Form submission
        const createForm = document.getElementById('createUserForm');
        if (createForm) {
            createForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Bulk creation form
        const bulkForm = document.getElementById('bulkUserForm');
        if (bulkForm) {
            bulkForm.addEventListener('submit', (e) => this.handleBulkSubmit(e));
        }

        // Password visibility toggles
        document.querySelectorAll('.password-toggle').forEach(btn => {
            btn.addEventListener('click', (e) => this.togglePasswordVisibility(e));
        });
    }

    setupPasswordStrengthIndicator() {
        const passwordInput = document.getElementById('password');
        if (passwordInput) {
            passwordInput.addEventListener('input', (e) => {
                this.updatePasswordStrength(e.target.value);
            });
        }
    }

    setupRealTimeValidation() {
        // Username validation
        const usernameInput = document.getElementById('ten_nguoi_dung');
        if (usernameInput) {
            usernameInput.addEventListener('input', (e) => {
                clearTimeout(this.validateTimeout);
                this.validateTimeout = setTimeout(() => {
                    this.validateUsername(e.target.value);
                }, 500);
            });
        }

        // Email validation
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.addEventListener('input', (e) => {
                clearTimeout(this.validateTimeout);
                this.validateTimeout = setTimeout(() => {
                    this.validateEmail(e.target.value);
                }, 500);
            });
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const userData = Object.fromEntries(formData.entries());

        // Show loading state
        this.setLoadingState(true);

        try {
            const response = await fetch(`${this.apiEndpoint}/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(userData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showSuccess(result.message);
                form.reset();
                this.resetValidationStates();
                
                // Redirect or update UI
                setTimeout(() => {
                    window.location.href = '/admin/users';
                }, 2000);
            } else {
                this.showError(result.message || 'Có lỗi xảy ra khi tạo người dùng');
            }
        } catch (error) {
            console.error('Error creating user:', error);
            this.showError('Có lỗi xảy ra khi tạo người dùng');
        } finally {
            this.setLoadingState(false);
        }
    }

    async handleBulkSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const usersData = document.getElementById('users_data').value;

        try {
            const users = JSON.parse(usersData);
            
            this.setLoadingState(true);

            const response = await fetch(`${this.apiEndpoint}/bulk-create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ users })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                const summary = result.summary;
                this.showSuccess(
                    `Đã tạo ${summary.success}/${summary.total} người dùng thành công`
                );
                
                // Show detailed results
                this.showBulkResults(result.results);
                
            } else {
                this.showError(result.message || 'Có lỗi xảy ra khi tạo người dùng hàng loạt');
            }
        } catch (error) {
            console.error('Error in bulk creation:', error);
            this.showError('Có lỗi xảy ra khi tạo người dùng hàng loạt');
        } finally {
            this.setLoadingState(false);
        }
    }

    async validateUsername(username) {
        if (!username || username.length < 3) {
            this.setFieldValidation('ten_nguoi_dung', null);
            return;
        }

        try {
            const response = await fetch(`${this.apiEndpoint}/check-username`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ username })
            });

            const result = await response.json();
            
            if (result.available) {
                this.setFieldValidation('ten_nguoi_dung', true, 'Tên người dùng khả dụng');
            } else {
                this.setFieldValidation('ten_nguoi_dung', false, 'Tên người dùng đã tồn tại');
            }
        } catch (error) {
            console.error('Error validating username:', error);
        }
    }

    async validateEmail(email) {
        if (!email || !this.isValidEmail(email)) {
            this.setFieldValidation('email', null);
            return;
        }

        try {
            const response = await fetch(`${this.apiEndpoint}/check-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ email })
            });

            const result = await response.json();
            
            if (result.available) {
                this.setFieldValidation('email', true, 'Email khả dụng');
            } else {
                this.setFieldValidation('email', false, 'Email đã được đăng ký');
            }
        } catch (error) {
            console.error('Error validating email:', error);
        }
    }

    updatePasswordStrength(password) {
        const strengthIndicator = document.getElementById('passwordStrength');
        const strengthFill = document.getElementById('strengthFill');
        const strengthText = document.getElementById('strengthText');

        if (!strengthIndicator || !strengthFill || !strengthText) return;

        const strength = this.calculatePasswordStrength(password);
        
        strengthFill.style.width = `${strength.percentage}%`;
        strengthFill.className = `strength-fill strength-${strength.level}`;
        strengthText.textContent = `Độ mạnh: ${strength.text}`;
    }

    calculatePasswordStrength(password) {
        let score = 0;
        let text = 'Rất yếu';
        
        if (password.length >= 8) score++;
        if (/[a-z]/.test(password)) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;

        switch (score) {
            case 0:
            case 1:
                return { level: 'weak', percentage: 20, text: 'Rất yếu' };
            case 2:
                return { level: 'weak', percentage: 40, text: 'Yếu' };
            case 3:
                return { level: 'fair', percentage: 60, text: 'Khá' };
            case 4:
                return { level: 'good', percentage: 80, text: 'Tốt' };
            case 5:
                return { level: 'strong', percentage: 100, text: 'Rất mạnh' };
            default:
                return { level: 'weak', percentage: 20, text: 'Rất yếu' };
        }
    }

    setFieldValidation(fieldId, isValid, message) {
        const field = document.getElementById(fieldId);
        const feedback = field.parentNode.querySelector('.validation-feedback');
        
        if (!feedback) {
            const feedbackEl = document.createElement('div');
            feedbackEl.className = 'validation-feedback';
            field.parentNode.appendChild(feedbackEl);
        }

        const feedbackEl = field.parentNode.querySelector('.validation-feedback');
        
        field.classList.remove('is-valid', 'is-invalid');
        
        if (isValid === true) {
            field.classList.add('is-valid');
            feedbackEl.className = 'validation-feedback valid-feedback';
            feedbackEl.textContent = message;
        } else if (isValid === false) {
            field.classList.add('is-invalid');
            feedbackEl.className = 'validation-feedback invalid-feedback';
            feedbackEl.textContent = message;
        } else {
            feedbackEl.textContent = '';
        }
    }

    resetValidationStates() {
        document.querySelectorAll('.is-valid, .is-invalid').forEach(el => {
            el.classList.remove('is-valid', 'is-invalid');
        });
        document.querySelectorAll('.validation-feedback').forEach(el => {
            el.textContent = '';
        });
    }

    togglePasswordVisibility(e) {
        const button = e.target.closest('.password-toggle');
        const input = button.previousElementSibling;
        const icon = button.querySelector('i');
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }

    setLoadingState(loading) {
        const submitButtons = document.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(btn => {
            if (loading) {
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
            } else {
                btn.disabled = false;
                btn.innerHTML = btn.dataset.originalText || btn.textContent;
            }
        });
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span>${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    showBulkResults(results) {
        const modal = document.createElement('div');
        modal.className = 'bulk-results-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Kết quả tạo người dùng hàng loạt</h3>
                    <button class="modal-close" onclick="this.closest('.bulk-results-modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${results.map((result, index) => `
                        <div class="result-item ${result.success ? 'success' : 'error'}">
                            <div class="result-icon">
                                <i class="fas ${result.success ? 'fa-check' : 'fa-times'}"></i>
                            </div>
                            <div class="result-content">
                                <strong>${result.success ? result.user.ten_nguoi_dung : result.user_data.ten_nguoi_dung}</strong>
                                <span>${result.message}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="this.closest('.bulk-results-modal').remove()">
                        Đóng
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    getCSRFToken() {
        const tokenMeta = document.querySelector('meta[name="csrf-token"]');
        return tokenMeta ? tokenMeta.getAttribute('content') : '';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new UserCreationManager();
});

// CSS Styles for notifications and modals
const styles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        max-width: 400px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        animation: slideIn 0.3s ease-out;
    }

    .notification-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }

    .notification-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }

    .notification-content {
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .notification-close {
        background: none;
        border: none;
        margin-left: auto;
        padding: 0.25rem;
        cursor: pointer;
        opacity: 0.7;
    }

    .notification-close:hover {
        opacity: 1;
    }

    .bulk-results-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .modal-content {
        background: white;
        border-radius: 12px;
        max-width: 600px;
        max-height: 80vh;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    .modal-header {
        padding: 1.5rem;
        border-bottom: 1px solid #dee2e6;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .modal-body {
        padding: 1.5rem;
        max-height: 400px;
        overflow-y: auto;
    }

    .modal-footer {
        padding: 1rem 1.5rem;
        border-top: 1px solid #dee2e6;
        text-align: right;
    }

    .result-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        border-radius: 6px;
    }

    .result-item.success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }

    .result-item.error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }

    .result-content {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .validation-feedback {
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }

    .valid-feedback {
        color: #28a745;
    }

    .invalid-feedback {
        color: #dc3545;
    }

    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = styles;
document.head.appendChild(styleSheet);
