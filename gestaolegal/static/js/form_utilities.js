const applyMask = (element, pattern) => {
    if (!element) return;
    
    element.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        let maskedValue = '';
        let patternIndex = 0;
        
        for (let i = 0; i < pattern.length && patternIndex < value.length; i++) {
            if (pattern[i] === '0') {
                maskedValue += value[patternIndex];
                patternIndex++;
            } else {
                maskedValue += pattern[i];
            }
        }
        
        e.target.value = maskedValue;
    });
};

const applyMasks = (masks) => {
    masks.forEach(({ selector, pattern }) => {
        let elements = Array.from(document.querySelectorAll(selector));
        if (elements.length === 0 && selector.startsWith('#')) {
            const altSelector = `.${selector.slice(1)}`;
            elements = Array.from(document.querySelectorAll(altSelector));
        }
        elements.forEach((el) => applyMask(el, pattern));
    });
};

const trataBotaoForm = (idForm = 'form', idBotao = 'button') => {
    const form = document.getElementById(idForm);
    if (!form) return;
    form.addEventListener('submit', function(event) {
        const button = document.getElementById(idBotao);
        if (!button) return;
        setTimeout(() => {
            if (event.defaultPrevented) return;
            if (!form.checkValidity()) return;
            button.disabled = true;
            button.setAttribute('aria-busy', 'true');
        }, 0);
    });
};

const toggleFieldsVisibility = (triggerId, fieldsToToggle, condition) => {
    const trigger = document.getElementById(triggerId);
    if (!trigger) return;
    
    const updateVisibility = () => {
        const shouldShow = condition(trigger);
        
        fieldsToToggle.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                if (shouldShow) {
                    field.classList.remove('hidden-field');
                } else {
                    field.classList.add('hidden-field');
                }
                
                const input = field.querySelector('input, select, textarea');
                if (input) {
                    input.required = shouldShow;
                }
            }
        });
    };
    
    updateVisibility();
    trigger.addEventListener('change', updateVisibility);
    
    return updateVisibility;
};

const setupDateRangeValidation = (startDateId, endDateId) => {
    const startDate = document.getElementById(startDateId);
    const endDate = document.getElementById(endDateId);
    
    if (!startDate || !endDate) return;
    
    const updateEndDateMin = () => {
        if (startDate.value) {
            endDate.min = startDate.value;
        }
    };
    
    const updateStartDateMax = () => {
        if (endDate.value) {
            startDate.max = endDate.value;
        }
    };
    
    startDate.addEventListener('change', updateEndDateMin);
    endDate.addEventListener('change', updateStartDateMax);
};

const preventNumberInputWheel = () => {
    document.addEventListener("wheel", function (event) {
        if (document.activeElement.type === "number") {
            document.activeElement.blur();
        }
    });
};

