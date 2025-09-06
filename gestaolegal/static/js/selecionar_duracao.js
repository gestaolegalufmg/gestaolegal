// Setup the calendar with the current date
var event_data = {"events":[]};
var datas_duracao = [];//TODAS as datas de duração do plantão

$(document).ready(function(){
    var date = new Date();
 
    // Set click handlers for DOM elements
    $(".right-button").click({date: date}, next_year);
    $(".left-button").click({date: date}, prev_year);
    $(".month").click({date: date}, month_click);

    // Set current month as active
    $(".months-row").children().eq(date.getMonth()).addClass("active-month");

    //Pega todas as datas que estao no banco e guarda no array
    get_datas_duracao().then(
        (_datas_duracao) => {
            datas_duracao = _datas_duracao;
            init_calendar(date);
        }
    );
});

$('#salva_configuracoes').click(function(){
    data_abertura = $('#data_abertura').val();
    hora_abertura = $('#hora_abertura').val();
    data_fechamento = $('#data_fechamento').val();
    hora_fechamento = $('#hora_fechamento').val();

    let compara_data_abertura = new Date(data_abertura.split('-')[0],data_abertura.split('-')[1],data_abertura.split('-')[2], hora_abertura.split(':')[0], hora_abertura.split(':')[1])
    let compara_data_fechamento = new Date(data_fechamento.split('-')[0],data_fechamento.split('-')[1],data_fechamento.split('-')[2], hora_fechamento.split(':')[0], hora_fechamento.split(':')[1])

    ajax_datas_duracao = []

    for(data of datas_duracao){
        ajax_datas_duracao.push(data.getDate() + "/" + (data.getMonth() + 1) + "/" + data.getFullYear())
    }

    if(compara_data_abertura > compara_data_fechamento){
        iziToast.error({
            title: "Erro!",
            message: "Data de abertura deve ocorrer antes da data de fechamento.",
            position: 'topCenter'
        });
    }
    else{
        $('.active-date').each(function(){
            let ano = $('.year').text();
            let mes = $('.active-month').text();
            let dia = $(this).text();
        });
        const csrftoken = $('meta[name=csrf-token]').attr('content')
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken)
                }
            }
        });
        $.ajax({
            type: "post",
            url: $('#hdnAjaxSalvaConfig').val(),
            contentType: 'application/json;charset=UTF-8',
            dataType: 'json',
            data: JSON.stringify({
                datas_duracao: ajax_datas_duracao,
                data_abertura: data_abertura,
                hora_abertura: hora_abertura,
                data_fechamento: data_fechamento,
                hora_fechamento: hora_fechamento
            }),
            success:(result) => {
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
    }
});

// Initialize the calendar by appending the HTML dates
function init_calendar(date) {
    $(".tbody").empty();
    $(".events-container").empty();
    var calendar_days = $(".tbody");
    var month = date.getMonth();
    var year = date.getFullYear();
    var day_count = days_in_month(month, year);
    var row = $("<tr class='table-row'></tr>");

    // Set date to 1 to find the first day of the month
    date.setDate(1);
    var first_day = date.getDay();
    // 35+firstDay is the number of date elements to be added to the dates table
    // 35 is from (7 days in a week) * (up to 5 rows of dates in a month)
    for(var i=0; i<35+first_day; i++) {
        // Since some of the elements will be blank, 
        // need to calculate actual date from index
        var day = i-first_day+1;
        // If it is a sunday, make a new row
        if(i%7===0) {
            calendar_days.append(row);
            row = $("<tr class='table-row'></tr>");
        }
        // if current index isn't a day in this month, make it blank
        if(i < first_day || day > day_count) {
            var curr_date = $("<td class='table-date nil'>"+"</td>");
            row.append(curr_date);
        }   
        else {
            var curr_date = $("<td class='table-date' id="+ day +">"+day+"</td>");

            // Set onClick handler for clicking a date
            curr_date.click({month: months[month], day:day}, date_click);
            row.append(curr_date);
        }
    }
    // Append the last row and set the current year
    calendar_days.append(row);
    $(".year").text(year);

    //marca os dias do mês atual, a partir do array já preenchido
    data = new Date(parseInt($('.year').text()), parseInt($('.active-month').attr('id').replace ( /[^\d.]/g, '' )), 1);

    for(data_duracao of datas_duracao){
        if((data_duracao.getMonth() == data.getMonth()) && (data_duracao.getFullYear() == data.getFullYear())){

            $("#" + data_duracao.getDate()).addClass("active-date");
        }
    }
}

// Get the number of days in a given month/year
function days_in_month(month, year) {
    var monthStart = new Date(year, month, 1);
    var monthEnd = new Date(year, month + 1, 1);
    return (monthEnd - monthStart) / (1000 * 60 * 60 * 24);    
}

// Event handler for when a date is clicked
function date_click(event) {
    $(this).toggleClass("active-date");

    data = new Date(parseInt($('.year').text()), parseInt($('.active-month').attr('id').replace ( /[^\d.]/g, '' )), parseInt($(this).text()));

    if($(this).hasClass("active-date"))
        datas_duracao.push(data);
    else   
        datas_duracao = datas_duracao.filter(function(value, index, arr){//remove a data que chamou este evento
            return (value.getDate() != data.getDate()) || (value.getMonth() != data.getMonth()) || (value.getFullYear() != data.getFullYear());
        });
};

// Event handler for when a month is clicked
function month_click(event) {
    $(".events-container").show(250);
    $("#dialog").hide(250);
    var date = event.data.date;
    $(".active-month").removeClass("active-month");
    $(this).addClass("active-month");
    var new_month = $(".month").index(this);
    date.setMonth(new_month);
    init_calendar(date);
}

// Event handler for when the year right-button is clicked
function next_year(event) {
    $("#dialog").hide(250);
    var date = event.data.date;
    var new_year = date.getFullYear()+1;
    $("year").html(new_year);
    date.setFullYear(new_year);
    init_calendar(date);
}

// Event handler for when the year left-button is clicked
function prev_year(event) {
    $("#dialog").hide(250);
    var date = event.data.date;
    var new_year = date.getFullYear()-1;
    $("year").html(new_year);
    date.setFullYear(new_year);
    init_calendar(date);
}

function get_datas_duracao(){  
    var date = new Date();
    mes = date.getMonth();
    

    return new Promise((resolve, reject) => {
        const csrftoken = $('meta[name=csrf-token]').attr('content')
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken)
                }
            }
        });

        $.ajax({
            url: $('#hdnAjaxDuracao').val(),
            type: 'POST',
            contentType: 'application/json;charset=UTF-8',
            dataType: 'json',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            success: function (result) {
              var dias_duracao = [];

              for(data of result){
                  tam = dias_duracao.push(new Date(data));//o novo objeto Date é gerado 1 dia anterior a data passada como parâmetro
                  dias_duracao[tam - 1].setDate(dias_duracao[tam - 1].getDate() + 1);//incremento no dia feito para esta data ser igual a passada como parâmetro
              }

              saida = ""
              for(data of dias_duracao){
                  saida = saida + data.getDate() + "/" + data.getMonth() + "/" + data.getFullYear() + "\n";
              }

              resolve(dias_duracao)
            },
            error: function (error) {
              reject(error)
            },
        })
    })
}

const months = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro"
];