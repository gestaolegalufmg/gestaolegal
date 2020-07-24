"use strict";
var chartTextColor = '#96A2B4';

var draw = Chart.controllers.line.prototype.draw;
Chart.controllers.lineShadow = Chart.controllers.line.extend({
	draw : function() {
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

function monthlyEarningChart() {
	var options = {
	          series: [{
	          name: 'Income',
	          data: [60, 80, 70, 100, 60, 85, 65]
	        }, {
	          name: 'Expense',
	          data: [11, 32, 45, 32, 34, 52, 41]
	        }],
	          chart: {
	          height: 227,
	          type: 'area',
	          toolbar : {
					show : false
				}
	        },
	        dataLabels: {
	          enabled: false
	        },
	        stroke: {
	          curve: 'straight',
	          dashArray: [5,0]
	        },
	        colors: ['#00FFE8', '#B102FC'],
	        xaxis: {
	          type: 'line',
	          categories: ["January", "February", "March", "April", "May", "June", "July"]
	        },
	        legend : {
				 position: 'top'
			}
	        };

	        var chart = new ApexCharts(document.querySelector("#monthlyEarningChart"), options);
	        chart.render();
}
monthlyEarningChart();

function yearlyRevenueChart() {

	var options = {
		series : [ {
			name : 'Revenue',
			data : [ 87, 57, 74, 88, 75, 45, 69 ],
			labels : [ "thousands" ]
		}, {
			name : "Expense",
			data : [ 35, 41, 62, 42, 13, 18, 29 ],
			labels : [ "thousands" ]
		}, {
			name : 'Profit',
			data : [ 60, 47, 68, 74, 70, 36, 60 ],
			labels : [ "thousands" ]
		} ],
		xaxis : {
			categories : [ "2020", "2019", "2018", "2017", "2016", "2015","2014" ]
		},
		chart : {
			type : 'line',
			height : 227,
			toolbar : {
				show : false
			}
		},
		dataLabels : {
			enabled : false
		},
		markers : {
			hover : {
				sizeOffset : 4
			}
		},
		legend : {
			 position: 'top'
		}
	};

	var chart = new ApexCharts(document.querySelector("#yearlyRevenueChart"),options);
	chart.render();
	
}
yearlyRevenueChart();

function taskIssuesChart() {
	var chart = new ApexCharts(document.querySelector("#taskIssuesChart"), {
		series : [ 80, 45 ],
		chart : {
			height : 345,
			type : 'radialBar',
			foreColor : chartTextColor,
		},
		plotOptions : {
			radialBar : {
				dataLabels : {
					name : {
						fontSize : '22px',
					},
					value : {
						fontSize : '16px',
					},
					total : {
						show : true,
						label : 'Total',
						color : chartTextColor,
						formatter : function(w) {
							return 125
						}
					}
				}
			}
		},
		labels : [ 'Open', 'Close' ],
	});
	chart.render();
}
taskIssuesChart();

function chart1(){
	
	var options = {
	          series: [{
	          name: 'Cash Flow',
	          data: [13.07,
	            5.8,7.37, 8.1, 13.57, 15.75, 17.1, 19.8, -8.03, -16.4, -24.2, -32.3, -10.6, -30.6, -15.1, -20.6]
	        }],
	          chart: {
	          type: 'bar',
	          height: 200,
	          toolbar : {
					show : false
				}
	        },
	        plotOptions: {
	          bar: {
	            colors: {
	              ranges: [{
	                from: -100,
	                to: -46,
	                color: '#F15B46'
	              }, {
	                from: -45,
	                to: 0,
	                color: '#FEB019'
	              }]
	            },
	            columnWidth: '80%',
	          }
	        },
	        dataLabels: {
	          enabled: false,
	        },
	        grid: {
	            show: false
	        },
	        yaxis: {
	          show : false
	        },
	        xaxis : {
	        	show : false,
				position : 'bottom',
				labels : {
					offsetY : -1,
					show : false
				},
				axisBorder : {
					show : false
				},
				axisTicks : {
					show : false
				},
				tooltip : {
					enabled : false,
					offsetY : -35,

				}
			}
	        };
	
	        var chart = new ApexCharts(document.querySelector("#chart-1"), options);
	        chart.render();
	
}
chart1();

function chart2(){
	
	var chart = new ApexCharts(document.querySelector("#chart-2"), {
		chart : {
			height : 200,
			type : 'bar',
			foreColor : chartTextColor,
			toolbar : {
				show : false,
			}
		},
		colors : [ '#9C27B0', '#E91E63', '#9C27B0' ],
		fill : {
			colors : [ '#9a56ff', '#e36cd9', '#9C27B0' ]
		},
		plotOptions : {
			bar : {
				columnWidth : '40%',
				dataLabels : {
					position : 'top', // top, center, bottom
				},
			}
		},
		dataLabels : {
			enabled : true,
			formatter : function(val) {
				return val;
			},
			offsetY : -20,
			style : {
				fontSize : '12px',
				colors : [ "#e36cd9", "#e36cd9", "#e36cd9" ]
			}
		},
		series : [ {
			name : 'Sales',
			data : [ 30, 34, 51, 23, 45, 41, 22 ]
		} ],
		grid: {
            show: false
        },
        yaxis: {
          show : false
        },
        xaxis : {
        	show : false,
			position : 'bottom',
			labels : {
				offsetY : -1,
				show : false
			},
			axisBorder : {
				show : false
			},
			axisTicks : {
				show : false
			},

			tooltip : {
				enabled : false,
				offsetY : -35,

			}
		}

	});

	chart.render();
	
}
chart2();

function chart3(){
	
	var options = {
	          series: [{
	            name: "Desktops",
	            data: [10, 41, 35, 51, 49, 62, 69, 91, 148]
	        }],
	          chart: {
	          height: 200,
	          type: 'line',
	          zoom: {
	            enabled: false
	          },
	          toolbar : {
					show : false
				}
	        },
	        colors:['#c02976'],
	        dataLabels: {
	          enabled: false
	        },
	        stroke: {
	          curve: 'straight'
	        },
	        grid: {
	            show: false
	        },
	        yaxis: {
	          show : false
	        },
	        xaxis : {
	        	show : false,
				position : 'bottom',
				labels : {
					offsetY : -1,
					show : false
				},
				axisBorder : {
					show : false
				},
				axisTicks : {
					show : false
				},

				tooltip : {
					enabled : false,
					offsetY : -35,

				}
			}
	        };

	        var chart = new ApexCharts(document.querySelector("#chart-3"), options);
	        chart.render();
	
}
chart3();