$("#registraPresenca").click(function(){
    const hora_registrada = $("#hora_registrada").val()
    const status_registro = $("#status_registro")

    const csrftoken = $('meta[name=csrf-token]').attr('content')

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    });

    $.ajax({
        type:'post',
        url: $("#hdnAjaxRegistraPresenca").val(),
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        data: JSON.stringify({
            hora_registrada: hora_registrada
        }),
        success: (result) => {
            status_registro.text(result.status)

            switch(result['tipo_mensagem']){
                case 'success':
                    iziToast.success({
                        title: 'Sucesso!',
                        message: result.mensagem,
                        position: 'topCenter'
                    });
                    break;
                case 'warning':
                    iziToast.warning({
                        title: 'Atenção:',
                        message: result.mensagem,
                        position: 'topCenter'
                    });
                    break;
            }
        }
    });
})