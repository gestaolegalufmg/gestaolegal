function validarPjConstituida() {
    var elemento_selecionado = document.getElementById("pj_constituida");
    if (!elemento_selecionado) {
        console.warn("Element pj_constituida not found");
        return;
    }
    
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].value;
    var div_cnpj = document.getElementById("div_cnpj");
    var formcnpj = document.getElementById("formcnpj");

    if (div_cnpj) {
        if (string_selecionada === "1") {
            div_cnpj.classList.remove("hidden");
            if (formcnpj) formcnpj.required = true;
        } else {
            div_cnpj.classList.add("hidden");
            if (formcnpj) formcnpj.required = false;
        }
    }

    validarRepresLegal();
}

function validarRepresLegal() {
    var pj_constituida = document.getElementById('pj_constituida');
    if (!pj_constituida) {
        console.warn("Element pj_constituida not found in validarRepresLegal");
        return;
    }
    
    var pj_constituida_opcao = pj_constituida.options[pj_constituida.selectedIndex].value;
    var div_repres_legal = document.getElementById("div_repres_legal");

    if (pj_constituida_opcao === "0") {
        if (div_repres_legal) div_repres_legal.classList.add("hidden");
        
        var repres_legal = document.getElementById("repres_legal");
        if (repres_legal) repres_legal.required = false;
        
        var nome_repres_legal = document.getElementById("nome_repres_legal");
        if (nome_repres_legal) nome_repres_legal.required = false;
        
        var fields = ['div_nome_repres_legal', 'div_cpf_repres_legal', 'div_contato_repres_legal', 'div_nascimento_repres_legal', 'div_rg_repres_legal'];
        fields.forEach(function(fieldId) {
            var element = document.getElementById(fieldId);
            if (element) element.classList.add("hidden");
        });
        return;
    }

    if (div_repres_legal) div_repres_legal.classList.remove("hidden");
    
    var repres_legal = document.getElementById("repres_legal");
    if (repres_legal) repres_legal.required = true;

    var elemento_selecionado = document.getElementById('repres_legal');
    if (!elemento_selecionado) {
        console.warn("Element repres_legal not found");
        return;
    }
    
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].value;

    if (string_selecionada === "0") {
        var nome_repres_legal = document.getElementById("nome_repres_legal");
        if (nome_repres_legal) nome_repres_legal.required = true;
        
        var fields = ['div_nome_repres_legal', 'div_cpf_repres_legal', 'div_contato_repres_legal', 'div_nascimento_repres_legal', 'div_rg_repres_legal'];
        fields.forEach(function(fieldId) {
            var element = document.getElementById(fieldId);
            if (element) element.classList.remove("hidden");
        });
    } else {
        var nome_repres_legal = document.getElementById("nome_repres_legal");
        if (nome_repres_legal) nome_repres_legal.required = false;
        
        var fields = ['div_nome_repres_legal', 'div_cpf_repres_legal', 'div_contato_repres_legal', 'div_nascimento_repres_legal', 'div_rg_repres_legal'];
        fields.forEach(function(fieldId) {
            var element = document.getElementById(fieldId);
            if (element) element.classList.add("hidden");
        });
    }
}

function validarCampoComo_conheceu(orgaoPublicoDesc) {
    var elemento_selecionado = document.getElementById('como_conheceu');
    if (!elemento_selecionado) {
        console.warn("Element como_conheceu not found");
        return;
    }
    
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;
    var div_indicacao_orgao = document.getElementById("div_indicacao_orgao");
    var indicacao_orgao = document.getElementById("indicacao_orgao");

    if (div_indicacao_orgao) {
        if (string_selecionada === orgaoPublicoDesc) {
            div_indicacao_orgao.classList.remove("hidden");
            if (indicacao_orgao) indicacao_orgao.required = true;
        } else {
            div_indicacao_orgao.classList.add("hidden");
            if (indicacao_orgao) indicacao_orgao.required = false;
        }
    }
}

function validarCampoProcurou_outro_local() {
    var elemento_selecionado = document.getElementById('procurou_outro_local');
    if (!elemento_selecionado) {
        console.warn("Element procurou_outro_local not found");
        return;
    }
    
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].value;
    var divElement = document.getElementById("div_procurou_qual_local");
    var procurou_qual_local = document.getElementById("procurou_qual_local");

    if (divElement) {
        if (string_selecionada === "True") {
            divElement.classList.remove("hidden");
            if (procurou_qual_local) procurou_qual_local.required = true;
        } else {
            divElement.classList.add("hidden");
            if (procurou_qual_local) procurou_qual_local.required = false;
        }
    }
}

function validarPretendeConstituirPj() {
    var pj_constituida = document.getElementById('pj_constituida');
    if (!pj_constituida) {
        console.warn("Element pj_constituida not found in validarPretendeConstituirPj");
        return;
    }
    
    var pj_constituida_opcao = pj_constituida.options[pj_constituida.selectedIndex].value;
    var div_pretende_constituir_pj = document.getElementById("div_pretende_constituir_pj");
    var pretende_constituir_pj = document.getElementById("pretende_constituir_pj");

    if (div_pretende_constituir_pj) {
        if (pj_constituida_opcao === "0") {
            div_pretende_constituir_pj.classList.remove("hidden");
            if (pretende_constituir_pj) pretende_constituir_pj.required = true;
        } else {
            div_pretende_constituir_pj.classList.add("hidden");
            if (pretende_constituir_pj) pretende_constituir_pj.required = false;
        }
    }
}

function validateForm(event) {
    var form = event.target;
    var isValid = true;
    var firstInvalidField = null;

    var elements = form.elements;

    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];

        if (element.type === 'hidden' ||
            element.style.display === 'none' ||
            element.closest('.hidden')) {
            continue;
        }

        if (element.required && !element.value) {
            isValid = false;
            element.classList.add('is-invalid');

            if (!firstInvalidField) {
                firstInvalidField = element;
            }
        } else {
            element.classList.remove('is-invalid');
        }
    }

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

document.addEventListener('DOMContentLoaded', function () {
    var form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', validateForm);
    }

    validarPjConstituida();
    validarRepresLegal();
    validarCampoComo_conheceu("Órgãos públicos");
    validarCampoProcurou_outro_local();
    validarPretendeConstituirPj();

    document.getElementById('pj_constituida').addEventListener('change', function () {
        validarPjConstituida();
        validarRepresLegal();
        validarPretendeConstituirPj();
    });

    document.getElementById('repres_legal').addEventListener('change', validarRepresLegal);
    document.getElementById('como_conheceu').addEventListener('change', function () {
        validarCampoComo_conheceu("Órgãos públicos");
    });
    document.getElementById('procurou_outro_local').addEventListener('change', validarCampoProcurou_outro_local);
    document.getElementById('pretende_constituir_pj').addEventListener('change', validarPretendeConstituirPj);

    var inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(function (input) {
        input.addEventListener('input', function () {
            this.classList.remove('is-invalid');
        });
    });
});
