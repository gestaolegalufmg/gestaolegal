function validarPjConstituida() {

    var elemento_selecionado = document.getElementById('pj_constituida');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if(string_selecionada == "Sim"){
        document.getElementById("div_cnpj").hidden = false;
        document.getElementById("div_cnpj").required = true;
        document.getElementById("div_repres_legal").hidden = false;
        document.getElementById("div_repres_legal").required = true;
    }
    else{
     document.getElementById("div_cnpj").hidden = true;
     document.getElementById("div_cnpj").required = false;
     document.getElementById("div_repres_legal").hidden = true;
     document.getElementById("div_repres_legal").required = false;
    }
}


function validarRepresLegal() {

    var elemento_selecionado = document.getElementById('repres_legal');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if(string_selecionada == "Sim"){

        document.getElementById("nome_repres_legal").required = false;
        document.getElementById("div_nome_repres_legal").hidden = true;
        document.getElementById("div_cpf_repres_legal").hidden = true;
        document.getElementById("div_contato_repres_legal").hidden = true;
        document.getElementById("div_nascimento_repres_legal").hidden = true;
        document.getElementById("div_rg_repres_legal").hidden = true;

        
        
    }

    else{

        document.getElementById("nome_repres_legal").required = true;
        document.getElementById("div_nome_repres_legal").hidden = false;
        document.getElementById("div_cpf_repres_legal").hidden = false;
        document.getElementById("div_contato_repres_legal").hidden = false;
        document.getElementById("div_nascimento_repres_legal").hidden = false;
        document.getElementById("div_rg_repres_legal").hidden = false;
    
     
    }
}



function validarCampoComo_conheceu(orgaoPublicoDesc) {

    var elemento_selecionado = document.getElementById('como_conheceu');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if(string_selecionada == orgaoPublicoDesc){
        document.getElementById("div_indicacao_orgao").hidden = false;
        document.getElementById("div_indicacao_orgao").required = true;
    }
    else{
     document.getElementById("div_indicacao_orgao").hidden = true;
     document.getElementById("div_indicacao_orgao").required = false;
    }
}

function validarCampoProcurou_outro_local() {

    var elemento_selecionado = document.getElementById('procurou_outro_local');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if(string_selecionada == "Sim"){
        document.getElementById("div_procurou_qual_local").hidden = false;
        document.getElementById("div_procurou_qual_local").required = true;
    }
    else{
     document.getElementById("div_procurou_qual_local").hidden = true;
     document.getElementById("div_procurou_qual_local").required = false;
    }
}