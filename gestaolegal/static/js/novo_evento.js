$(document).ready(function(){
    
    $('#usuario-js').select2({
        ajax: {
            url: $('#apiCasosBuscarUsuario').val(),
            dataType: 'json',
        },
        delay: 500,
        placeholder: 'Pesquisar usuários por nome',
        width: '100%',
        allowClear: true 
    })

    $('#usuario-js').on('change', function(){
        $('#usuario').val($('#usuario-js').val());
    });

})