function assistido_visibilidadePjConstituida(pj_constituida){

    if ((pj_constituida == '1') || (pj_constituida == 'Sim')){
        document.getElementById("campos_pj_constituida").hidden = false;
    }
    else{
        document.getElementById("campos_pj_constituida").hidden =true;
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

function visibilidadePessoaDoenteOBS(pessoa_doenteOutrosDesc){
    
    var elemento_selecionado = document.getElementById('pessoa_doente');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    var doenca_grave_familia = document.getElementById('doenca_grave_familia');
    var doenca_grave_familia_option = doenca_grave_familia.options[doenca_grave_familia.selectedIndex].text;

    if (!document.getElementById('div_pessoa_doente').hidden || !document.getElementById('div_doenca_grave_familia').hidden){
        if ((string_selecionada == pessoa_doenteOutrosDesc) && (doenca_grave_familia_option == "Sim")){
            document.getElementById("div_pessoa_doente_obs").hidden = false;
        }
        else{
            document.getElementById("div_pessoa_doente_obs").hidden =true;
        }
    }
}

function visibilidadeDoenca_grave_familia(pessoa_doenteOutrosDesc){

    visibilidadePessoaDoenteOBS(pessoa_doenteOutrosDesc)

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

function visibilidadeRecebe_beneficio(){
    var elemento_selecionado = document.getElementById('beneficio');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

        if (string_selecionada == "Outro"){
            document.getElementById("div_qual_beneficio").hidden = false;
        }
        else{
            document.getElementById("div_qual_beneficio").hidden =true;
        }
}

function visibilidadePossui_imoveis(){
    var elemento_selecionado = document.getElementById('possui_outros_imoveis');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

        if (string_selecionada == "Sim"){
            document.getElementById("div_quantos_imoveis").hidden = false;
        }
        else{
            document.getElementById("div_quantos_imoveis").hidden =true;
        }
}

visibilidadeSocios = () =>{
    const elementoSelecionado = document.getElementById('enquadramento')
    const stringSelecionada = elementoSelecionado.options[elementoSelecionado.selectedIndex].text

    if(stringSelecionada == "Microempreendedor Individual"){
        document.getElementById("div_socios").hidden = true
    }
    else{
        document.getElementById("div_socios").hidden = false
    }
}