const validateForm = (event) => {
    const form = event.target;
    let isValid = true;
    let firstInvalidField = null;

    console.log('Form validation started');

    const allElements = form.querySelectorAll('input, select, textarea');
    allElements.forEach(element => {
        element.classList.remove('is-invalid');
    });

    const elements = form.elements;

    for (let i = 0; i < elements.length; i++) {
        const element = elements[i];

        if (element.type === 'hidden' ||
            element.disabled ||
            element.style.display === 'none' ||
            element.closest('.hidden') ||
            element.closest('.hidden-field')) {
            continue;
        }

        if (element.required && (!element.value || element.value.trim() === '')) {
            console.log('Required field missing:', element.name, element.id, element.value);
            isValid = false;
            element.classList.add('is-invalid');

            if (!firstInvalidField) {
                firstInvalidField = element;
            }
        }
    }

    console.log('Form validation result:', isValid);

    if (!isValid) {
        event.preventDefault();
        console.log('Form submission prevented');
        if (firstInvalidField) {
            firstInvalidField.focus();
            firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return false;
    }

    console.log('Form validation passed, submitting...');
    return true;
};

const testaCPF = (strCPF) => {
    let soma;
    let resto;
    soma = 0;
    if (strCPF === "00000000000") return false;
     
    for (let i = 1; i <= 9; i++) soma = soma + parseInt(strCPF.substring(i-1, i)) * (11 - i);
    resto = (soma * 10) % 11;
   
    if ((resto === 10) || (resto == 11)) resto = 0;
    if (resto != parseInt(strCPF.substring(9, 10))) return false;
   
    soma = 0;
    for (let i = 1; i <= 10; i++) soma = soma + parseInt(strCPF.substring(i-1, i)) * (12 - i);
    resto = (soma * 10) % 11;
   
    if ((resto === 10) || (resto === 11)) resto = 0;
    if (resto != parseInt(strCPF.substring(10, 11))) return false;
    return true;
};

const validateDate = (inputText) => {
    const dateformat = /^(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[012])[\/\-]\d{4}$/;
    
    if (!inputText.value.match(dateformat)) {
        alert("Invalid date format!");
        inputText.focus();
        return false;
    }

    const opera1 = inputText.value.split('/');
    const opera2 = inputText.value.split('-');
    const lopera1 = opera1.length;
    const lopera2 = opera2.length;
    
    let pdate;
    if (lopera1 > 1) {
        pdate = inputText.value.split('/');
    } else if (lopera2 > 1) {
        pdate = inputText.value.split('-');
    }
    
    const dd = parseInt(pdate[0]);
    const mm = parseInt(pdate[1]);
    const yy = parseInt(pdate[2]);
    
    const listofDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    
    if (mm === 1 || mm > 2) {
        if (dd > listofDays[mm - 1]) {
            alert('Invalid date format!');
            return false;
        }
    }
    
    if (mm === 2) {
        let lyear = false;
        if ((!(yy % 4) && yy % 100) || !(yy % 400)) {
            lyear = true;
        }
        if ((lyear === false) && (dd >= 29)) {
            alert('Invalid date format!');
            return false;
        }
        if ((lyear === true) && (dd > 29)) {
            alert('Invalid date format!');
            return false;
        }
    }
    
    return true;
};

const toggleBolsistaFields = (bolsistaId, fieldsToToggle) => {
    const bolsista = document.getElementById(bolsistaId);
    if (!bolsista) return;
    
    const updateVisibility = () => {
        const isBolsista = bolsista.options[bolsista.selectedIndex].text === 'Sim';
        
        fieldsToToggle.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                if (isBolsista) {
                    field.classList.remove('hidden-field');
                } else {
                    field.classList.add('hidden-field');
                }
                
                const input = field.querySelector('input, select, textarea');
                if (input) {
                    input.required = isBolsista;
                }
            }
        });
    };
    
    updateVisibility();
    bolsista.addEventListener('change', updateVisibility);
    
    return updateVisibility;
};

const setupBolsistaDateRange = (startDateId, endDateId) => {
    const startDate = document.getElementById(startDateId);
    const endDate = document.getElementById(endDateId);
    
    if (!startDate || !endDate) return;
    
    const updateEndDateMin = () => {
        if (startDate.value) {
            endDate.min = startDate.value;
        }
    };
    
    const updateStartDateMax = () => {
        if (endDate.value) {
            startDate.max = endDate.value;
        }
    };
    
    startDate.addEventListener('change', updateEndDateMin);
    endDate.addEventListener('change', updateStartDateMax);
};

const initializeNativeSelect = (elementId, options = {}) => {
    const element = document.getElementById(elementId);
    if (!element || typeof NativeSelect === 'undefined') return null;
    
    const defaultOptions = {
        ajax: {
            url: '',
            delay: 500,
            params: {}
        },
        placeholder: 'Pesquisar...',
        allowClear: true,
        width: '100%'
    };
    
    const config = { ...defaultOptions, ...options };
    return new NativeSelect(element, config);
};

const getCSRFToken = () => {
    return typeof csrf_token !== 'undefined' ? csrf_token : '';
};

const setupAutoSubmit = (selectSelector) => {
    document.addEventListener('DOMContentLoaded', function() {
        const select = document.querySelector(selectSelector);
        if (select) {
            select.addEventListener('change', function() {
                this.form.submit();
            });
        }
    });
};

const initializeFormWithValidation = (config) => {
    const {
        formId = 'form',
        buttonId = 'button',
        masks = [],
        conditionalFields = [],
        dateRanges = [],
        bolsistaFields = [],
        nativeSelects = [],
        preventWheel = true,
        enableValidation = true
    } = config;
    
    initializeForm(config);
    
    initializeSemNumeroState();
    
    if (enableValidation) {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener('submit', validateForm);
            
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                const clearInvalid = function() {
                    this.classList.remove('is-invalid');
                };
                
                input.addEventListener('input', clearInvalid);
                input.addEventListener('change', clearInvalid);
            });
        }
    }
    
    bolsistaFields.forEach(({ bolsistaId, fieldsToToggle }) => {
        toggleBolsistaFields(bolsistaId, fieldsToToggle);
    });
    
    nativeSelects.forEach(({ elementId, options, targetFieldId }) => {
        const select = initializeNativeSelect(elementId, options);
        if (select && targetFieldId) {
            const element = document.getElementById(elementId);
            const targetField = document.getElementById(targetFieldId);
            if (element && targetField) {
                element.addEventListener('change', function() {
                    if (options.multiple) {
                        targetField.value = this.value.join(',');
                    } else {
                        targetField.value = this.value;
                    }
                });
            }
        }
    });
};

