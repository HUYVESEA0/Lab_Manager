document.addEventListener('DOMContentLoaded', function() {
    // Get container and form elements
    const container = document.getElementById('container');
    const signInContainer = document.querySelector('.sign-in-container');
    const signUpContainer = document.querySelector('.sign-up-container');
    const mobileSwitchButton = document.getElementById('mobileSwitchButton');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    // Fix initialization issues
    if (signInContainer) signInContainer.style.display = 'flex';
    if (signUpContainer) signUpContainer.style.display = 'flex';

    // IMPORTANT CHANGE: Ensure forms are visible based on URL
    const currentPath = window.location.pathname;
    if (currentPath.includes('register')) {
        container.classList.add('right-panel-active');
        if (mobileSwitchButton) {
            mobileSwitchButton.textContent = '03ng nhadp';
            mobileSwitchButton.setAttribute('data-target', 'login');
        }
        // Make registration form visible immediately
        if (signUpContainer) {
            signUpContainer.style.opacity = '1';
            signUpContainer.style.visibility = 'visible';
            signUpContainer.style.zIndex = '5';
        }
        if (signInContainer) {
            signInContainer.style.opacity = '0';
            signInContainer.style.visibility = 'hidden';
        }
    } else {
        container.classList.remove('right-panel-active');
        if (mobileSwitchButton) {
            mobileSwitchButton.textContent = '03ng kd';
            mobileSwitchButton.setAttribute('data-target', 'register');
        }
        // Make login form visible immediately
        if (signInContainer) {
            signInContainer.style.opacity = '1';
            signInContainer.style.visibility = 'visible';
            signInContainer.style.zIndex = '5';
        }
        if (signUpContainer) {
            signUpContainer.style.opacity = '0';
            signUpContainer.style.visibility = 'hidden';
        }
    }

    // Helper functions for form visibility
    function makeRegistrationFormVisible() {
        if (!signUpContainer || !signInContainer) return;

        signUpContainer.style.opacity = '1';
        signUpContainer.style.visibility = 'visible';
        signUpContainer.style.display = 'flex';
        signUpContainer.style.zIndex = '5';

        signInContainer.style.opacity = '0';
        signInContainer.style.visibility = 'hidden';
        signInContainer.style.zIndex = '1';
    }

    function makeLoginFormVisible() {
        if (!signUpContainer || !signInContainer) return;

        signInContainer.style.opacity = '1';
        signInContainer.style.visibility = 'visible';
        signInContainer.style.display = 'flex';
        signInContainer.style.zIndex = '2';

        signUpContainer.style.opacity = '0';
        signUpContainer.style.visibility = 'hidden';
        signUpContainer.style.zIndex = '1';
    }

    // Switch form function with simplified logic
    function switchForm(targetForm) {
        if (targetForm === 'register') {
            // Update UI for registration
            container.classList.add('right-panel-active');
            makeRegistrationFormVisible();

            // IMPORTANT CHANGE: Use proper form submission instead of history.pushState
            // Don't update URL with pushState to avoid CSRF issues
            document.title = '03ng kd - Python Manager';

            // Update mobile button if exists
            if (mobileSwitchButton) {
                mobileSwitchButton.textContent = '03ng nhadp';
                mobileSwitchButton.setAttribute('data-target', 'login');
            }
        } else {
            // Update UI for login
            container.classList.remove('right-panel-active');
            makeLoginFormVisible();

            // IMPORTANT CHANGE: Use proper form submission instead of history.pushState
            // Don't update URL with pushState to avoid CSRF issues
            document.title = '03ng nhadp - Python Manager';

            // Update mobile button if exists
            if (mobileSwitchButton) {
                mobileSwitchButton.textContent = '03ng kd';
                mobileSwitchButton.setAttribute('data-target', 'register');
            }
        }
    }

    // Attach event listeners to form switch buttons
    const switchButtons = document.querySelectorAll('.switch-form');
    switchButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetForm = this.getAttribute('data-target');
            switchForm(targetForm);
        });
    });

    // Mobile switch button functionality
    if (mobileSwitchButton) {
        mobileSwitchButton.addEventListener('click', function() {
            const targetForm = this.getAttribute('data-target');
            switchForm(targetForm);
        });
    }

    // Handle browser back/forward events
    window.addEventListener('popstate', function() {
        const currentPath = window.location.pathname;
        if (currentPath.includes('register')) {
            container.classList.add('right-panel-active');
            makeRegistrationFormVisible();
        } else {
            container.classList.remove('right-panel-active');
            makeLoginFormVisible();
        }
    });

    // Fix form submission handling
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            // Get the current CSRF token before submission
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            if (csrfToken) {
                const csrfField = loginForm.querySelector('input[name="csrf_token"]');
                if (csrfField) {
                    csrfField.value = csrfToken;
                }
            }

            // Remove previous error messages
            loginForm.querySelectorAll('.error-message').forEach(el => el.remove());

            const emailInput = loginForm.querySelector('input[name="email"]');
            const passwordInput = loginForm.querySelector('input[name="password"]');
            let hasError = false;

            // Validate email
            if (!emailInput.value.trim()) {
                showFieldError(emailInput, 'Email kh4ng 10e3c 1ec3 tred1ng');
                hasError = true;
            }

            // Validate password
            if (!passwordInput.value) {
                showFieldError(passwordInput, 'Meadt khea9u kh4ng 10ee3c 1ec3 tred1ng');
                hasError = true;
            }

            // FIXED: Only prevent submission if there's an error
            if (hasError) {
                e.preventDefault();
            }
            // Otherwise let the form submit normally
        });
    }

    // Helper function to show field errors
    function showFieldError(inputElement, message) {
        const errorSpan = document.createElement('span');
        errorSpan.className = 'error-message';
        errorSpan.textContent = message;
        inputElement.parentNode.insertBefore(errorSpan, inputElement.nextSibling);
        inputElement.classList.add('is-invalid');
    }

    // Enhanced CSRF and form handling utilities
    function showSuccessMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'success-message';
        messageDiv.textContent = message;
        messageDiv.style.cssText = `
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            text-align: center;
        `;
        
        // Insert at top of container
        const container = document.getElementById('container');
        if (container) {
            container.insertBefore(messageDiv, container.firstChild);
            // Auto remove after 5 seconds
            setTimeout(() => messageDiv.remove(), 5000);
        }
    }

    // If there's any direct cookie setting in JavaScript, update it like this:
    function setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + encodeURIComponent(value) + expires + "; path=/; Secure; SameSite=Lax";
    }

    // Initialize API when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Wait for LabManagerAPI to be available
        if (window.labAPI) {
            console.log('LabManagerAPI is ready for form submissions');
        } else {
            console.warn('LabManagerAPI not found, using fallback CSRF handling');
        }
    });
});
