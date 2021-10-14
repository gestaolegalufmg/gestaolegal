function validarCampoAreaDireito()  {
    let elemento_selecionado = document.getElementById('area_direito-js');
    let string_selecionada = elemento_selecionado.options[elemento_selecionado.selectedIndex].text;

    document.getElementById("div_sub_area").hidden = string_selecionada !== "Civel";
    document.getElementById("div_sub_area_admin").hidden = string_selecionada !== "Administrativo";
}