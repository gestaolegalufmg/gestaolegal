
function myChart(){
	
	var options = {
	          series: [{
	          name: 'Total Sales',
	          type: 'area',
	          data: [55, 31, 47, 31, 43, 26]
	        }, {
	          name: 'Total Purchase',
	          type: 'line',
	          data: [69, 45, 61, 43, 54, 37]
	        }],
	          chart: {
	          height: 300,
	          type: 'line',
	          toolbar : {
					show : false
				}
	        },
	        colors:['#57138f', '#e042f5'],
	        stroke: {
	          curve: 'smooth'
	        },
	        fill: {
	          type:'solid',
	          opacity: [0.35, 1],
	        },
	        labels: ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],
	        markers: {
	          size: 0
	        },
	        yaxis: [
	          {
	            title: {
	              text: 'Total Sales',
	            },
	          },
	          {
	            opposite: true,
	            title: {
	              text: 'Total Purchase',
	            },
	          },
	        ],
	        tooltip: {
	          shared: true,
	          intersect: false,
	          y: {
	            formatter: function (y) {
	              if(typeof y !== "undefined") {
	                return  y.toFixed(0) + " points";
	              }
	              return y;
	            }
	          }
	        }
	        };
	
	        var chart = new ApexCharts(document.querySelector("#myChart"), options);
	        chart.render();
}
myChart();

function myChart2(){
var ctx = document.getElementById("myChart2").getContext('2d');
var myChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    datasets: [{
      label: 'Statistics',
      data: [525, 447, 326, 452, 560, 510, 620, 526, 620, 423, 590, 650],
      borderWidth: 2,
      backgroundColor: 'rgba(3,243,254,.9)',
      borderColor: 'rgba(3,243,254,.9)',
      borderWidth: 2.5,
      pointBackgroundColor: '#ffffff',
      pointRadius: 4
    }, {
      label: 'Statistics',
      data: [422, 410, 380, 516, 600, 355, 490, 560, 630, 420, 600, 440],
      borderWidth: 2,
      backgroundColor: 'rgba(3,167,254,.9)',
      borderColor: 'transparent',
      borderWidth: 0,
      pointBackgroundColor: '#999',
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
          stepSize: 150,
          fontColor: "#9aa0ac", // Font Color
        }
      }],
      xAxes: [{
        gridLines: {
          display: false
        },
        ticks: {
          fontColor: "#9aa0ac", // Font Color
        }
      }]
    },
  }
});
}
myChart2();


function referral(){
	
	function generateData(baseval, count, yrange) {
	    var i = 0;
	    var series = [];
	    while (i < count) {
	      //var x =Math.floor(Math.random() * (750 - 1 + 1)) + 1;;
	      var y = Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;
	      var z = Math.floor(Math.random() * (75 - 15 + 1)) + 15;
	  
	      series.push([baseval, y, z]);
	      baseval += 86400000;
	      i++;
	    }
	    return series;
	  }
	var options = {
	          series: [{
	          name: 'Chrome',
	          data: generateData(new Date('27 April 2020 GMT').getTime(), 20, {
	            min: 10,
	            max: 60
	          })
	        },
	        {
	          name: 'Firefox',
	          data: generateData(new Date('27 April 2020 GMT').getTime(), 20, {
	            min: 10,
	            max: 60
	          })
	        },
	        {
	          name: 'Safari',
	          data: generateData(new Date('27 April 2020 GMT').getTime(), 20, {
	            min: 10,
	            max: 60
	          })
	        },
	        {
	          name: 'Opera',
	          data: generateData(new Date('27 April 2020 GMT').getTime(), 20, {
	            min: 10,
	            max: 60
	          })
	        }],
	          chart: {
	          height: 325,
	          type: 'bubble',
	          toolbar : {
					show : false
				}
	        },
	        colors:['#51bb25', '#26a0fc', '#7571f0', '#cf799b'],
	        dataLabels: {
	          enabled: false
	        },
	        fill: {
	          type: 'gradient',
	        },
	        xaxis: {
	          tickAmount: 12,
	          type: 'datetime',
	          labels: {
	              rotate: 0,
	          }
	        },
	        yaxis: {
	          max: 70
	        },
	        theme: {
	          palette: 'palette2'
	        },
	        legend : {
				 position: 'top'
			}
	        };

	        var chart = new ApexCharts(document.querySelector("#referral"), options);
	        chart.render();
	
}
referral();

