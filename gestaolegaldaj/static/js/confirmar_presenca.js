$(document).ajaxStart(function() {
    $('#conteudoPagina').hide();
    $('#loadingGIF').show();
}).ajaxStop(function() {
    $('#loadingGIF').hide();
    $('#conteudoPagina').show();
});

$("#dataProcurada").change(function(){
    let nova_data = $("#dataProcurada").val();
    const tabela_presenca = $("#tabelaPresenca tbody");
    const tabela_plantao = $("#tabelaPlantao tbody");
    const conteudo_presenca = $("#conteudoPresenca");
    const conteudo_plantao = $("#conteudoPlantao");
    const sem_presenca = $("#semPresenca");
    const sem_plantao = $("#semPlantao");
    
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
        url: $("#hdnAjaxBuscaPresencasData").val(),
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        data: JSON.stringify({
            nova_data: nova_data
        }),
        success: (result) => {
            tabela_presenca.empty();
            tabela_plantao.empty();
            conteudo_presenca.hide();
            conteudo_plantao.hide();

            if(result.tem_presenca){
                conteudo_presenca.show();
                sem_presenca.hide();

                for(let i = 0; i < result.presencas.length; i++){
                        tabela_presenca.append(`
                        <tr>
                            <td>${result.presencas[i].Nome}</td>
                            <td>${result.presencas[i].Cargo}</td>
                            <td>${result.presencas[i].Entrada}</td>
                            <td>${result.presencas[i].Saida}</td>
                            <td>
                                <div class="col-lg-6 d-flex justify-content-center">
                                    <input class="confirmacao" type="radio" name="presenca_${result.presencas[i].IdPresenca}" value="confirmar">
                                </div>
                            </td>
                            <td>
                                <div class="col-lg-6 d-flex justify-content-center">
                                    <input class="confirmacao" type="radio" name="presenca_${result.presencas[i].IdPresenca}" value="divergencia">
                                </div>
                            </td>
                            <td>
                                <div class="col-lg-6 d-flex justify-content-center">
                                    <input class="confirmacao" type="radio" name="presenca_${result.presencas[i].IdPresenca}" value="ausencia">
                                </div>
                            </td>
                        </tr>
                        `);
                }
            }
            else{
                sem_presenca.show();
            }

            if(result.tem_plantao){
                sem_plantao.hide();
                conteudo_plantao.show();

                for(let i = 0; i < result.plantoes.length; i++){  
                    tabela_plantao.append(`
                    <tr>
                        <td>${result.plantoes[i].Nome}</td>
                        <td>${result.plantoes[i].Cargo}</td>
                        <td>
                            <div class="col-lg-6 d-flex justify-content-center">
                                <input class="confirmacao" type="radio" name="plantao_${result.plantoes[i].IdPlantao}" value="confirmar">
                            </div>
                        </td>
                        <td>
                            <div class="col-lg-6 d-flex justify-content-center">
                                <input class="confirmacao" type="radio" name="plantao_${result.plantoes[i].IdPlantao}" value="divergencia">
                            </div>
                        </td>
                        <td>
                            <div class="col-lg-6 d-flex justify-content-center">
                                <input class="confirmacao" type="radio" name="plantao_${result.plantoes[i].IdPlantao}" value="ausencia">
                            </div>
                        </td>
                    </tr>
                    `);
                }
            }
            else{
                sem_plantao.show();
            }
        }
    });
});