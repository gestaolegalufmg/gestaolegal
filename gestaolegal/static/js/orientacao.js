function validarCampoAreaDireito() {
    var elemento_selecionado = document.getElementById('area_direito');
    var string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    if(string_selecionada == "Civel"){
        document.getElementById("div_sub_area").classList.remove('hidden-field');
    }
    else{
        document.getElementById("div_sub_area").classList.add('hidden-field');
    }
    
    if(string_selecionada == "Administrativo"){
        document.getElementById("div_sub_area_admin").classList.remove('hidden-field');
    }else{
        document.getElementById("div_sub_area_admin").classList.add('hidden-field');
    }
}