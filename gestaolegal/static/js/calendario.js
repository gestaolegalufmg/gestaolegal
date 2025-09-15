// Setup the calendar with the current date
var event_data = {"events":[]};

document.addEventListener('DOMContentLoaded', function(){
    fetch(window.origin + document.getElementById('hdnAjaxEscala').value, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json;charset=UTF-8'
        }
    })
    .then(response => response.json())
    .then(result => {
          event_data = {
            "events": result
          }

            var date = new Date();
            var today = date.getDate();
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
            document.getElementById("add-button").addEventListener('click', {date: date}, new_event);
            // Set current month as active
            const monthsRow = document.querySelector(".months-row");
            if (monthsRow && monthsRow.children[date.getMonth()]) {
                monthsRow.children[date.getMonth()].classList.add("active-month");
            }

            init_calendar(date);
            show_events(event_data.events, months[date.getMonth()], today);
        }
    })
    .catch(error => console.error('Error:', error));
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
    var today = date.getDate();
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
            curr_date.textContent = day;
            var events = check_events(day, month+1, year);
            if(today===day && document.querySelectorAll(".active-date").length===0) {
                curr_date.classList.add("active-date");
                show_events(events, months[month], day);
            }
            // If this date has any events, style it with .event-date
            if(events.length!==0) {
                curr_date.classList.add("event-date");
            }
            // Set onClick handler for clicking a date
            curr_date.addEventListener('click', {events: events, month: months[month], day:day}, date_click);
            row.appendChild(curr_date);
        }
    }
    // Append the last row and set the current year
    calendar_days.appendChild(row);
    document.querySelector('.year').textContent = year;
}

// Get the number of days in a given month/year
function days_in_month(month, year) {
    var monthStart = new Date(year, month, 1);
    var monthEnd = new Date(year, month + 1, 1);
    return (monthEnd - monthStart) / (1000 * 60 * 60 * 24);    
}

// Event handler for when a date is clicked
function date_click(event) {
    document.querySelector(".events-container").style.display = "block";
    document.getElementById("dialog").style.display = "none";
    document.querySelectorAll(".active-date").forEach(el => el.classList.remove("active-date"));
    event.target.classList.add("active-date");
    show_events(event.data.events, event.data.month, event.data.day);
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

// Event handler for clicking the new event button
function new_event(event) {
    // if a date isn't selected then do nothing
    if(document.querySelectorAll(".active-date").length===0)
        return;
    // remove red error input on click
    document.querySelectorAll("input").forEach(input => {
        input.addEventListener('click', function(){
            this.classList.remove("error-input");
        });
    });
    // empty inputs and hide events
    document.querySelectorAll("#dialog input[type=text]").forEach(input => input.value = '');
    document.querySelectorAll("#dialog input[type=number]").forEach(input => input.value = '');
    document.querySelector(".events-container").style.display = "none";
    document.getElementById("dialog").style.display = "block";
    // Event handler for cancel button
    document.getElementById("cancel-button").addEventListener('click', function() {
        document.getElementById("name").classList.remove("error-input");
        document.getElementById("count").classList.remove("error-input");
        document.getElementById("dialog").style.display = "none";
        document.querySelector(".events-container").style.display = "block";
    });
    // Event handler for ok button
    document.getElementById("ok-button").addEventListener('click', {date: event.data.date}, function(clickEvent) {
        var date = clickEvent.data.date;
        var name = document.getElementById("name").value.trim();
        var count = parseInt(document.getElementById("count").value.trim());
        var day = parseInt(document.querySelector(".active-date").textContent);
        // Basic form validation
        if(name.length === 0) {
            document.getElementById("name").classList.add("error-input");
        }
        else if(isNaN(count)) {
            document.getElementById("count").classList.add("error-input");
        }
        else {
            document.getElementById("dialog").style.display = "none";
            console.log("new event");
            new_event_json(name, count, date, day);
            date.setDate(day);
            init_calendar(date);
        }
    });
}

// Adds a json event to event_data
function new_event_json(name, count, date, day) {
    var event = {
        "occasion": name,
        "invited_count": count,
        "year": date.getFullYear(),
        "month": date.getMonth()+1,
        "day": day
    };
    event_data["events"].push(event);
}

// Display all events of the selected date in card views
function show_events(events, month, day) {
    // Clear the dates container
    const container = document.querySelector(".events-container");
    container.innerHTML = '';
    container.style.display = "block";
    // If there are no events for this date, notify the user
    if(events.length===0) {
        var event_card = document.createElement('div');
        event_card.className = 'card card-danger';
        event_card.innerHTML = `<div class="card-body"><li>Não há escalados para ${day} de ${month}.</li></div>`;
        container.appendChild(event_card);
    }
    else {
        // Go through and add each event as a card to the events container
        var event_card_top = document.createElement('div');
        event_card_top.className = 'card card-primary';
        event_card_top.innerHTML = '<div class="card-body"></div>';
        const cardBody = event_card_top.querySelector('.card-body');
        for(_event of events) {
            const li = document.createElement('li');
            li.className = 'data_plantao';
            li.textContent = _event.nome;
            cardBody.appendChild(li);
        }
        container.appendChild(event_card_top);
    }
}

// Checks if a specific date has any events
function check_events(day, month, year) {
    var events = [];
    for(var i=0; i<event_data["events"].length; i++) {
        var event = event_data["events"][i];
        if(event["day"]==day &&
            event["month"]==month &&
            event["year"]==year) {
                events.push(event);
            }
    }
    return events;
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