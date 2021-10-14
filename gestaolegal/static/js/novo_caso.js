$(document).ready(function(){

    trocaLinkRoteiro();

    $('#clientes-js').select2({
        ajax: {
            url: $('#apiCasosBuscarAtendido').val(),
            dataType: 'json',
        },
        delay: 500,
        placeholder: 'Pesquisar clientes (nome, CPF ou CNPJ)',
        width: '100%'
    });

    $('#clientes-js').on('change', function(){
        $('#clientes').val($('#clientes-js').val().join(','));
    });

    $('#orientador-js').select2({
        ajax: {
            url: $('#apiCasosBuscarUsuario').val(),
            dataType: 'json',
        },
        delay: 500,
        placeholder: 'Pesquisar usuários por nome',
        width: '100%'
    });

    $('#orientador-js').on('change', function(){
        $('#orientador').val($('#orientador-js').val());
    });

    $('#area_direito-js').on('change',function(){
        trocaLinkRoteiro();
    });

    function trocaLinkRoteiro(){
        $.ajax({
            url: $('#apiCasosBuscarRoteiro').val(),
            data:{termo: $('#area_direito-js').val()}
          }).done(function(data) {
              if (data.link){
                $('#link-roteiro').attr('href', data.link);
                $('#link-roteiro').removeClass('disabled');
              }else{
                $('#link-roteiro').addClass('disabled');
              }
          });
    }
});