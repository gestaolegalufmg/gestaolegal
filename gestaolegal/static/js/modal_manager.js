class ModalManager {
  constructor() {
    this.activeModals = new Set();
    this.focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    this.previousActiveElement = null;
    
    this.init();
  }

  init() {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.activeModals.size > 0) {
        const lastModal = Array.from(this.activeModals).pop();
        this.close(lastModal);
      }
    });

    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        const modalId = e.target.id;
        this.close(modalId);
      }
    });

    document.addEventListener('focusin', (e) => {
      if (this.activeModals.size > 0) {
        const modal = e.target.closest('.modal-overlay');
        if (!modal && !e.target.closest('.modal-content')) {
          const lastModal = Array.from(this.activeModals).pop();
          this.trapFocus(lastModal);
        }
      }
    });
  }

  /**
   * Open a modal
   * @param {string} modalId - The ID of the modal to open
   * @param {Object} options - Configuration options
   */
  open(modalId, options = {}) {
    const modal = document.getElementById(modalId);
    if (!modal) {
      console.warn(`Modal with ID "${modalId}" not found`);
      return;
    }

    this.previousActiveElement = document.activeElement;

    this.activeModals.add(modalId);

    modal.classList.remove('modal-hidden');

    this.trapFocus(modalId);

    this.dispatchEvent(modalId, 'modal:open', { modal, options });

    if (options.onOpen && typeof options.onOpen === 'function') {
      options.onOpen(modal);
    }
  }

  /**
   * Close a modal
   * @param {string} modalId - The ID of the modal to close
   * @param {Object} options - Configuration options
   */
  close(modalId, options = {}) {
    const modal = document.getElementById(modalId);
    if (!modal) {
      console.warn(`Modal with ID "${modalId}" not found`);
      return;
    }

    modal.classList.add('modal-closing');

    this.activeModals.delete(modalId);

    this.dispatchEvent(modalId, 'modal:close', { modal, options });

    if (options.onClose && typeof options.onClose === 'function') {
      options.onClose(modal);
    }

    setTimeout(() => {
      modal.classList.add('modal-hidden');
      modal.classList.remove('modal-closing');

      if (this.previousActiveElement) {
        this.previousActiveElement.focus();
        this.previousActiveElement = null;
      }

      if (this.activeModals.size === 0) {
        document.body.style.overflow = '';
      }
    }, 300);
  }

  /**
   * Toggle modal visibility
   * @param {string} modalId - The ID of the modal to toggle
   * @param {Object} options - Configuration options
   */
  toggle(modalId, options = {}) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    if (modal.classList.contains('modal-hidden')) {
      this.open(modalId, options);
    } else {
      this.close(modalId, options);
    }
  }

  /**
   * Close all open modals
   */
  closeAll() {
    this.activeModals.forEach(modalId => {
      this.close(modalId);
    });
  }

  /**
   * Check if a modal is open
   * @param {string} modalId - The ID of the modal to check
   * @returns {boolean}
   */
  isOpen(modalId) {
    return this.activeModals.has(modalId);
  }

  /**
   * Get all open modals
   * @returns {Array<string>}
   */
  getOpenModals() {
    return Array.from(this.activeModals);
  }

  /**
   * Trap focus within modal
   * @param {string} modalId - The ID of the modal
   */
  trapFocus(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    const focusableElements = modal.querySelectorAll(this.focusableElements);
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (firstElement) {
      firstElement.focus();
    }

    modal.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    }, { once: false });
  }

  /**
   * @param {string} modalId - The ID of the modal
   * @param {string} eventName - The event name
   * @param {Object} detail - Event detail
   */
  dispatchEvent(modalId, eventName, detail) {
    const event = new CustomEvent(eventName, {
      detail: { modalId, ...detail }
    });
    document.dispatchEvent(event);
  }

  /**
   * Create a modal dynamically
   * @param {Object} config - Modal configuration
   * @returns {string} - The generated modal ID
   */
  create(config) {
    const modalId = config.id || `modal_${Date.now()}`;
    const modal = document.createElement('div');
    
    modal.className = 'modal-overlay modal-hidden';
    modal.id = modalId;
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-labelledby', `${modalId}_title`);
    modal.setAttribute('aria-describedby', `${modalId}_body`);

    modal.innerHTML = `
      <div class="modal-content ${config.size || 'modal-md'}" tabindex="-1">
        <div class="modal-header">
          <h2 class="modal-title" id="${modalId}_title">${config.title || ''}</h2>
          <button type="button" class="modal-close" aria-label="Fechar modal">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body" id="${modalId}_body">
          ${config.body || ''}
        </div>
        ${config.footer ? `
          <div class="modal-footer">
            ${config.footer}
          </div>
        ` : ''}
      </div>
    `;

    modal.querySelector('.modal-close').addEventListener('click', () => {
      this.close(modalId);
    });

    document.body.appendChild(modal);
    return modalId;
  }

  /**
   * Remove a modal from DOM
   * @param {string} modalId - The ID of the modal to remove
   */
  remove(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      this.close(modalId);
      setTimeout(() => {
        modal.remove();
      }, 300);
    }
  }
}

window.ModalManager = new ModalManager();


if (typeof module !== 'undefined' && module.exports) {
  module.exports = ModalManager;
}
