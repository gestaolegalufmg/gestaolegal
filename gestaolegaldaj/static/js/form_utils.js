function trataBotaoForm(idForm = 'form', idBotao = 'button'){
    document.getElementById(idForm).onsubmit= function() {document.getElementById(idBotao).disabled = true};
}