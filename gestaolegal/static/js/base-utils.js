$(document).ready(function () {
    //Mostrar notificações na tela
    for (var elem of $('.flash-message')){
        var categoria = $(elem).data("category");
        switch (categoria){
            case 'info':
                iziToast.info({
                    title: 'Informe:',
                    message: $(elem).text(),
                    position: 'topCenter'
                });
                break;
            case 'success':
                iziToast.success({
                    title: 'Sucesso!',
                    message: $(elem).text(),
                    position: 'topCenter'
                });
                break;
            case 'warning':
                iziToast.warning({
                    title: 'Atenção:',
                    message: $(elem).text(),
                    position: 'topCenter'
                });
                break;
            case 'danger':
                iziToast.danger({
                    title: 'Erro:',
                    message: $(elem).text(),
                    position: 'topCenter'
                });
                break;
            default:
                iziToast.info({
                    title: 'Informe:',
                    message: $(elem).text(),
                    position: 'topCenter'
                });
        }
    }
});