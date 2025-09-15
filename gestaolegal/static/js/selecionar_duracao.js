// Setup the calendar with the current date
var event_data = {"events":[]};
var datas_duracao = [];//TODAS as datas de duração do plantão

document.addEventListener('DOMContentLoaded', function(){
    var date = new Date();
 
    // Set click handlers for DOM elements
    document.querySelectorAll(".right-button").forEach(btn => {
        btn.addEventListener('click', {date: date}, next_year);
    });
    document.querySelectorAll(".left-button").forEach(btn => {
        btn.addEventListener('click', {date: date}, prev_year);
    });
    document.querySelectorAll(".month").forEach(btn => {
        btn.addEventListener('click', {date: date}, month_click);
    });

    // Set current month as active
    const monthsRow = document.querySelector(".months-row");
    if (monthsRow && monthsRow.children[date.getMonth()]) {
        monthsRow.children[date.getMonth()].classList.add("active-month");
    }

    //Pega todas as datas que estao no banco e guarda no array
    get_datas_duracao().then(
        (_datas_duracao) => {
            datas_duracao = _datas_duracao;
            init_calendar(date);
        }
    );
});

document.getElementById('salva_configuracoes').addEventListener('click', function(){
    data_abertura = document.getElementById('data_abertura').value;
    hora_abertura = document.getElementById('hora_abertura').value;
    data_fechamento = document.getElementById('data_fechamento').value;
    hora_fechamento = document.getElementById('hora_fechamento').value;

    let compara_data_abertura = new Date(data_abertura.split('-')[0],data_abertura.split('-')[1],data_abertura.split('-')[2], hora_abertura.split(':')[0], hora_abertura.split(':')[1])
    let compara_data_fechamento = new Date(data_fechamento.split('-')[0],data_fechamento.split('-')[1],data_fechamento.split('-')[2], hora_fechamento.split(':')[0], hora_fechamento.split(':')[1])

    ajax_datas_duracao = []

    for(data of datas_duracao){
        ajax_datas_duracao.push(data.getDate() + "/" + (data.getMonth() + 1) + "/" + data.getFullYear())
    }

    if(compara_data_abertura > compara_data_fechamento){
        showNotification("Erro!", "Data de abertura deve ocorrer antes da data de fechamento.", "danger");
    }
    else{
        document.querySelectorAll('.active-date').forEach(element => {
            let ano = document.querySelector('.year').textContent;
            let mes = document.querySelector('.active-month').textContent;
            let dia = element.textContent;
        });
        const csrftoken = document.querySelector('meta[name=csrf-token]').getAttribute('content');
        
        fetch(document.getElementById('hdnAjaxSalvaConfig').value, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=UTF-8',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                datas_duracao: ajax_datas_duracao,
                data_abertura: data_abertura,
                hora_abertura: hora_abertura,
                data_fechamento: data_fechamento,
                hora_fechamento: hora_fechamento
            })
        })
        .then(response => response.json())
        .then(result => {
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
    }
});

// Initialize the calendar by appending the HTML dates
function init_calendar(date) {
    document.querySelector('.tbody').innerHTML = '';
    document.querySelector('.events-container').innerHTML = '';
    var calendar_days = document.querySelector('.tbody');
    var month = date.getMonth();
    var year = date.getFullYear();
    var day_count = days_in_month(month, year);
    var row = document.createElement('tr');
    row.className = 'table-row';

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
            calendar_days.appendChild(row);
            row = document.createElement('tr');
            row.className = 'table-row';
        }
        // if current index isn't a day in this month, make it blank
        if(i < first_day || day > day_count) {
            var curr_date = document.createElement('td');
            curr_date.className = 'table-date nil';
            row.appendChild(curr_date);
        }   
        else {
            var curr_date = document.createElement('td');
            curr_date.className = 'table-date';
            curr_date.id = day;
            curr_date.textContent = day;

            // Set onClick handler for clicking a date
            curr_date.addEventListener('click', {month: months[month], day:day}, date_click);
            row.appendChild(curr_date);
        }
    }
    // Append the last row and set the current year
    calendar_days.appendChild(row);
    document.querySelector('.year').textContent = year;

    //marca os dias do mês atual, a partir do array já preenchido
    const yearElement = document.querySelector('.year');
    const activeMonthElement = document.querySelector('.active-month');
    if (yearElement && activeMonthElement) {
        data = new Date(parseInt(yearElement.textContent), parseInt(activeMonthElement.id.replace(/[^\d.]/g, '')), 1);

        for(data_duracao of datas_duracao){
            if((data_duracao.getMonth() == data.getMonth()) && (data_duracao.getFullYear() == data.getFullYear())){
                const dayElement = document.getElementById(data_duracao.getDate());
                if (dayElement) {
                    dayElement.classList.add("active-date");
                }
            }
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
    const clickedElement = event.target;
    clickedElement.classList.toggle("active-date");

    const yearElement = document.querySelector('.year');
    const activeMonthElement = document.querySelector('.active-month');
    if (yearElement && activeMonthElement) {
        data = new Date(parseInt(yearElement.textContent), parseInt(activeMonthElement.id.replace(/[^\d.]/g, '')), parseInt(clickedElement.textContent));

        if(clickedElement.classList.contains("active-date"))
            datas_duracao.push(data);
        else   
            datas_duracao = datas_duracao.filter(function(value, index, arr){//remove a data que chamou este evento
                return (value.getDate() != data.getDate()) || (value.getMonth() != data.getMonth()) || (value.getFullYear() != data.getFullYear());
            });
    }
};

// Event handler for when a month is clicked
function month_click(event) {
    document.querySelector(".events-container").style.display = "block";
    document.getElementById("dialog").style.display = "none";
    var date = event.data.date;
    document.querySelector(".active-month").classList.remove("active-month");
    event.target.classList.add("active-month");
    var monthElements = document.querySelectorAll(".month");
    var new_month = Array.from(monthElements).indexOf(event.target);
    date.setMonth(new_month);
    init_calendar(date);
}

// Event handler for when the year right-button is clicked
function next_year(event) {
    document.getElementById("dialog").style.display = "none";
    var date = event.data.date;
    var new_year = date.getFullYear()+1;
    document.querySelector(".year").textContent = new_year;
    date.setFullYear(new_year);
    init_calendar(date);
}

// Event handler for when the year left-button is clicked
function prev_year(event) {
    document.getElementById("dialog").style.display = "none";
    var date = event.data.date;
    var new_year = date.getFullYear()-1;
    document.querySelector(".year").textContent = new_year;
    date.setFullYear(new_year);
    init_calendar(date);
}

function get_datas_duracao(){  
    var date = new Date();
    mes = date.getMonth();
    

    return new Promise((resolve, reject) => {
        const csrftoken = document.querySelector('meta[name=csrf-token]').getAttribute('content');

        fetch(document.getElementById('hdnAjaxDuracao').value, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=UTF-8',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(result => {
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
        })
        .catch(error => {
              reject(error)
        });
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