function chart1(){
	
    var options = {
            series: [{
            name: 'Total Earning',
            data: [80, 60, 100, 80, 130, 100, 150]
          }],
            chart: {
            height: 150,
            type: 'area',
            toolbar : {
				show : false
			}
          },
          colors:['#26a0fc'],
          dataLabels: {
            enabled: false
          },
          stroke: {
	          curve: 'straight'
	        },
	        grid: {
	            show: false,
	            padding: {
	                top: 0,
	                right: 1,
	                bottom: 10,
	                left: 9
	            }
	        },
          xaxis: {
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
          },
          yaxis: {
	          show : false
	        }
          };

	        var chart = new ApexCharts(document.querySelector("#chart-1"), options);
	        chart.render();
	
}
chart1();

function chart2(){
	
	var options = {
            series: [{
            name: 'Total Earning',
            data: [80, 60, 100, 80, 130, 100, 150]
          }],
            chart: {
            height: 150,
            type: 'area',
            toolbar : {
				show : false
			}
          },
          colors:['#a96fff'],
          dataLabels: {
            enabled: false
          },
          stroke: {
            curve: 'straight'
          },
	        grid: {
	            show: false,
	            padding: {
	                top: 0,
	                right: 0,
	                bottom: 10,
	                left: 9
	            }
	        },
          xaxis: {
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
          },
          yaxis: {
	          show : false
	        }
          };

	        var chart = new ApexCharts(document.querySelector("#chart-2"), options);
	        chart.render();
	
}
chart2();

function chart3(){
	
    var options = {
            series: [{
            name: 'Total Earning',
            data: [80, 60, 100, 80, 130, 100, 150]
          }],
            chart: {
            height: 150,
            type: 'area',
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
	            show: false,
	            padding: {
	                top: 0,
	                right: 1,
	                bottom: 10,
	                left: 9
	            }
	        },
          xaxis: {
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
          },
          yaxis: {
	          show : false
	        }
          };

	        var chart = new ApexCharts(document.querySelector("#chart-3"), options);
	        chart.render();
	
}
chart3();

function donutChart(){
	
	var options = {
	          series: [{
	          data: [400, 430, 448, 470, 540, 580, 690, 1100, 1200, 1380]
	        }],
	          chart: {
	          type: 'bar',
	          height: 310,
	          toolbar : {
					show : false
				}
	        },
	        plotOptions: {
	          bar: {
	            barHeight: '100%',
	            distributed: true,
	            horizontal: true,
	            dataLabels: {
	              position: 'bottom'
	            },
	          }
	        },
	        colors: ['#33b2df', '#546E7A', '#d4526e', '#13d8aa', '#A5978B', '#2b908f', '#f9a3a4', '#90ee7e',
	          '#f48024', '#69d2e7'
	        ],
	        dataLabels: {
	          enabled: true,
	          textAnchor: 'start',
	          style: {
	            colors: ['#fff']
	          },
	          formatter: function (val, opt) {
	            return opt.w.globals.labels[opt.dataPointIndex] + ":  " + val
	          },
	          offsetX: 0,
	          dropShadow: {
	            enabled: true
	          }
	        },
	        stroke: {
	          width: 1,
	          colors: ['#fff']
	        },
	        xaxis: {
	          categories: ['South Korea', 'Canada', 'United Kingdom', 'Netherlands', 'Italy', 'France', 'Japan',
	            'United States', 'China', 'India'
	          ],
	        },
	        yaxis: {
	          labels: {
	            show: false
	          }
	        },
	        subtitle: {
	            text: 'Country wise visitors',
	            align: 'center',
	        },
	        tooltip: {
	          theme: 'dark',
	          x: {
	            show: false
	          },
	          y: {
	            title: {
	              formatter: function () {
	                return ''
	              }
	            }
	          }
	        }
	        };

	        var chart = new ApexCharts(document.querySelector("#donutChart"), options);
	        chart.render();
	
}
donutChart();
