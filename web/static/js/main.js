// PassAudit - Main JavaScript

// Utility functions
const PassAudit = {
    // Show loading spinner on button
    showLoading: function(button) {
        const originalText = button.innerHTML;
        button.disabled = true;
        button.dataset.originalText = originalText;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    },

    // Hide loading spinner
    hideLoading: function(button) {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText;
    },

    // Show alert message
    showAlert: function(container, message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        container.insertBefore(alertDiv, container.firstChild);

        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }, 5000);
    },

    // Format strength score as badge
    getStrengthBadge: function(score) {
        if (score >= 80) return '<span class="badge bg-success">Very Strong</span>';
        if (score >= 60) return '<span class="badge bg-info">Strong</span>';
        if (score >= 40) return '<span class="badge bg-warning">Medium</span>';
        if (score >= 20) return '<span class="badge bg-orange text-white">Weak</span>';
        return '<span class="badge bg-danger">Very Weak</span>';
    },

    // Get progress bar class based on score
    getProgressBarClass: function(score) {
        if (score >= 80) return 'bg-success';
        if (score >= 60) return 'bg-info';
        if (score >= 40) return 'bg-warning';
        if (score >= 20) return 'bg-orange';
        return 'bg-danger';
    },

    // Copy text to clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                return true;
            }).catch(() => {
                return false;
            });
        } else {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                document.body.removeChild(textarea);
                return true;
            } catch (err) {
                document.body.removeChild(textarea);
                return false;
            }
        }
    }
};

// Make PassAudit object available globally
window.PassAudit = PassAudit;
