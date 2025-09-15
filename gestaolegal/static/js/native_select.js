class NativeSelect {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            placeholder: 'Selecione uma opção...',
            allowClear: false,
            multiple: false,
            ajax: null,
            delay: 300,
            minimumInputLength: 0,
            width: '100%',
            ...options
        };
        
        this.isOpen = false;
        this.selectedOptions = new Set();
        this.filteredOptions = [];
        this.allOptions = [];
        this.searchTerm = '';
        this.debounceTimer = null;
        
        this.init();
    }
    
    init() {
        this.createWrapper();
        this.createSelectElement();
        this.createDropdown();
        this.bindEvents();
        this.loadInitialData();
    }
    
    createWrapper() {
        // Create wrapper container
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'native-select-wrapper';
        this.wrapper.style.position = 'relative';
        this.wrapper.style.width = this.options.width;
        
        this.element.parentNode.insertBefore(this.wrapper, this.element.nextSibling);
        
        this.element.style.display = 'none';
    }
    
    createSelectElement() {
        this.selectElement = document.createElement('div');
        this.selectElement.className = 'native-select';
        this.selectElement.setAttribute('tabindex', '0');
        this.selectElement.setAttribute('role', 'combobox');
        this.selectElement.setAttribute('aria-expanded', 'false');
        this.selectElement.setAttribute('aria-haspopup', 'listbox');
        
        this.displayArea = document.createElement('div');
        this.displayArea.className = 'native-select-display';
        
        this.valueDisplay = document.createElement('div');
        this.valueDisplay.className = 'native-select-value';
        this.valueDisplay.textContent = this.options.placeholder;
        
        if (this.options.allowClear) {
            this.clearButton = document.createElement('button');
            this.clearButton.className = 'native-select-clear';
            this.clearButton.innerHTML = '×';
            this.clearButton.type = 'button';
            this.clearButton.setAttribute('aria-label', 'Limpar seleção');
        }
        
        this.arrow = document.createElement('div');
        this.arrow.className = 'native-select-arrow';
        this.arrow.innerHTML = '▼';
        
        this.displayArea.appendChild(this.valueDisplay);
        if (this.clearButton) {
            this.displayArea.appendChild(this.clearButton);
        }
        this.displayArea.appendChild(this.arrow);
        this.selectElement.appendChild(this.displayArea);
        
        this.wrapper.appendChild(this.selectElement);
    }
    
    createDropdown() {
        // Create dropdown container
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'native-select-dropdown';
        this.dropdown.setAttribute('role', 'listbox');
        this.dropdown.style.display = 'none';
        
        // Create search input if AJAX is enabled
        if (this.options.ajax) {
            this.searchInput = document.createElement('input');
            this.searchInput.className = 'native-select-search';
            this.searchInput.type = 'text';
            this.searchInput.placeholder = 'Pesquisar...';
            this.searchInput.setAttribute('aria-label', 'Pesquisar opções');
            this.dropdown.appendChild(this.searchInput);
        }
        
        this.optionsContainer = document.createElement('div');
        this.optionsContainer.className = 'native-select-options';
        this.dropdown.appendChild(this.optionsContainer);
        
        this.loadingIndicator = document.createElement('div');
        this.loadingIndicator.className = 'native-select-loading';
        this.loadingIndicator.textContent = 'Carregando...';
        this.loadingIndicator.style.display = 'none';
        this.dropdown.appendChild(this.loadingIndicator);
        
        this.noResults = document.createElement('div');
        this.noResults.className = 'native-select-no-results';
        this.noResults.textContent = 'Nenhum resultado encontrado';
        this.noResults.style.display = 'none';
        this.dropdown.appendChild(this.noResults);
        
        this.emptyList = document.createElement('div');
        this.emptyList.className = 'native-select-empty-list';
        this.emptyList.textContent = 'Nenhuma opção disponível';
        this.emptyList.style.display = 'none';
        this.dropdown.appendChild(this.emptyList);
        
        this.wrapper.appendChild(this.dropdown);
    }
    
    bindEvents() {
        this.selectElement.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggle();
        });
        
        this.selectElement.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });
        
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
            
            this.searchInput.addEventListener('keydown', (e) => {
                this.handleSearchKeydown(e);
            });
        }
        
        if (this.clearButton) {
            this.clearButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.clearSelection();
            });
        }
        
        document.addEventListener('click', (e) => {
            if (!this.wrapper.contains(e.target)) {
                this.close();
            }
        });
        
        window.addEventListener('resize', () => {
            if (this.isOpen) {
                this.positionDropdown();
            }
        });
    }
    
    handleKeydown(e) {
        switch (e.key) {
            case 'Enter':
            case ' ':
                e.preventDefault();
                this.toggle();
                break;
            case 'Escape':
                this.close();
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.open();
                this.focusNextOption();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.open();
                this.focusPreviousOption();
                break;
        }
    }
    
    handleSearchKeydown(e) {
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.focusNextOption();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.focusPreviousOption();
                break;
            case 'Enter':
                e.preventDefault();
                this.selectFocusedOption();
                break;
            case 'Escape':
                this.close();
                break;
        }
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        if (this.isOpen) return;
        
        this.isOpen = true;
        this.selectElement.classList.add('open');
        this.selectElement.setAttribute('aria-expanded', 'true');
        this.dropdown.style.display = 'block';
        
        this.positionDropdown();
        
        if (this.searchInput) {
            this.searchInput.focus();
        } else {
            this.focusFirstOption();
        }
        
        if (this.allOptions.length === 0) {
            this.loadData();
        }
    }
    
    close() {
        if (!this.isOpen) return;
        
        this.isOpen = false;
        this.selectElement.classList.remove('open');
        this.selectElement.setAttribute('aria-expanded', 'false');
        this.dropdown.style.display = 'none';
        
        if (this.searchInput) {
            this.searchInput.value = '';
            this.searchTerm = '';
        }
    }
    
    positionDropdown() {
        const rect = this.selectElement.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const dropdownHeight = 200; 
        
        const spaceBelow = viewportHeight - rect.bottom;
        const spaceAbove = rect.top;
        
        if (spaceBelow >= dropdownHeight || spaceBelow > spaceAbove) {
            this.dropdown.style.top = '100%';
            this.dropdown.style.bottom = 'auto';
            this.dropdown.classList.remove('above');
        } else {
            this.dropdown.style.bottom = '100%';
            this.dropdown.style.top = 'auto';
            this.dropdown.classList.add('above');
        }
        
        this.dropdown.style.left = '0';
        this.dropdown.style.right = '0';
    }
    
    async loadData(searchTerm = '') {
        if (!this.options.ajax) return;
        
        if (searchTerm.length < this.options.minimumInputLength) {
            this.showNoResults();
            return;
        }
        
        this.showLoading();
        
        try {
            let ajaxParams = {};
            if (typeof this.options.ajax.params === 'function') {
                ajaxParams = this.options.ajax.params(searchTerm);
            } else {
                ajaxParams = { ...this.options.ajax.params };
            }
            
            const params = new URLSearchParams({
                term: searchTerm,
                ...ajaxParams
            });
            
            const response = await fetch(`${this.options.ajax.url}?${params}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.allOptions = data.results || data;
            this.filteredOptions = [...this.allOptions];
            this.renderOptions();
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Erro ao carregar dados');
        } finally {
            this.hideLoading();
        }
    }
    
    loadInitialData() {
        if (this.options.ajax) {
            this.loadData('');
        } else {
            this.loadFromSelectOptions();
        }
    }
    
    loadFromSelectOptions() {
        this.allOptions = Array.from(this.element.options).map(option => ({
            id: option.value,
            text: option.text,
            selected: option.selected
        }));
        
        this.filteredOptions = [...this.allOptions];
        this.renderOptions();
    }
    
    handleSearch(searchTerm) {
        this.searchTerm = searchTerm;
        
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        this.debounceTimer = setTimeout(() => {
            if (this.options.ajax) {
                this.loadData(searchTerm);
            } else {
                this.filterOptions(searchTerm);
            }
        }, this.options.delay);
    }
    
    filterOptions(searchTerm) {
        if (!searchTerm) {
            this.filteredOptions = [...this.allOptions];
        } else {
            const term = searchTerm.toLowerCase();
            this.filteredOptions = this.allOptions.filter(option => 
                option.text.toLowerCase().includes(term)
            );
        }
        
        this.renderOptions();
    }
    
    renderOptions() {
        this.optionsContainer.innerHTML = '';
        
        if (this.allOptions.length === 0) {
            this.showEmptyList();
            return;
        }
        
        if (this.filteredOptions.length === 0) {
            this.showNoResults();
            return;
        }
        
        this.hideNoResults();
        this.hideEmptyList();
        
        this.filteredOptions.forEach((option, index) => {
            const optionElement = this.createOptionElement(option, index);
            this.optionsContainer.appendChild(optionElement);
        });
    }
    
    createOptionElement(option, index) {
        const optionElement = document.createElement('div');
        optionElement.className = 'native-select-option';
        optionElement.setAttribute('role', 'option');
        optionElement.setAttribute('data-value', option.id);
        optionElement.setAttribute('data-index', index);
        optionElement.textContent = option.text;
        
        if (this.isSelected(option.id)) {
            optionElement.classList.add('selected');
        }
        
        optionElement.addEventListener('click', () => {
            this.selectOption(option);
        });
        
        optionElement.addEventListener('mouseenter', () => {
            this.focusOption(optionElement);
        });
        
        return optionElement;
    }
    
    selectOption(option) {
        if (this.options.multiple) {
            this.toggleSelection(option.id);
        } else {
            this.setSelection(option.id);
            this.close();
        }
        
        this.updateDisplay();
        this.updateOriginalSelect();
        this.triggerChange();
    }
    
    toggleSelection(value) {
        if (this.selectedOptions.has(value)) {
            this.selectedOptions.delete(value);
        } else {
            this.selectedOptions.add(value);
        }
    }
    
    setSelection(value) {
        this.selectedOptions.clear();
        this.selectedOptions.add(value);
    }
    
    clearSelection() {
        this.selectedOptions.clear();
        this.updateDisplay();
        this.updateOriginalSelect();
        this.triggerChange();
    }
    
    isSelected(value) {
        return this.selectedOptions.has(value);
    }
    
    updateDisplay() {
        if (this.selectedOptions.size === 0) {
            this.valueDisplay.textContent = this.options.placeholder;
            this.valueDisplay.classList.add('placeholder');
        } else if (this.options.multiple) {
            const selectedTexts = Array.from(this.selectedOptions).map(value => {
                const option = this.allOptions.find(opt => opt.id === value);
                return option ? option.text : value;
            });
            this.valueDisplay.textContent = selectedTexts.join(', ');
            this.valueDisplay.classList.remove('placeholder');
        } else {
            const selectedValue = Array.from(this.selectedOptions)[0];
            const option = this.allOptions.find(opt => opt.id === selectedValue);
            this.valueDisplay.textContent = option ? option.text : selectedValue;
            this.valueDisplay.classList.remove('placeholder');
        }
        
        if (this.clearButton) {
            this.clearButton.style.display = this.selectedOptions.size > 0 ? 'block' : 'none';
        }
    }
    
    updateOriginalSelect() {
        Array.from(this.element.options).forEach(option => {
            option.selected = false;
        });
        
        this.selectedOptions.forEach(value => {
            const option = this.element.querySelector(`option[value="${value}"]`);
            if (option) {
                option.selected = true;
            }
        });
    }
    
    triggerChange() {
        const event = new Event('change', { bubbles: true });
        this.element.dispatchEvent(event);
    }
    
    focusFirstOption() {
        const firstOption = this.optionsContainer.querySelector('.native-select-option');
        if (firstOption) {
            this.focusOption(firstOption);
        }
    }
    
    focusNextOption() {
        const focused = this.optionsContainer.querySelector('.native-select-option.focused');
        if (focused) {
            const next = focused.nextElementSibling;
            if (next && next.classList.contains('native-select-option')) {
                this.focusOption(next);
            }
        } else {
            this.focusFirstOption();
        }
    }
    
    focusPreviousOption() {
        const focused = this.optionsContainer.querySelector('.native-select-option.focused');
        if (focused) {
            const prev = focused.previousElementSibling;
            if (prev && prev.classList.contains('native-select-option')) {
                this.focusOption(prev);
            }
        }
    }
    
    focusOption(optionElement) {
        // Remove focus from all options
        this.optionsContainer.querySelectorAll('.native-select-option').forEach(opt => {
            opt.classList.remove('focused');
        });
        
        // Add focus to selected option
        optionElement.classList.add('focused');
        optionElement.scrollIntoView({ block: 'nearest' });
    }
    
    selectFocusedOption() {
        const focused = this.optionsContainer.querySelector('.native-select-option.focused');
        if (focused) {
            const value = focused.getAttribute('data-value');
            const option = this.allOptions.find(opt => opt.id === value);
            if (option) {
                this.selectOption(option);
            }
        }
    }
    
    showLoading() {
        this.loadingIndicator.style.display = 'block';
        this.optionsContainer.style.display = 'none';
        this.hideNoResults();
        this.hideEmptyList();
    }
    
    hideLoading() {
        this.loadingIndicator.style.display = 'none';
        this.optionsContainer.style.display = 'block';
    }
    
    showNoResults() {
        this.noResults.style.display = 'block';
        this.optionsContainer.style.display = 'none';
        this.hideLoading();
    }
    
    hideNoResults() {
        this.noResults.style.display = 'none';
        this.optionsContainer.style.display = 'block';
    }
    
    showEmptyList() {
        this.emptyList.style.display = 'block';
        this.optionsContainer.style.display = 'none';
        this.hideNoResults();
        this.hideLoading();
    }
    
    hideEmptyList() {
        this.emptyList.style.display = 'none';
        this.optionsContainer.style.display = 'block';
    }
    
    showError(message) {
        this.noResults.textContent = message;
        this.showNoResults();
    }
    
    // Public API methods
    destroy() {
        if (this.wrapper && this.wrapper.parentNode) {
            this.wrapper.parentNode.removeChild(this.wrapper);
        }
        this.element.style.display = '';
    }
    
    val(value) {
        if (value !== undefined) {
            if (this.options.multiple) {
                this.selectedOptions = new Set(Array.isArray(value) ? value : [value]);
            } else {
                this.selectedOptions = new Set([value]);
            }
            this.updateDisplay();
            this.updateOriginalSelect();
        } else {
            if (this.options.multiple) {
                return Array.from(this.selectedOptions);
            } else {
                return Array.from(this.selectedOptions)[0] || null;
            }
        }
    }
    
    trigger(eventType) {
        const event = new Event(eventType, { bubbles: true });
        this.element.dispatchEvent(event);
    }
}

// Auto-initialize selects with data-native-select attribute
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('select[data-native-select]').forEach(select => {
        const options = {
            placeholder: select.getAttribute('data-placeholder') || 'Selecione uma opção...',
            multiple: select.hasAttribute('multiple'),
            allowClear: select.hasAttribute('data-allow-clear'),
            ajax: select.getAttribute('data-ajax-url') ? {
                url: select.getAttribute('data-ajax-url'),
                params: {}
            } : null
        };
        
        new NativeSelect(select, options);
    });
});

if (typeof module !== 'undefined' && module.exports) {
    module.exports = NativeSelect;
}
