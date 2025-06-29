function validarPjConstituida() {
    var elemento_selecionado = document.getElementById("pj_constituida");
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].value;
    var div_cnpj = document.getElementById("div_cnpj");

    if (string_selecionada === "1") {
        div_cnpj.classList.remove("hidden");
        document.getElementById("formcnpj").required = true;
    } else {
        div_cnpj.classList.add("hidden");
        document.getElementById("formcnpj").required = false;
    }

    validarRepresLegal();
}

function validarRepresLegal() {
    var pj_constituida = document.getElementById('pj_constituida');
    var pj_constituida_opcao = pj_constituida.options[pj_constituida.selectedIndex].value;
    var div_repres_legal = document.getElementById("div_repres_legal");

    if (pj_constituida_opcao === "0") {
        div_repres_legal.classList.add("hidden");
        document.getElementById("repres_legal").required = false;
        document.getElementById("nome_repres_legal").required = false;
        document.getElementById("div_nome_repres_legal").classList.add("hidden");
        document.getElementById("div_cpf_repres_legal").classList.add("hidden");
        document.getElementById("div_contato_repres_legal").classList.add("hidden");
        document.getElementById("div_nascimento_repres_legal").classList.add("hidden");
        document.getElementById("div_rg_repres_legal").classList.add("hidden");
        return;
    }

    div_repres_legal.classList.remove("hidden");
    document.getElementById("repres_legal").required = true;

    var elemento_selecionado = document.getElementById('repres_legal');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].value;

    if (string_selecionada === "0") {
        document.getElementById("nome_repres_legal").required = true;
        document.getElementById("div_nome_repres_legal").classList.remove("hidden");
        document.getElementById("div_cpf_repres_legal").classList.remove("hidden");
        document.getElementById("div_contato_repres_legal").classList.remove("hidden");
        document.getElementById("div_nascimento_repres_legal").classList.remove("hidden");
        document.getElementById("div_rg_repres_legal").classList.remove("hidden");
    } else {
        document.getElementById("nome_repres_legal").required = false;
        document.getElementById("div_nome_repres_legal").classList.add("hidden");
        document.getElementById("div_cpf_repres_legal").classList.add("hidden");
        document.getElementById("div_contato_repres_legal").classList.add("hidden");
        document.getElementById("div_nascimento_repres_legal").classList.add("hidden");
        document.getElementById("div_rg_repres_legal").classList.add("hidden");
    }
}

function validarCampoComo_conheceu(orgaoPublicoDesc) {
    var elemento_selecionado = document.getElementById('como_conheceu');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (string_selecionada === orgaoPublicoDesc) {
        document.getElementById("div_indicacao_orgao").classList.remove("hidden");
        document.getElementById("indicacao_orgao").required = true;
    } else {
        document.getElementById("div_indicacao_orgao").classList.add("hidden");
        document.getElementById("indicacao_orgao").required = false;
    }
}

function validarCampoProcurou_outro_local() {
    var elemento_selecionado = document.getElementById('procurou_outro_local');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].value;
    var divElement = document.getElementById("div_procurou_qual_local");

    if (string_selecionada === "True") {
        divElement.classList.remove("hidden");
        document.getElementById("procurou_qual_local").required = true;
    } else {
        divElement.classList.add("hidden");
        document.getElementById("procurou_qual_local").required = false;
    }
}

function validarPretendeConstituirPj() {
    var pj_constituida = document.getElementById('pj_constituida');
    var pj_constituida_opcao = pj_constituida.options[pj_constituida.selectedIndex].value;

    if (pj_constituida_opcao === "0") {
        document.getElementById("div_pretende_constituir_pj").classList.remove("hidden");
        document.getElementById("pretende_constituir_pj").required = true;
    } else {
        document.getElementById("div_pretende_constituir_pj").classList.add("hidden");
        document.getElementById("pretende_constituir_pj").required = false;
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
