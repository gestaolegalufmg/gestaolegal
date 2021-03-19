$(document).ready(function(){
    
    $('#usuario-js').select2({
        ajax: {
            url: $('#apiCasosBuscarUsuario').val(),
            dataType: 'json',
        },
        delay: 500,
        placeholder: 'Pesquisar usuários por nome',
        width: '100%'
    })

    $('#usuario-js').on('change', function(){
        $('#usuarios').val($('#usuario-js').val());
    });

})