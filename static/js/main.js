// Utility functions for garden app

// Format dates consistently
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}

// Show toast notifications for actions
function showNotification(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} position-fixed bottom-0 end-0 m-3`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

// Handle API errors
function handleApiError(error) {
    console.error('API Error:', error);
    showNotification(error.message || 'An error occurred', 'danger');
}