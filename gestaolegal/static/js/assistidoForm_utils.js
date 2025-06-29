function assistido_visibilidadePjConstituida(pj_constituida) {
    var campos_pj_constituida = document.getElementById("campos_pj_constituida");
    if (pj_constituida === "true") {
        campos_pj_constituida.classList.remove("hidden");
    } else {
        campos_pj_constituida.classList.add("hidden");
    }
}

function visibilidadeTem_funcionarios() {
    var elemento_selecionado = document.getElementById('tem_funcionarios');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (!document.getElementById('div_tem_funcionarios').classList.contains('hidden')) {
        if (string_selecionada == "Sim") {
            document.getElementById("div_qtd_funcionarios").classList.remove("hidden");
        }
        else {
            document.getElementById("div_qtd_funcionarios").classList.add("hidden");
        }
    }
}

function visibilidadeSede_bh() {
    var elemento_selecionado = document.getElementById('sede_bh');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (!document.getElementById('div_sede_bh').classList.contains('hidden')) {
        if (string_selecionada == "Sim") {
            document.getElementById("div_regiao_sede_bh").classList.remove("hidden");
            document.getElementById("div_regiao_sede_outros").classList.add("hidden");
        }
        else {
            document.getElementById("div_regiao_sede_bh").classList.add("hidden");
            document.getElementById("div_regiao_sede_outros").classList.remove("hidden");
        }
    }
}

function visibilidadePessoaDoenteOBS(pessoa_doenteOutrosDesc) {

    var elemento_selecionado = document.getElementById('pessoa_doente');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    var doenca_grave_familia = document.getElementById('doenca_grave_familia');
    var doenca_grave_familia_option = doenca_grave_familia.options[doenca_grave_familia.selectedIndex].text;

    if (!document.getElementById('div_pessoa_doente').classList.contains('hidden') ||
        !document.getElementById('div_doenca_grave_familia').classList.contains('hidden')) {
        if ((string_selecionada == pessoa_doenteOutrosDesc) && (doenca_grave_familia_option == "Sim")) {
            document.getElementById("div_pessoa_doente_obs").classList.remove("hidden");
        }
        else {
            document.getElementById("div_pessoa_doente_obs").classList.add("hidden");
        }
    }
}

function visibilidadeDoenca_grave_familia(pessoa_doenteOutrosDesc) {

    visibilidadePessoaDoenteOBS(pessoa_doenteOutrosDesc)

    var elemento_selecionado = document.getElementById('doenca_grave_familia');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (!document.getElementById('div_doenca_grave_familia').classList.contains('hidden')) {
        if (string_selecionada == "Sim") {
            document.getElementById("div_pessoa_doente").classList.remove("hidden");
            document.getElementById("div_gastos_medicacao").classList.remove("hidden");
        }
        else {
            document.getElementById("div_pessoa_doente").classList.add("hidden");
            document.getElementById("div_gastos_medicacao").classList.add("hidden");
        }
    }
}

function visibilidadePossui_veiculos() {
    var elemento_selecionado = document.getElementById('possui_veiculos');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (!document.getElementById('div_possui_veiculos').classList.contains('hidden')) {
        if (string_selecionada == "Sim") {
            document.getElementById("div_possui_veiculos_obs").classList.remove("hidden");
            document.getElementById("div_quantos_veiculos").classList.remove("hidden");
            document.getElementById("div_ano_veiculo").classList.remove("hidden");
        }
        else {
            document.getElementById("div_possui_veiculos_obs").classList.add("hidden");
            document.getElementById("div_quantos_veiculos").classList.add("hidden");
            document.getElementById("div_ano_veiculo").classList.add("hidden");
        }
    }
}

function visibilidadeRecebe_beneficio() {
    var elemento_selecionado = document.getElementById('beneficio');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (string_selecionada == "Outro") {
        document.getElementById("div_qual_beneficio").classList.remove("hidden");
    }
    else {
        document.getElementById("div_qual_beneficio").classList.add("hidden");
    }
}

function visibilidadePossui_imoveis() {
    var elemento_selecionado = document.getElementById('possui_outros_imoveis');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (string_selecionada == "Sim") {
        document.getElementById("div_quantos_imoveis").classList.remove("hidden");
    }
    else {
        document.getElementById("div_quantos_imoveis").classList.add("hidden");
    }
}

visibilidadeSocios = () => {
    const elementoSelecionado = document.getElementById('enquadramento');
    const stringSelecionada = elementoSelecionado.options[elementoSelecionado.selectedIndex].text;

    if (stringSelecionada == "Microempreendedor Individual") {
        document.getElementById("div_socios").classList.add("hidden");
    }
    else {
        document.getElementById("div_socios").classList.remove("hidden");
    }
}
