"use strict";


var draw = Chart.controllers.line.prototype.draw;
Chart.controllers.lineShadow = Chart.controllers.line.extend({
    draw: function() {
        draw.apply(this, arguments);
        var ctx = this.chart.chart.ctx;
        var _stroke = ctx.stroke;
        ctx.stroke = function() {
            ctx.save();
            ctx.shadowColor = '#00000075';
            ctx.shadowBlur = 10;
            ctx.shadowOffsetX = 8;
            ctx.shadowOffsetY = 8;
            _stroke.apply(this, arguments)
            ctx.restore();
        }
    }
});

var ctx = document.getElementById("myChart").getContext('2d');
var myChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    datasets: [{
      label: 'Statistics',
      data: [300, 450, 320, 600, 150, 350, 200],
      borderWidth: 2,
      backgroundColor: 'rgba(155,126,212,.2)',
      borderColor: '#9B7ED4',
      borderWidth: 1,
      pointBackgroundColor: '#ffffff',
      pointRadius: 4
    }]
  },
  options: {
    legend: {
      display: false
    },
    scales: {
      yAxes: [{
        gridLines: {
          drawBorder: false,
          color: '#f2f2f2',
        },
        ticks: {
          beginAtZero: true,
          stepSize: 150
        }
      }],
      xAxes: [{
        ticks: {
          display: false
        },
        gridLines: {
          display: false
        }
      }]
    },
  }
});

var ctx = document.getElementById("myChart2").getContext('2d');
var myChart = new Chart(ctx, {
  type: 'horizontalBar',
  data: {
    labels: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    datasets: [{
      label: 'Statistics',
      data: [450, 450, 320, 532, 420, 650, 480],
      borderWidth: 1,
      backgroundColor: 'rgba(77,181,249,.2)',
      borderColor: '#4DB5F9',
      borderWidth: 1,
      pointBackgroundColor: '#ffffff',
      pointRadius: 4
    }]
  },
  options: {
    legend: {
      display: false
    },
    scales: {
      yAxes: [{
        gridLines: {
          drawBorder: false,
          color: '#f2f2f2',
        },
        ticks: {
          beginAtZero: true,
          stepSize: 150
        }
      }],
      xAxes: [{
        ticks: {
          display: false
        },
        gridLines: {
          display: false
        }
      }]
    },
  }
});

var ctx = document.getElementById("myChart3").getContext('2d');
var myChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    datasets: [{
      data: [
        70,
        60,
        30,
        20,
        10,
      ],
      backgroundColor: [
    	  'rgba(138,212,235)',
    	  'rgba(28,123,153)',
    	  'rgba(253,98,94)',
    	  'rgba(252,190,6)',
    	  'rgba(0,223,206)'
      ],
      borderColor: [
    	  '#ffffff',
    	  '#ffffff',
    	  '#ffffff',
    	  '#ffffff',
    	  '#ffffff',
      ],
      borderWidth: 1,
      label: 'Dataset 1'
    }],
  },
  options: {
    responsive: true,
    legend: {
      position: 'bottom',
    },
  }
});

var ctx = document.getElementById("myChart4").getContext('2d');
var myChart = new Chart(ctx, {
  type: 'pie',
  data: {
    datasets: [{
      data: [
        70,
        40,
        30,
        20,
        90,
      ],
      backgroundColor: [
    	  'rgba(138,212,235)',
    	  'rgba(28,123,153)',
    	  'rgba(253,98,94)',
    	  'rgba(252,190,6)',
    	  'rgba(0,223,206)'
      ],
      borderColor: [
    	  '#ffffff',
    	  '#ffffff',
    	  '#ffffff',
    	  '#ffffff',
    	  '#ffffff',
      ],
      borderWidth: 1,
      label: 'Dataset 1'
    }],
  },
  options: {
    responsive: true,
    legend: {
      position: 'bottom',
    },
  }
});

