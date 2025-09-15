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

        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'notification-content';

        const iconWrapper = document.createElement('div');
        iconWrapper.className = 'notification-icon-wrapper';
        
        const iconElement = document.createElement('div');
        iconElement.className = `notification-icon ${type} icon ${getNotificationIcon(type)}`;
        
        iconWrapper.appendChild(iconElement);

        const textWrapper = document.createElement('div');
        textWrapper.className = 'notification-text';

        const titleElement = document.createElement('div');
        titleElement.className = 'notification-title';
        titleElement.textContent = title;

        const messageElement = document.createElement('div');
        messageElement.className = 'notification-message';
        messageElement.textContent = message;

        const closeButton = document.createElement('button');
        closeButton.className = 'notification-close';
        closeButton.innerHTML = '×';
        closeButton.setAttribute('aria-label', 'Fechar notificação');

        textWrapper.appendChild(titleElement);
        textWrapper.appendChild(messageElement);
        contentWrapper.appendChild(iconWrapper);
        contentWrapper.appendChild(textWrapper);
        contentWrapper.appendChild(closeButton);
        notification.appendChild(contentWrapper);
        container.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        let hideTimeout;
        let isHovered = false;
        
        function startHideTimer() {
            if (hideTimeout) {
                clearTimeout(hideTimeout);
            }
            hideTimeout = setTimeout(() => {
                hideNotification(notification);
            }, isHovered ? 3000 : 5000);
        }

        startHideTimer();

        notification.addEventListener('mouseenter', () => {
            isHovered = true;
            if (hideTimeout) {
                clearTimeout(hideTimeout);
            }
        });

        notification.addEventListener('mouseleave', () => {
            isHovered = false;
            startHideTimer();
        });

        closeButton.addEventListener('click', (e) => {
            e.stopPropagation();
            if (hideTimeout) {
                clearTimeout(hideTimeout);
            }
            hideNotification(notification);
        });

        notification.addEventListener('click', (e) => {
            if (e.target !== closeButton && !closeButton.contains(e.target)) {
                if (hideTimeout) {
                    clearTimeout(hideTimeout);
                }
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
        }, 400);
    }

    function getNotificationIcon(type) {
        switch (type) {
            case 'success':
                return 'icon-check';
            case 'warning':
                return 'icon-exclamation-triangle';
            case 'danger':
                return 'icon-close';
            case 'info':
            default:
                return 'icon-info-circle';
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
            case 'error':
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