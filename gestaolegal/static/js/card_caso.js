function deferir_caso(url){
    $('#deferir_confirm').attr('href', url)
    
    $('#deferir').modal({
                show: true
            });
  }

function indeferir_caso(url){
    $('#indeferir_confirm').attr('href', url)
    
    $('#indeferir').modal({
                show: true
            });
  }