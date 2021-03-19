'use strict';
var chartTextColor= '#96A2B4';
$(function () {
    chart1();
    chart2();
    chart3();
    chart4();
    chart5();
    chart6();
    chart7();
    chart8();
});

function chart1(){
	 var options = {
			
            chart: {
                height: 350,
                type: 'bar',
                foreColor: chartTextColor,
                toolbar : {
					show : true
				}
            },
            plotOptions: {
                bar: {
                    horizontal: true,
                    endingShape: 'rounded',
                    columnWidth: '55%',
                },
            },
            dataLabels: {
                enabled: false
            },
            stroke: {
                show: true,
                width: 2,
                colors: ['transparent']
            },
            colors: ['#D24BFA','#FA4BBD','#6CCBF8'],
            series: [{
                name: 'Net Profit',
                data: [40, 50, 55, 60, 60, 51, 69, 62, 67]
            }, {
                name: 'Revenue',
                data: [70, 80, 100, 90, 80, 110, 90, 120, 100]
            }, {
                name: 'Free Cash Flow',
                data: [30, 40, 30, 20, 40, 40, 50, 50, 40]
            }],
            xaxis: {
                categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
                
            },
            yaxis: {
                title: {
                    text: '$ (thousands)'
                }
            },
            fill: {
                opacity: 1

            },
            tooltip: {
                y: {
                    formatter: function (val) {
                        return "$ " + val + " thousands"
                    }
                }
            },
            
        }

        var chart = new ApexCharts(
            document.querySelector("#chart1"),
            options
        );

        chart.render();
}
function chart2(){

	 var options = {
	          series: [{
	          data: [54, 65, 51, 74, 32, 53, 31]
	        }, {
	          data: [63, 42, 43, 62, 23, 54, 42]
	        }],
	          chart: {
	          type: 'bar',
	          height: 350,
	          toolbar : {
					show : true
				}
	        },
	        colors: ['#FED700','#B6FF02'],
	        plotOptions: {
	          bar: {
	            horizontal: false,
	            dataLabels: {
	              position: 'top',
	            },
	          }
	        },
	        dataLabels: {
	          enabled: true,
	          offsetX: 0,
	          style: {
	            fontSize: '12px',
	            colors: ['#fff']
	          }
	        },
	        stroke: {
	          show: true,
	          width: 1,
	          colors: ['#fff']
	        },
	        xaxis: {
	          categories: [2013, 2014, 2015, 2016, 2017, 2018, 2019],
	        },
	        };

        var chart = new ApexCharts(
            document.querySelector("#chart2"),
            options
        );

        chart.render();
    
    }
