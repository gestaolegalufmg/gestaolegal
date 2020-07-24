function visibilidadePJ(){
    var elemento_selecionado = document.getElementById('pj_constituida');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (!document.getElementById('pj_constituida').hidden){
        if (string_selecionada == "Sim"){
            document.getElementById("hidePJ").hidden = false;
        }
        else{
            document.getElementById("hidePJ").hidden =true;
        }
    }
}

function visibilidadeRepresLegal(){
    var elemento_selecionado = document.getElementById('repres_legal');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (!document.getElementById('repres_legal').hidden){
        if (string_selecionada == "Sim"){
            document.getElementById("hideRepresLegal").hidden = true;
        }
        else{
            document.getElementById("hideRepresLegal").hidden =false;
        }
    }
}


function visibilidadeTem_funcionarios(){
    var elemento_selecionado = document.getElementById('tem_funcionarios');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (!document.getElementById('div_tem_funcionarios').hidden){
        if (string_selecionada == "Sim"){
            document.getElementById("div_qtd_funcionarios").hidden = false;
        }
        else{
            document.getElementById("div_qtd_funcionarios").hidden =true;
        }
    }
}

function visibilidadeSede_bh(){
    var elemento_selecionado = document.getElementById('sede_bh');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (!document.getElementById('div_sede_bh').hidden){
        if (string_selecionada == "Sim"){
            document.getElementById("div_regiao_sede_bh").hidden = false;
            document.getElementById("div_regiao_sede_outros").hidden = true;
        }
        else{
            document.getElementById("div_regiao_sede_bh").hidden =true;
            document.getElementById("div_regiao_sede_outros").hidden =false;
        }
    }
}

function visibilidadeDoenca_grave_familia(){
    var elemento_selecionado = document.getElementById('doenca_grave_familia');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (!document.getElementById('div_doenca_grave_familia').hidden){
        if (string_selecionada == "Sim"){
            document.getElementById("div_pessoa_doente").hidden = false;
            document.getElementById("div_gastos_medicacao").hidden = false;
        }
        else{
            document.getElementById("div_pessoa_doente").hidden =true;
            document.getElementById("div_gastos_medicacao").hidden =true;
            document.getElementById("pessoa_doente_obs").hidden =true;

        }
    }
}

function visibilidadePessoaDoenteOBS(){
    var elemento_selecionado = document.getElementById('pessoa_doente');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (!document.getElementById('div_pessoa_doente').hidden){
        if (string_selecionada == "Outros"){
            document.getElementById("pessoa_doente_obs").hidden = false;
        }
        else{
            document.getElementById("pessoa_doente_obs").hidden =true;
        }
    }
}



function visibilidadePossui_veiculos(){
    var elemento_selecionado = document.getElementById('possui_veiculos');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if (!document.getElementById('div_possui_veiculos').hidden){
        if (string_selecionada == "Sim"){
            document.getElementById("div_possui_veiculos_obs").hidden = false;
            document.getElementById("div_quantos_veiculos").hidden = false;
            document.getElementById("div_ano_veiculo").hidden = false;
        }
        else{
            document.getElementById("div_possui_veiculos_obs").hidden =true;
            document.getElementById("div_quantos_veiculos").hidden =true;
            document.getElementById("div_ano_veiculo").hidden =true;
        }
    }
}

