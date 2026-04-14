// Handle voting confirmation
function confirmVote(candidateName) {
    return confirm("Are you sure you want to cast your vote for " + candidateName + "?\n\nThis action is final and cannot be undone.");
}

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500); // remove from DOM after fade out
            });
        }, 5000);
    }
});
