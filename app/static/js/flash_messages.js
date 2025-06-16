/**
 * Flash Messages Enhanced Functionality
 * Lab Manager - Interactive notification system
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeFlashMessages();
});

function initializeFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message, .alert');
    
    flashMessages.forEach(function(message) {
        // Skip already initialized messages
        if (message.hasAttribute('data-flash-initialized')) {
            return;
        }
        message.setAttribute('data-flash-initialized', 'true');
        
        // Add auto-dismiss class for automatic removal (unless it's persistent)
        if (!message.classList.contains('persistent') && !message.classList.contains('alert-dismissible')) {
            message.classList.add('auto-dismiss');
        }
        
        // Ensure close button functionality
        const closeButton = message.querySelector('.close');
        if (closeButton) {
            closeButton.addEventListener('click', function(e) {
                e.preventDefault();
                dismissMessage(message);
            });
        }
        
        // Add dismissible functionality for non-Bootstrap alerts (for clicking on message)
        if (!message.classList.contains('no-dismiss') && !closeButton) {
            message.classList.add('dismissible');
            message.style.cursor = 'pointer';
            message.addEventListener('click', function() {
                dismissMessage(this);
            });
        }
        
        // Add urgent class for danger messages automatically
        if (message.classList.contains('danger') || message.classList.contains('alert-danger')) {
            if (isUrgentMessage(message.textContent)) {
                message.classList.add('urgent');
            }
        }
        
        // Auto dismiss after timeout (unless persistent or has Bootstrap dismiss button)
        const shouldAutoDismiss = message.classList.contains('auto-dismiss') || 
                                 (!message.classList.contains('persistent') && 
                                  !message.classList.contains('alert-dismissible'));
        
        if (shouldAutoDismiss) {
            setTimeout(function() {
                if (!message.classList.contains('closed') && message.parentNode) {
                    dismissMessage(message);
                }
            }, getAutoDismissTime(message));
        }
    });
}

function dismissMessage(messageElement) {
    messageElement.classList.add('closed');
    
    // Remove element after animation
    setTimeout(function() {
        if (messageElement.parentNode) {
            messageElement.parentNode.removeChild(messageElement);
        }
    }, 300);
}

function getAutoDismissTime(messageElement) {
    // Different dismiss times based on message type
    if (messageElement.classList.contains('danger') || 
        messageElement.classList.contains('alert-danger') ||
        messageElement.classList.contains('critical')) {
        return 8000; // 8 seconds for important messages
    } else if (messageElement.classList.contains('warning') || 
               messageElement.classList.contains('alert-warning')) {
        return 6000; // 6 seconds for warnings
    } else {
        return 5000; // 5 seconds for other messages
    }
}

function isUrgentMessage(messageText) {
    const urgentKeywords = [
        'cảnh báo',
        'nguy hiểm', 
        'lỗi',
        'thất bại',
        'không thành công',
        'xóa',
        'mất',
        'reset',
        'đặt lại',
        'hết hạn',
        'không hợp lệ',
        'cần thiết',
        'bắt buộc'
    ];
    
    const text = messageText.toLowerCase();
    return urgentKeywords.some(keyword => text.includes(keyword));
}

// Function to show new flash message programmatically
function showFlashMessage(message, type = 'info', options = {}) {
    const container = document.querySelector('.flash-messages') || createFlashContainer();
    
    const messageElement = document.createElement('div');
    messageElement.className = `flash-message ${type}`;
    
    if (options.urgent) {
        messageElement.classList.add('urgent');
    }
    
    if (options.critical) {
        messageElement.classList.add('critical');
    }
    
    if (options.persistent) {
        messageElement.classList.add('persistent');
    }
    
    if (options.dismissible !== false) {
        messageElement.classList.add('dismissible');
    }
    
    messageElement.textContent = message;
    
    container.appendChild(messageElement);
    
    // Initialize the new message
    initializeFlashMessages();
    
    return messageElement;
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    
    // Insert at the top of main content or body
    const mainContent = document.querySelector('main') || 
                       document.querySelector('.container') || 
                       document.body;
    
    mainContent.insertBefore(container, mainContent.firstChild);
    
    return container;
}

// Export functions for use in other scripts
window.FlashMessages = {
    show: showFlashMessage,
    dismiss: dismissMessage,
    initialize: initializeFlashMessages
};

// Auto-initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeFlashMessages);
} else {
    initializeFlashMessages();
}
