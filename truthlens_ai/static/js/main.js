// Global Toast Notification Utility
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-circle-check';
    if (type === 'error') icon = 'fa-circle-xmark';
    if (type === 'warning') icon = 'fa-triangle-exclamation';
    
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Live character counter for text areas
document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('news-text');
    const counter = document.getElementById('char-count');
    if (textarea && counter) {
        textarea.addEventListener('input', () => {
            const count = textarea.value.trim().length;
            counter.innerText = `${count} characters (min. 15 required)`;
            if (count >= 15) {
                counter.style.color = '#34d399';
            } else {
                counter.style.color = '#94a3b8';
            }
        });
    }
});
