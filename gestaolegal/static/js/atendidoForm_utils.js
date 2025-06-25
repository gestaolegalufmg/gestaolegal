function validarPjConstituida() {
    var elemento_selecionado = document.getElementById("pj_constituida");
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].value;
    var div_cnpj = document.getElementById("div_cnpj");

    if (string_selecionada === "1") {
        div_cnpj.style.display = "block";
        document.getElementById("formcnpj").required = true;
    } else {
        div_cnpj.style.display = "none";
        document.getElementById("formcnpj").required = false;
    }
    
    // Always call validarRepresLegal to handle representative legal field visibility
    validarRepresLegal();
}

function validarRepresLegal() {
    var pj_constituida = document.getElementById('pj_constituida');
    var pj_constituida_opcao = pj_constituida.options[pj_constituida.selectedIndex].value;
    var div_repres_legal = document.getElementById("div_repres_legal");
    
    // If no PJ constituted, hide all representative legal fields
    if (pj_constituida_opcao === "0") {
        div_repres_legal.style.display = "none";
        document.getElementById("repres_legal").required = false;
        document.getElementById("nome_repres_legal").required = false;
        document.getElementById("div_nome_repres_legal").style.display = "none";
        document.getElementById("div_cpf_repres_legal").style.display = "none";
        document.getElementById("div_contato_repres_legal").style.display = "none";
        document.getElementById("div_nascimento_repres_legal").style.display = "none";
        document.getElementById("div_rg_repres_legal").style.display = "none";
        return;
    }
    
    // If PJ is constituted, show the main representative legal field
    div_repres_legal.style.display = "block";
    document.getElementById("repres_legal").required = true;
    
    // Now check the representative legal value
    var elemento_selecionado = document.getElementById('repres_legal');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].value;

    // Only show detailed representative legal fields if atendido is NOT the representative
    if (string_selecionada === "0") {
        document.getElementById("nome_repres_legal").required = true;
        document.getElementById("div_nome_repres_legal").style.display = "block";
        document.getElementById("div_cpf_repres_legal").style.display = "block";
        document.getElementById("div_contato_repres_legal").style.display = "block";
        document.getElementById("div_nascimento_repres_legal").style.display = "block";
        document.getElementById("div_rg_repres_legal").style.display = "block";
    } else {
        document.getElementById("nome_repres_legal").required = false;
        document.getElementById("div_nome_repres_legal").style.display = "none";
        document.getElementById("div_cpf_repres_legal").style.display = "none";
        document.getElementById("div_contato_repres_legal").style.display = "none";
        document.getElementById("div_nascimento_repres_legal").style.display = "none";
        document.getElementById("div_rg_repres_legal").style.display = "none";
    }
}

function validarCampoComo_conheceu(orgaoPublicoDesc) {
    var elemento_selecionado = document.getElementById('como_conheceu');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (string_selecionada === orgaoPublicoDesc) {
        document.getElementById("div_indicacao_orgao").style.display = "block";
        document.getElementById("indicacao_orgao").required = true;
    } else {
        document.getElementById("div_indicacao_orgao").style.display = "none";
        document.getElementById("indicacao_orgao").required = false;
    }
}

function validarCampoProcurou_outro_local() {
    var elemento_selecionado = document.getElementById('procurou_outro_local');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].value;

    if (string_selecionada === "True") {
        document.getElementById("div_procurou_qual_local").style.display = "block";
        document.getElementById("procurou_qual_local").required = true;
    } else {
        document.getElementById("div_procurou_qual_local").style.display = "none";
        document.getElementById("procurou_qual_local").required = false;
    }
}

function validarPretendeConstituirPj() {
    var pj_constituida = document.getElementById('pj_constituida');
    var pj_constituida_opcao = pj_constituida.options[pj_constituida.selectedIndex].value;

    // Show "Pretende constituir PJ" field only when PJ is NOT constituted
    if (pj_constituida_opcao === "0") {
        document.getElementById("div_pretende_constituir_pj").style.display = "block";
        document.getElementById("pretende_constituir_pj").required = true;
    } else {
        document.getElementById("div_pretende_constituir_pj").style.display = "none";
        document.getElementById("pretende_constituir_pj").required = false;
    }
}

// Form validation function
function validateForm(event) {
    var form = event.target;
    var isValid = true;
    var firstInvalidField = null;

    // Get all form elements
    var elements = form.elements;

    // Check each element
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        
        // Skip hidden elements
        if (element.type === 'hidden' || element.style.display === 'none') {
            continue;
        }

        // Check if element is required and empty
        if (element.required && !element.value) {
            isValid = false;
            element.classList.add('is-invalid');
            
            // Store first invalid field for focus
            if (!firstInvalidField) {
                firstInvalidField = element;
            }
        } else {
            element.classList.remove('is-invalid');
        }
    }

    // If form is invalid, prevent submission and focus first invalid field
    if (!isValid) {
        event.preventDefault();
        if (firstInvalidField) {
            firstInvalidField.focus();
            firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return false;
    }

    return true;
}

// Add event listener for when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Get the form element
    var form = document.querySelector('form');
    if (form) {
        // Add submit event listener to the form
        form.addEventListener('submit', validateForm);
    }

    // Trigger validation for all conditional fields
    validarPjConstituida();
    validarRepresLegal();
    validarCampoComo_conheceu("Órgãos públicos");
    validarCampoProcurou_outro_local();
    validarPretendeConstituirPj();

    // Add change event listeners
    document.getElementById('pj_constituida').addEventListener('change', function() {
        validarPjConstituida();
        validarRepresLegal();
        validarPretendeConstituirPj();
    });

    document.getElementById('repres_legal').addEventListener('change', validarRepresLegal);
    document.getElementById('como_conheceu').addEventListener('change', function() {
        validarCampoComo_conheceu("Órgãos públicos");
    });
    document.getElementById('procurou_outro_local').addEventListener('change', validarCampoProcurou_outro_local);
    document.getElementById('pretende_constituir_pj').addEventListener('change', validarPretendeConstituirPj);

    // Add input event listeners to remove invalid class when user starts typing
    var inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(function(input) {
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
        });
    });
});