"use strict";
var chartTextColor = '#96A2B4';

if ($("#message-list").length) {
	$("#message-list").css({
		height : 400
	}).niceScroll();
}

/* chart shadow */
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

function monthlySalesChart() {
	var options = {
		chart : {
			height : 300,
			type : 'bar',
			foreColor : chartTextColor,
			stacked: true,
			toolbar : {
				show : false,
			}
		},
		colors:['#fab107', '#0775fa', '#9C27B0'],
		plotOptions : {
			bar : {
				horizontal : false,
				//endingShape : 'rounded',
				columnWidth : '55%',
			},
		},
		dataLabels : {
			enabled : false
		},
		stroke : {
			show : true,
			width : 2,
			colors : [ 'transparent' ]
		},
		series : [ {
			name : 'Net Profit',
			data : [ 44, 55, 57, 56, 61, 58, 63, 60, 66, 53, 57, 61 ]
		}, {
			name : 'Revenue',
			data : [ 76, 85, 99, 98, 87, 95, 91, 98, 94, 83, 93, 98 ]
		}, {
			name : 'Expense',
			data : [ 35, 41, 34, 26, 45, 38, 52, 38, 41, 30, 36, 37 ]
		} ],
		xaxis : {
			categories : [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
					'Aug', 'Sep', "Oct", "Nov", "Dec" ],

		},
		yaxis : {
			title : {
				text : '$ (thousands)'
			}
		},
		fill : {
			opacity : 1

		},
		tooltip : {
			y : {
				formatter : function(val) {
					return "$ " + val + " thousands"
				}
			}
		}
	}

	var chart = new ApexCharts(document.querySelector("#monthlySalesChart"), options);

	chart.render();

}

monthlySalesChart();

function yearlySalesChart() {
	var options = {
		chart : {
			height : 315,
			type : 'line',
			foreColor : chartTextColor,
			shadow : {
				enabled : false,
				color : '#bbb',
				top : 3,
				left : 2,
				blur : 3,
				opacity : 1
			},
			toolbar : {
				show : false,
			}
		},
		stroke : {
			width : 7,
			curve : 'smooth'
		},
		series : [ {
			name : 'revenue',
			data : [ 190, 243, 150, 301, 333, 230, 401, 346, 505, 618, 567 ]
		} ],
		xaxis : {
			type : 'year',
			categories : [ '2009', '2010', '2011', '2012', '2013', '2014',
					'2015', '2016', '2017', '2018', '2019', ],
		},

		fill : {
			type : 'gradient',
			gradient : {
				shade : 'dark',
				gradientToColors : [ '#f635fd' ],
				inverseColors: true,
				shadeIntensity : 1,
				type : 'horizontal',
				opacityFrom : 1,
				opacityTo : 1,
				stops: [50, 100],
			    colorStops: ["#b435fd","#fd5035"]
			},
		},
		markers : {
			size : 4,
			opacity : 0.9,
			colors : [ "#FFA41B" ],
			strokeColor : "#fff",
			strokeWidth : 2,

			hover : {
				size : 7,
			}
		},
		yaxis : {
			min : 0,
			max : 700,
			title : {
				text : '$ (thousands)',
			},
		}
	}

	var chart = new ApexCharts(document.querySelector("#yearlySalesChart"), options);

	chart.render();
}

yearlySalesChart();

function salesByCountriesChart() {
	var chart = document.getElementById('salesByCountriesChart');
	var barChart = echarts.init(chart);

	barChart.setOption({
		tooltip : {
			trigger : "item",
			formatter : "{a} <br/>{b} : {c} ({d}%)"
		},

		calculable : !0,
		series : [ {
			name : "Chart Data",
			type : "pie",
			radius : "55%",
			center : [ "50%", "48%" ],
			data : [ {
				value : 8500,
				name : "India"
			}, {
				value : 9500,
				name : "USA"
			}, {
				value : 1600,
				name : "Cambodia"
			}, {
				value : 6100,
				name : "Germany"
			} ]
		} ],
		color : [ '#575B7A', '#fc544b', '#ffc107', '#50A5D8' ]
	});
}

salesByCountriesChart();
