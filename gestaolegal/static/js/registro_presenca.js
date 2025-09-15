document.getElementById('registraPresenca').addEventListener('click', function(){
    const hora_registrada = document.getElementById('hora_registrada').value;
    const status_registro = document.getElementById('status_registro');

    const csrftoken = document.querySelector('meta[name=csrf-token]').getAttribute('content');

    fetch(document.getElementById('hdnAjaxRegistraPresenca').value, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=UTF-8',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            hora_registrada: hora_registrada
        })
    })
    .then(response => response.json())
    .then(result => {
        status_registro.textContent = result.status;

        switch(result['tipo_mensagem']){
            case 'success':
                showNotification('Sucesso!', result.mensagem, 'success');
                break;
            case 'warning':
                showNotification('Atenção:', result.mensagem, 'warning');
                break;
        }
    })
    .catch(error => console.error('Error:', error));
});