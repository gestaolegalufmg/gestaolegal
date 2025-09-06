document.addEventListener('DOMContentLoaded', function () {
    function showNotification(title, message, type) {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            document.body.appendChild(container);
        }

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;

        // Create notification content wrapper
        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'notification-content';

        // Create icon element
        const iconElement = document.createElement('div');
        iconElement.className = `notification-icon ${type}`;
        iconElement.textContent = getNotificationIcon(type);

        // Create text content wrapper
        const textWrapper = document.createElement('div');
        textWrapper.className = 'notification-text';

        // Create title element
        const titleElement = document.createElement('div');
        titleElement.className = 'notification-title';
        titleElement.textContent = title;

        // Create message element
        const messageElement = document.createElement('div');
        messageElement.className = 'notification-message';
        messageElement.textContent = message;

        // Create close button
        const closeButton = document.createElement('button');
        closeButton.className = 'notification-close';
        closeButton.innerHTML = '×';
        closeButton.setAttribute('aria-label', 'Fechar notificação');

        // Assemble the notification
        textWrapper.appendChild(titleElement);
        textWrapper.appendChild(messageElement);
        contentWrapper.appendChild(iconElement);
        contentWrapper.appendChild(textWrapper);
        contentWrapper.appendChild(closeButton);
        notification.appendChild(contentWrapper);
        container.appendChild(notification);

        // Show notification with animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            hideNotification(notification);
        }, 5000);

        // Add close functionality to close button
        closeButton.addEventListener('click', (e) => {
            e.stopPropagation();
            hideNotification(notification);
        });

        // Add click to dismiss for the entire notification (except close button)
        notification.addEventListener('click', (e) => {
            if (e.target !== closeButton && !closeButton.contains(e.target)) {
                hideNotification(notification);
            }
        });
    }

    function hideNotification(notification) {
        notification.classList.add('hide');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 400); // Match CSS transition duration
    }

    function getNotificationIcon(type) {
        switch (type) {
            case 'success':
                return '✓';
            case 'warning':
                return '⚠';
            case 'danger':
                return '✕';
            case 'info':
            default:
                return 'i';
        }
    }

    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(elem) {
        const categoria = elem.getAttribute('data-category');
        const message = elem.textContent.trim();
        
        let title, type;
        switch (categoria) {
            case 'info':
                title = 'Informe:';
                type = 'info';
                break;
            case 'success':
                title = 'Sucesso!';
                type = 'success';
                break;
            case 'warning':
                title = 'Atenção:';
                type = 'warning';
                break;
            case 'danger':
                title = 'Erro:';
                type = 'danger';
                break;
            default:
                title = 'Informe:';
                type = 'info';
        }
        
        showNotification(title, message, type);
    });
});