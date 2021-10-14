function deferir_caso(url) {
    $('#deferir_confirm').attr('href', url);
    $('#deferir').modal({
        show: true
    });
}

function indeferir_caso(url) {
    $('#indeferir_confirm').attr('href', url);
    $('#indeferir').modal({
        show: true
    });
}

function excluir_caso(url) {
    $('#excluir_confirm').attr('href', url);
    $('#excluir').modal({
        show: true
    });
}