function chart3(){
	
	 var options = {
            chart: {
                height: 350,
                type: 'line',
                foreColor: chartTextColor,
                shadow: {
                    enabled: true,
                    color: '#000',
                    top: 18,
                    left: 7,
                    blur: 10,
                    opacity: 1
                },
                toolbar: {
                    show: true
                }
            },
            colors: ['#FE9703', '#03A6FE'],
            dataLabels: {
                enabled: true,
            },
            stroke: {
                curve: 'smooth',
                dashArray: [5,0]
            },
            series: [{
                    name: "High - 2013",
                    data: [25, 20, 15, 40, 35, 20, 25]
                },
                {
                    name: "Low - 2013",
                    data: [15, 25, 30, 15, 25, 25, 15]
                }
            ],
            title: {
                text: 'Average High & Low Temperature',
                align: 'left'
            },
            grid: {
                borderColor: '#e7e7e7',
                row: {
                    colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
                    opacity: 0.5
                },
            },
            markers: {
                
                size: 6
            },
            xaxis: {
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                title: {
                    text: 'Month'
                }
            },
            yaxis: {
                title: {
                    text: 'Temperature'
                },
                min: 5,
                max: 40
            },
            legend: {
                position: 'bottom'
            }
        }

        var chart = new ApexCharts(
            document.querySelector("#chart3"),
            options
        );

        chart.render();
}
function chart4(){

	var options = {
	          series: [{
	          data: [24, 34, 44, 11, 8, 33, 23, 13, 56, 56, 48]
	        }],
	          chart: {
	          type: 'line',
	          height: 350
	        },
	        stroke: {
	          curve: 'stepline',
	        },
	        dataLabels: {
	          enabled: false
	        },
	        title: {
	          text: 'Stepline Chart',
	          align: 'left'
	        },
	        markers: {
	          hover: {
	            sizeOffset: 4
	          }
	        }
	        };
	
       var chart = new ApexCharts(
            document.querySelector("#chart4"),
            options
        );
        
        chart.render();
}
function chart5(){
	var options = {
	          series: [{
	          name: 'Income',
	          type: 'column',
	          data: [2, 2.5, 1.5, 2.5, 2.8, 3.8, 4.6]
	        }, {
	          name: 'Cashflow',
	          type: 'column',
	          data: [3, 3.1, 4, 4.1, 4.9, 6.5, 8.5]
	        }, {
	          name: 'Revenue',
	          type: 'line',
	          data: [29, 37, 36, 44, 45, 50, 58]
	        }],
	          chart: {
	          height: 350,
	          type: 'line',
	          stacked: false
	        },
	        dataLabels: {
	          enabled: false
	        },
	        stroke: {
	          width: [1, 1, 4]
	        },
	        title: {
	          text: 'XYZ - Stock Analysis (2013 - 2019)',
	          align: 'left',
	          offsetX: 110
	        },
	        xaxis: {
	          categories: [2013, 2014, 2015, 2016, 2017, 2018, 2019],
	        },
	        yaxis: [
	          {
	            axisTicks: {
	              show: true,
	            },
	            axisBorder: {
	              show: true,
	              color: '#008FFB'
	            },
	            labels: {
	              style: {
	                colors: '#008FFB',
	              }
	            },
	            title: {
	              text: "Income (thousand crores)",
	              style: {
	                color: '#008FFB',
	              }
	            },
	            tooltip: {
	              enabled: true
	            }
	          },
	          {
	            seriesName: 'Income',
	            opposite: true,
	            axisTicks: {
	              show: true,
	            },
	            axisBorder: {
	              show: true,
	              color: '#00E396'
	            },
	            labels: {
	              style: {
	                colors: '#00E396',
	              }
	            },
	            title: {
	              text: "Operating Cashflow (thousand crores)",
	              style: {
	                color: '#00E396',
	              }
	            },
	          },
	          {
	            seriesName: 'Revenue',
	            opposite: true,
	            axisTicks: {
	              show: true,
	            },
	            axisBorder: {
	              show: true,
	              color: '#FEB019'
	            },
	            labels: {
	              style: {
	                colors: '#FEB019',
	              },
	            },
	            title: {
	              text: "Revenue (thousand crores)",
	              style: {
	                color: '#FEB019',
	              }
	            }
	          },
	        ],
	        tooltip: {
	          fixed: {
	            enabled: true,
	            position: 'topLeft',
	            offsetY: 30,
	            offsetX: 60
	          },
	        },
	        legend: {
	          horizontalAlign: 'left',
	          offsetX: 40
	        }
	        };

    var chart = new ApexCharts(
      document.querySelector("#chart5"),
      options
    );

    chart.render();
}
function chart6(){
	var options = {
	          series: [{
	          name: "STOCK ABC",
	          data: [19, 27, 20, 30, 35, 23, 15, 35, 10, 30]
	        }],
	          chart: {
	          type: 'area',
	          height: 350,
	          zoom: {
	            enabled: false
	          }
	        },
	        dataLabels: {
	          enabled: false
	        },
	        stroke: {
	          curve: 'straight'
	        },
	        colors : ['#FFD902'],
	        title: {
	          text: 'Fundamental Analysis of Stocks',
	          align: 'left'
	        },
	        subtitle: {
	          text: 'Price Movements',
	          align: 'left'
	        },
	        xaxis: {
	          type: 'category',
	          categories: ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10'],
	        },
	        yaxis: {
	          opposite: true
	        },
	        legend: {
	          horizontalAlign: 'left'
	        }
	        };

        var chart = new ApexCharts(
            document.querySelector("#chart6"),
            options
        );

        chart.render();
}
function chart7(){
	
	 var options = {
	          series: [44, 55, 41, 17, 15],
	          chart: {
	          width: 355,
	          type: 'donut',
	          dropShadow: {
	            enabled: true,
	            color: '#111',
	            top: -1,
	            left: 3,
	            blur: 3,
	            opacity: 0.2
	          }
	        },
	        stroke: {
	          width: 0,
	        },
	        plotOptions: {
	          pie: {
	            donut: {
	              labels: {
	                show: true,
	                total: {
	                  showAlways: true,
	                  show: true
	                }
	              }
	            }
	          }
	        },
	        labels: ["Comedy", "Action", "SciFi", "Drama", "Horror"],
	        dataLabels: {
	          dropShadow: {
	            blur: 3,
	            opacity: 0.8
	          }
	        },
	        fill: {
	        type: 'pattern',
	          opacity: 1,
	          pattern: {
	            enabled: true,
	            style: ['verticalLines', 'squares', 'horizontalLines', 'circles','slantedLines'],
	          },
	        },
	        states: {
	          hover: {
	            filter: 'none'
	          }
	        },
	        theme: {
	          palette: 'palette2'
	        },
	        title: {
	          text: "Favourite Movie Type"
	        },
	        responsive: [{
	          breakpoint: 480,
	          options: {
	            chart: {
	              width: 200
	            },
	            legend: {
	              position: 'bottom'
	            }
	          }
	        }]
	        };

        var chart = new ApexCharts(
            document.querySelector("#chart7"),
            options
        );

        chart.render();
}
function chart8(){

	var options = {
	          series: [{
	          data: [{
	              x: new Date(1538778600000),
	              y: [6629.81, 6650.5, 6623.04, 6633.33]
	            },
	            {
	              x: new Date(1538780400000),
	              y: [6632.01, 6643.59, 6620, 6630.11]
	            },
	            {
	              x: new Date(1538782200000),
	              y: [6630.71, 6648.95, 6623.34, 6635.65]
	            },
	            {
	              x: new Date(1538784000000),
	              y: [6635.65, 6651, 6629.67, 6638.24]
	            },
	            {
	              x: new Date(1538785800000),
	              y: [6638.24, 6640, 6620, 6624.47]
	            },
	            {
	              x: new Date(1538787600000),
	              y: [6624.53, 6636.03, 6621.68, 6624.31]
	            },
	            {
	              x: new Date(1538789400000),
	              y: [6624.61, 6632.2, 6617, 6626.02]
	            },
	            {
	              x: new Date(1538791200000),
	              y: [6627, 6627.62, 6584.22, 6603.02]
	            },
	            {
	              x: new Date(1538793000000),
	              y: [6605, 6608.03, 6598.95, 6604.01]
	            },
	            {
	              x: new Date(1538794800000),
	              y: [6604.5, 6614.4, 6602.26, 6608.02]
	            },
	            {
	              x: new Date(1538796600000),
	              y: [6608.02, 6610.68, 6601.99, 6608.91]
	            },
	            {
	              x: new Date(1538798400000),
	              y: [6608.91, 6618.99, 6608.01, 6612]
	            },
	            {
	              x: new Date(1538800200000),
	              y: [6612, 6615.13, 6605.09, 6612]
	            },
	            {
	              x: new Date(1538802000000),
	              y: [6612, 6624.12, 6608.43, 6622.95]
	            },
	            {
	              x: new Date(1538803800000),
	              y: [6623.91, 6623.91, 6615, 6615.67]
	            },
	            {
	              x: new Date(1538805600000),
	              y: [6618.69, 6618.74, 6610, 6610.4]
	            },
	            {
	              x: new Date(1538807400000),
	              y: [6611, 6622.78, 6610.4, 6614.9]
	            },
	            {
	              x: new Date(1538809200000),
	              y: [6614.9, 6626.2, 6613.33, 6623.45]
	            },
	            {
	              x: new Date(1538811000000),
	              y: [6623.48, 6627, 6618.38, 6620.35]
	            },
	            {
	              x: new Date(1538812800000),
	              y: [6619.43, 6620.35, 6610.05, 6615.53]
	            },
	            {
	              x: new Date(1538814600000),
	              y: [6615.53, 6617.93, 6610, 6615.19]
	            },
	            {
	              x: new Date(1538816400000),
	              y: [6615.19, 6621.6, 6608.2, 6620]
	            },
	            {
	              x: new Date(1538818200000),
	              y: [6619.54, 6625.17, 6614.15, 6620]
	            },
	            {
	              x: new Date(1538820000000),
	              y: [6620.33, 6634.15, 6617.24, 6624.61]
	            },
	            {
	              x: new Date(1538821800000),
	              y: [6625.95, 6626, 6611.66, 6617.58]
	            },
	            {
	              x: new Date(1538823600000),
	              y: [6619, 6625.97, 6595.27, 6598.86]
	            },
	            {
	              x: new Date(1538825400000),
	              y: [6598.86, 6598.88, 6570, 6587.16]
	            },
	            {
	              x: new Date(1538827200000),
	              y: [6588.86, 6600, 6580, 6593.4]
	            },
	            {
	              x: new Date(1538829000000),
	              y: [6593.99, 6598.89, 6585, 6587.81]
	            },
	            {
	              x: new Date(1538830800000),
	              y: [6587.81, 6592.73, 6567.14, 6578]
	            },
	            {
	              x: new Date(1538832600000),
	              y: [6578.35, 6581.72, 6567.39, 6579]
	            },
	            {
	              x: new Date(1538834400000),
	              y: [6579.38, 6580.92, 6566.77, 6575.96]
	            },
	            {
	              x: new Date(1538836200000),
	              y: [6575.96, 6589, 6571.77, 6588.92]
	            },
	            {
	              x: new Date(1538838000000),
	              y: [6588.92, 6594, 6577.55, 6589.22]
	            },
	            {
	              x: new Date(1538839800000),
	              y: [6589.3, 6598.89, 6589.1, 6596.08]
	            },
	            {
	              x: new Date(1538841600000),
	              y: [6597.5, 6600, 6588.39, 6596.25]
	            },
	            {
	              x: new Date(1538843400000),
	              y: [6598.03, 6600, 6588.73, 6595.97]
	            },
	            {
	              x: new Date(1538845200000),
	              y: [6595.97, 6602.01, 6588.17, 6602]
	            },
	            {
	              x: new Date(1538847000000),
	              y: [6602, 6607, 6596.51, 6599.95]
	            },
	            {
	              x: new Date(1538848800000),
	              y: [6600.63, 6601.21, 6590.39, 6591.02]
	            },
	            {
	              x: new Date(1538850600000),
	              y: [6591.02, 6603.08, 6591, 6591]
	            },
	            {
	              x: new Date(1538852400000),
	              y: [6591, 6601.32, 6585, 6592]
	            },
	            {
	              x: new Date(1538854200000),
	              y: [6593.13, 6596.01, 6590, 6593.34]
	            },
	            {
	              x: new Date(1538856000000),
	              y: [6593.34, 6604.76, 6582.63, 6593.86]
	            },
	            {
	              x: new Date(1538857800000),
	              y: [6593.86, 6604.28, 6586.57, 6600.01]
	            },
	            {
	              x: new Date(1538859600000),
	              y: [6601.81, 6603.21, 6592.78, 6596.25]
	            },
	            {
	              x: new Date(1538861400000),
	              y: [6596.25, 6604.2, 6590, 6602.99]
	            },
	            {
	              x: new Date(1538863200000),
	              y: [6602.99, 6606, 6584.99, 6587.81]
	            },
	            {
	              x: new Date(1538865000000),
	              y: [6587.81, 6595, 6583.27, 6591.96]
	            },
	            {
	              x: new Date(1538866800000),
	              y: [6591.97, 6596.07, 6585, 6588.39]
	            },
	            {
	              x: new Date(1538868600000),
	              y: [6587.6, 6598.21, 6587.6, 6594.27]
	            },
	            {
	              x: new Date(1538870400000),
	              y: [6596.44, 6601, 6590, 6596.55]
	            },
	            {
	              x: new Date(1538872200000),
	              y: [6598.91, 6605, 6596.61, 6600.02]
	            },
	            {
	              x: new Date(1538874000000),
	              y: [6600.55, 6605, 6589.14, 6593.01]
	            },
	            {
	              x: new Date(1538875800000),
	              y: [6593.15, 6605, 6592, 6603.06]
	            },
	            {
	              x: new Date(1538877600000),
	              y: [6603.07, 6604.5, 6599.09, 6603.89]
	            },
	            {
	              x: new Date(1538879400000),
	              y: [6604.44, 6604.44, 6600, 6603.5]
	            },
	            {
	              x: new Date(1538881200000),
	              y: [6603.5, 6603.99, 6597.5, 6603.86]
	            },
	            {
	              x: new Date(1538883000000),
	              y: [6603.85, 6605, 6600, 6604.07]
	            },
	            {
	              x: new Date(1538884800000),
	              y: [6604.98, 6606, 6604.07, 6606]
	            },
	          ]
	        }],
	          chart: {
	          type: 'candlestick',
	          height: 350
	        },
	        title: {
	          text: 'CandleStick Chart',
	          align: 'left'
	        },
	        xaxis: {
	          type: 'datetime'
	        },
	        colors : ['#FF0202','#F7FF02'],
	        yaxis: {
	          tooltip: {
	            enabled: true
	          }
	        }
	        };

        var chart = new ApexCharts(
            document.querySelector("#chart8"),
            options
        );

        chart.render();

       

}