const initializeForm = (config) => {
    const {
        formId = 'form',
        buttonId = 'button',
        masks = [],
        conditionalFields = [],
        dateRanges = [],
        preventWheel = true
    } = config;
    
    trataBotaoForm(formId, buttonId);
    
    if (masks.length > 0) {
        applyMasks(masks);
    }
    
    conditionalFields.forEach(({ triggerId, fieldsToToggle, condition }) => {
        toggleFieldsVisibility(triggerId, fieldsToToggle, condition);
    });
    
    dateRanges.forEach(({ startDateId, endDateId }) => {
        setupDateRangeValidation(startDateId, endDateId);
    });
    
    if (preventWheel) {
        preventNumberInputWheel();
    }

    setupCepAutoFill();
    setupSemNumeroHandler();
    initializeSemNumeroState();
};

const setupCepAutoFill = () => {
    document.addEventListener(
        'blur',
        async (event) => {
            const target = event.target;
            if (!target || !target.matches || !target.matches('.formcep')) return;
            const cep = target.value.replace(/\D/g, '');
            if (cep.length !== 8) return;
            try {
                const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
                const data = await response.json();
                const form = target.form || document.getElementById('form') || document;
                const getField = (name) => (form.querySelector(`[name="${name}"]`) || document.querySelector(`[name="${name}"]`));
                if (data.erro) {
                    const fields = ['logradouro', 'bairro', 'cidade', 'estado'];
                    fields.forEach((f) => {
                        const el = getField(f);
                        if (el) el.value = '';
                    });
                    return;
                }
                const mappings = {
                    logradouro: data.logradouro || '',
                    bairro: data.bairro || '',
                    cidade: data.localidade || '',
                    estado: data.uf || ''
                };
                Object.entries(mappings).forEach(([name, value]) => {
                    const el = getField(name);
                    if (el) el.value = value;
                });
            } catch (error) {
                console.error('Erro ao buscar CEP:', error);
            }
        },
        true
    );
};

const setupSemNumeroHandler = () => {
    document.addEventListener(
        'change',
        (event) => {
            const target = event.target;
            if (!target || target.id !== 'sem_numero' || target.type !== 'checkbox') return;
            const form = target.form || document.getElementById('form') || document;
            const numeroField = form.querySelector('[name="numero"]');
            if (!numeroField) return;
            if (target.checked) {
                numeroField.setAttribute('readonly', true);
                numeroField.value = 'S/N';
            } else {
                numeroField.removeAttribute('readonly');
                if (numeroField.value === 'S/N') numeroField.value = '';
            }
        },
        true
    );
};

const initializeSemNumeroState = () => {
    const numeroField = document.querySelector('[name="numero"]');
    const semNumeroCheckbox = document.getElementById('sem_numero');
    
    if (numeroField && semNumeroCheckbox) {
        if (numeroField.value === 'S/N') {
            semNumeroCheckbox.checked = true;
            numeroField.setAttribute('readonly', true);
        }
    }
};

const MASK_PATTERNS = {
    CPF: '000.000.000-00',
    CNPJ: '00.000.000/0000-00',
    PHONE: '(00) 0000-0000',
    CELL_PHONE: '(00) 00000-0000',
    CEP: '00000-000'
};

const FIELD_SELECTORS = {
    CPF: '#formcpf',
    CNPJ: '#formcnpj',
    PHONE: '#formtel',
    CELL_PHONE: '#formcel',
    CEP: '#formcep'
};

window.FormUtils = {
    applyMask,
    applyMasks,
    trataBotaoForm,
    toggleFieldsVisibility,
    setupDateRangeValidation,
    setupBolsistaDateRange,
    preventNumberInputWheel,
    initializeForm,
    initializeFormWithValidation,
    validateForm,
    testaCPF,
    validateDate,
    toggleBolsistaFields,
    initializeNativeSelect,
    getCSRFToken,
    setupAutoSubmit,
    initializeSemNumeroState,
    MASK_PATTERNS,
    FIELD_SELECTORS,
    validateForm
};