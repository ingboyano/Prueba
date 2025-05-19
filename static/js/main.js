// Enable tooltips everywhere
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Initialize DataTables for better table interaction
    if (document.querySelector('.table-datatable')) {
        const table = $('.table-datatable').DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json'
            },
            responsive: true,
            pageLength: 10,
            lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "Todos"]],
            dom: 'Bfrtip',
            order: [[0, 'desc']]
        });
    }
    
    // Animate elements on scroll
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(el => observer.observe(el));
    }
    
    // Flow logo animation on hover for all pages
    const flowLogos = document.querySelectorAll('.flow-logo');
    
    flowLogos.forEach(logo => {
        logo.addEventListener('mouseover', function() {
            this.style.filter = 'drop-shadow(0 0 8px var(--flow-primary))';
        });
        
        logo.addEventListener('mouseout', function() {
            this.style.filter = '';
        });
    });
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const x = e.clientX - e.target.getBoundingClientRect().left;
            const y = e.clientY - e.target.getBoundingClientRect().top;
            
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
});

// VM Status change with animation
function updateVMStatus(vmId, status, statusName) {
    if (confirmAction(`¿Estás seguro que deseas cambiar el estado a ${statusName}?`)) {
        fetch(`/vm/${vmId}/status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: status }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'éxito' || data.status === 'success') {
                const statusCell = document.querySelector(`#vm-${vmId}-status`);
                const oldBadge = statusCell.querySelector('.badge');
                const newBadge = document.createElement('span');
                
                // Create new badge with transition
                newBadge.className = `badge status-${status.toLowerCase()}`;
                newBadge.innerHTML = statusName;
                newBadge.style.opacity = '0';
                newBadge.style.transform = 'scale(0.8)';
                
                // Add new badge and animate it
                statusCell.appendChild(newBadge);
                
                // Fade out old badge
                oldBadge.style.transition = 'all 0.3s ease';
                oldBadge.style.opacity = '0';
                oldBadge.style.transform = 'scale(0.8)';
                
                setTimeout(() => {
                    oldBadge.remove();
                    newBadge.style.transition = 'all 0.3s ease';
                    newBadge.style.opacity = '1';
                    newBadge.style.transform = 'scale(1)';
                }, 300);
                
                // Show success message
                showNotification('Estado actualizado correctamente', 'success');
            } else {
                showNotification('Error al actualizar el estado', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error al actualizar el estado', 'error');
        });
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="bi ${type === 'success' ? 'bi-check-circle' : type === 'error' ? 'bi-exclamation-circle' : 'bi-info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">×</button>
    `;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Show with animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Auto dismiss after 5 seconds
    const dismissTimer = setTimeout(() => {
        dismissNotification(notification);
    }, 5000);
    
    // Close button handler
    notification.querySelector('.notification-close').addEventListener('click', () => {
        clearTimeout(dismissTimer);
        dismissNotification(notification);
    });
}

// Dismiss notification with animation
function dismissNotification(notification) {
    notification.classList.add('hiding');
    setTimeout(() => {
        notification.remove();
    }, 300);
}

// Confirm dialog for important actions
function confirmAction(message) {
    return confirm(message || '¿Estás seguro que deseas realizar esta acción?');
}