var ctx = document.getElementById("line-chart");
if (ctx) {
	ctx.height = 150;
	var myChart = new Chart(ctx, {
		type: 'lineShadow',
		data: {
			labels: ["2010", "2011", "2012", "2013", "2014", "2015", "2016"],
			type: 'line',
			defaultFontFamily: 'Poppins',
			datasets: [{
				label: "Foods",
				data: [0, 20, 10, 110, 60, 50, 60],
				backgroundColor: 'transparent',
				borderColor: '#FF7007',
				borderWidth: 2,
				pointStyle: 'circle',
				pointRadius: 3,
				pointBorderColor: 'transparent',
				pointBackgroundColor: '#FF7007',
			}, {
				label: "Electronics",
				data: [0, 55, 45, 85, 45, 70, 110],
				backgroundColor: 'transparent',
				borderColor: '#07FFFB',
				borderWidth: 2,
				pointStyle: 'circle',
				pointRadius: 3,
				pointBorderColor: 'transparent',
				pointBackgroundColor: '#07FFFB',
			}]
		},
		options: {
			responsive: true,
			tooltips: {
				mode: 'index',
				titleFontSize: 12,
				titleFontColor: '#000',
				bodyFontColor: '#000',
				backgroundColor: '#fff',
				titleFontFamily: 'Poppins',
				bodyFontFamily: 'Poppins',
				cornerRadius: 3,
				intersect: false,
			},
			legend: {
				display: false,
				labels: {
					usePointStyle: true,
					fontFamily: 'Poppins',
				},
			},
			scales: {
				xAxes: [{
					display: true,
					gridLines: {
						display: false,
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'Month'
					},
					ticks: {
						fontFamily: "Poppins"
					}
				}],
				yAxes: [{
					display: true,
					gridLines: {
						display: false,
						drawBorder: false
					},
					scaleLabel: {
						display: true,
						labelString: 'Value',
						fontFamily: "Poppins"

					},
					ticks: {
						fontFamily: "Poppins"
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});
}


var ctx = document.getElementById("lineChartFill");
if (ctx) {
	ctx.height = 150;
	var myChart = new Chart(ctx, {
		type: 'line',
		data: {
			labels: ["January", "February", "March", "April", "May", "June", "July"],
			datasets: [
				{
					label: "My First dataset",
					borderColor: "rgba(7,33,255)",
					borderWidth: "1",
					backgroundColor: "rgba(7,33,255,.1)",
					data: [23, 45, 68, 44, 77, 46, 13]
				},
				{
					label: "My Second dataset",
					borderColor: "rgba(255,7,240, 0.9)",
					borderWidth: "1",
					backgroundColor: "rgba(255, 7, 240, 0.5)",
					pointHighlightStroke: "rgba(65, 149, 250,,1)",
					data: [17, 33, 19, 27, 43, 34, 45]
				}
			]
		},
		options: {
			legend: {
				position: 'top',
				labels: {
				}

			},
			responsive: true,
			tooltips: {
				mode: 'index',
				intersect: false
			},
			hover: {
				mode: 'nearest',
				intersect: true
			},
			scales: {
				xAxes: [{
					ticks: {

					}
				}],
				yAxes: [{
					ticks: {
						beginAtZero: true,
					}
				}]
			}

		}
	});
}

//radar chart
var ctx = document.getElementById("radar-chart");
if (ctx) {
	ctx.height = 200;
	var myChart = new Chart(ctx, {
		type: 'radar',
		data: {
			labels: [["Eating", "Dinner"], ["Drinking", "Water"], "Sleeping", ["Designing", "Graphics"], "Coding", "Cycling", "Running"],
			datasets: [
				{
					label: "My First dataset",
					data: [66, 58, 65, 44, 55, 54, 41],
					borderColor: "rgba(0, 123, 255, 0.6)",
					borderWidth: "1",
					backgroundColor: "rgba(255, 197, 0,0.5)"
				},
				{
					label: "My Second dataset",
					data: [29, 13, 41, 18, 62, 26, 88],
					borderColor: "rgba(0, 123, 255, 0.7",
					borderWidth: "1",
					backgroundColor: "rgba(232, 0, 255,0.5)"
				}
			]
		},
		options: {
			legend: {
				position: 'top',
				labels: {
				}

			},
			scale: {
				ticks: {
					beginAtZero: true,
				}
			}
		}
	});
}

var ctx = document.getElementById("polar-chart");
if (ctx) {
	ctx.height = 200;
	var myChart = new Chart(ctx, {
		type: 'polarArea',
		data: {
			datasets: [{
				data: [14, 17, 12, 9, 22],
				backgroundColor: [
					"rgba(255, 197, 0,0.9)",
					"rgba(232, 0, 255,0.8)",
					"rgba(236, 255, 0,0.7)",
					"rgba(255,0,178,0.2)",
					"rgba(255, 135, 0,0.5)"
				]

			}],
			labels: [
				"A",
				"B",
				"C",
				"D"
			]
		},
		options: {
			legend: {
				position: 'top',
				labels: {
					fontFamily: 'Poppins'
				}

			},
			responsive: true
		}
	});
}

var ctx = document.getElementById('line-chart3').getContext("2d");


var gradientStroke = ctx.createLinearGradient(500, 0, 0, 0);
gradientStroke.addColorStop(0, 'rgba(255, 0, 240, 1)');
gradientStroke.addColorStop(1, 'rgba(255, 0, 0, 1)');


var myChart = new Chart(ctx, {
type: 'lineShadow',
data: {
	labels: ["2010", "2011", "2012", "2013", "2014", "2015", "2016"],
	type: 'line',
	defaultFontFamily: 'Poppins',
	datasets: [{
		label: "Foods",
		data: [0, 35, 15, 125, 55, 65, 15],
		borderColor: gradientStroke,
        pointBorderColor: gradientStroke,
        pointBackgroundColor: gradientStroke,
        pointHoverBackgroundColor: gradientStroke,
        pointHoverBorderColor: gradientStroke,
        pointBorderWidth: 10,
        pointHoverRadius: 10,
        pointHoverBorderWidth: 1,
        pointRadius: 1,
        fill: false,
        borderWidth: 4,

	}, {
		label: "Electronics",
		data: [0, 55, 45, 85, 45, 70, 110],
		borderColor: gradientStroke,
        pointBorderColor: gradientStroke,
        pointBackgroundColor: gradientStroke,
        pointHoverBackgroundColor: gradientStroke,
        pointHoverBorderColor: gradientStroke,
        pointBorderWidth: 10,
        pointHoverRadius: 10,
        pointHoverBorderWidth: 1,
        pointRadius: 1,
        fill: false,
        borderWidth: 4,
	}]
},
options: {          
    legend: {
        position: "bottom"
    },
    tooltips: {
		mode: 'index',
		titleFontSize: 12,
		titleFontColor: '#fff',
		bodyFontColor: '#fff',
		backgroundColor: '#000',
		titleFontFamily: 'Poppins',
		bodyFontFamily: 'Poppins',
		cornerRadius: 3,
		intersect: false,
	},
    scales: {
        yAxes: [{
            ticks: {
                fontColor: "rgba(0,0,0,0.5)",
                fontStyle: "bold",
                beginAtZero: true,
                maxTicksLimit: 5,
                padding: 20
            },
            gridLines: {
                drawTicks: false,
                display: false
            }

        }],
        xAxes: [{
            gridLines: {
                zeroLineColor: "transparent"
            },
            ticks: {
                padding: 20,
                fontColor: "rgba(0,0,0,0.5)",
                fontStyle: "bold"
            }
        }]
    }
}
});

var ctx = document.getElementById('line-chart4').getContext("2d");

var gradientStroke = ctx.createLinearGradient(0,0,700,0);
gradientStroke.addColorStop(0, 'rgba(255, 0, 0, 1)');   
gradientStroke.addColorStop(0.5, 'rgba(255, 152, 0, 1)');
gradientStroke.addColorStop(1, 'rgba(0, 255, 61, 1)');

var myChart = new Chart(ctx, {
type: 'lineShadow',
data: {
	labels: ["2010", "2011", "2012", "2013", "2014", "2015", "2016"],
	type: 'line',
	defaultFontFamily: 'Poppins',
	datasets: [{
		label: "Foods",
		data: [0, 35, 15, 125, 55, 65, 15],
		 borderColor: gradientStroke,
	        pointBorderColor: gradientStroke,
	        pointBackgroundColor: gradientStroke,
	       pointHoverBackgroundColor: gradientStroke,
	        pointHoverBorderColor: gradientStroke,
	        pointBorderWidth: 10,
	        pointHoverRadius: 10,
	        pointHoverBorderWidth: 1,
	        pointRadius: 0,
	        fill: false,
	        borderWidth: 4,
	}, {
		label: "Electronics",
		data: [0, 55, 45, 85, 45, 75, 125],
		 borderColor: gradientStroke,
	        pointBorderColor: gradientStroke,
	        pointBackgroundColor: gradientStroke,
	       pointHoverBackgroundColor: gradientStroke,
	        pointHoverBorderColor: gradientStroke,
	        pointBorderWidth: 10,
	        pointHoverRadius: 10,
	        pointHoverBorderWidth: 1,
	        pointRadius: 0,
	        fill: false,
	        borderWidth: 4,
	}]
},


options: {          
    legend: {
        position: "bottom"
    },
    scales: {
        yAxes: [{
            ticks: {
                fontColor: "rgba(0,0,0,0.5)",
                fontStyle: "bold",
                beginAtZero: true,
                maxTicksLimit: 5,
                padding: 20
            },
            gridLines: {
                drawTicks: false,
                display: false
            }

        }],
        xAxes: [{
            gridLines: {
                zeroLineColor: "transparent"
            },
            ticks: {
                padding: 20,
                fontColor: "rgba(0,0,0,0.5)",
                fontStyle: "bold"
            }
        }]
    }
}
});