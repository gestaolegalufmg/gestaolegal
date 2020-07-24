
 var today = new Date();
  year = today.getFullYear();
  month = today.getMonth();
  day = today.getDate();
  var calendar = $('#myEvent').fullCalendar({
  height: 'auto',
    defaultView: 'month',
    editable: true,
    selectable: true,
    header: {
      left: 'prev,next today',
      center: 'title',
      right: 'month,agendaWeek,agendaDay,listMonth'
    },
    events: [{
      title: "John Marx",
      start: new Date(year, month, day, 11, 30),
      end: new Date(year, month, day, 12, 00),
      backgroundColor: "#46be76"
    }, {
      title: "Karlie Pearson",
      start: new Date(year, month, day + 16, 13, 30),
      end: new Date(year, month, day +16, 14, 00),
      backgroundColor: "#ffab03"
    }, {
      title: "Wiltor Stone",
      start: new Date(year, month, day + 14, 17, 30),
      end: new Date(year, month, day + 14, 18, 00),
      backgroundColor: "#f356d9"
    }, {
      title: "Jessica Hill",
      start: new Date(year, month, day, 22, 00),
      end: new Date(year, month, day, 22, 30),
      backgroundColor: "#0573f0"
    }, {
      title: "Nancy Burton",
      start: new Date(year, month, day + 5, 19, 00),
      end: new Date(year, month, day + 5, 19, 30),
      backgroundColor: "#46be76",
    }, {
      title: "Dorothy Hike",
      start: new Date(year, month, day + 19, 21, 00),
      end: new Date(year, month, day + 19, 21, 30),
      backgroundColor: "#0573f0",
    },{
      title: "Emma Wick",
      start: new Date(year, month, day + 10, 2, 30),
      end: new Date(year, month, day + 10, 3, 00),
      backgroundColor: "#9b59b6"
    }, {
      title: "Wiltor Stone",
      start: new Date(year, month, day + 8, 17, 30),
      end: new Date(year, month, day + 8, 18, 00),
      backgroundColor: "#f356d9"
    }, {
      title: "Sophia Martin",
      start: new Date(year, month, day + 5, 9, 30),
      end: new Date(year, month, day + 5, 10, 00),
      backgroundColor: "#ffab03"
    }]
  });
  
