function validarCampoBolsista() {

    var elemento_selecionado = document.getElementById('bolsista');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if(string_selecionada == 'Sim'){
        document.getElementById("div_tipo_bolsa").hidden = false;
        document.getElementById("div_inicio_bolsa").hidden = false;
        document.getElementById("div_fim_bolsa").hidden = false;
        document.getElementById("div_tipo_bolsa").required = true;
        document.getElementById("div_inicio_bolsa").required = true;
        document.getElementById("div_fim_bolsa").required = true;
    }
    else{
        document.getElementById("div_tipo_bolsa").hidden = true;
        document.getElementById("div_inicio_bolsa").hidden = true;
        document.getElementById("div_fim_bolsa").hidden = true;
        document.getElementById("div_tipo_bolsa").required = false;
        document.getElementById("div_inicio_bolsa").required = false;
        document.getElementById("div_fim_bolsa").required = false;
    }
}

const defineMinimoDataFinalBolsista = () =>{
    dataInicio = document.getElementById("inicio_bolsa").value
    document.getElementById("fim_bolsa").min = dataInicio
}
const defineMaximoDataInicialBolsista = () =>{
    dataFinal = document.getElementById("fim_bolsa").value
    document.getElementById("inicio_bolsa").max = dataFinal
}