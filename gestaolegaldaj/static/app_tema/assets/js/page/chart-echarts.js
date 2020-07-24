$(function (e) {
    'use strict'

    /* Chart data*/
    var chartdata = [
        {
            name: 'sales',
            type: 'bar',
            data: [15, 12, 15, 9, 17, 12, 14]
        },
        {
            name: 'profit',
            type: 'line',
            data: [15, 11, 8, 18, 12, 16],
            symbolSize: 10,
        },
        {
            name: 'growth',
            type: 'bar',
            data: [19, 11, 15, 11, 16, 10, 26]
        }
    ];

    /* Bar chart echartopt1*/
    var chart = document.getElementById('echart_bar_line');
    var barChart = echarts.init(chart);

    var option = {
        grid: {
            top: '6',
            right: '0',
            bottom: '17',
            left: '25',
        },
        xAxis: {
            data: ['2014', '2015', '2016', '2017', '2018', '2019'],
            axisLine: {
                lineStyle: {
                    color: '#eaeaea'
                }
            },
            axisLabel: {
                fontSize: 10,
                color: '#000'
            }
        },
        tooltip: {
            show: true,
            showContent: true,
            alwaysShowContent: false,
            triggerOn: 'mousemove',
            trigger: 'axis',
            axisPointer:
            {
                label: {
                    show: false,
                }
            }

        },
        yAxis: {
            splitLine: {
                lineStyle: {
                    color: '#eaeaea'
                }
            },
            axisLine: {
                lineStyle: {
                    color: '#eaeaea'
                }
            },
            axisLabel: {
                fontSize: 10,
                color: '#000'
            }
        },
        series: chartdata,
        color: ['#28699B', '#B60048', '#E2A100',]
    };

    barChart.setOption(option);


    var chartdata2 = [
        {
            name: 'sales',
            type: 'line',
            data: [20, 27, 19, 36, 22, 46],
            symbolSize: 10,
            color: ['#FF07F0']
        },
        {
            name: 'Profit',
            type: 'line',
            smooth: true,
            symbolSize: 10,
            size: 10,
            data: [13, 17, 33, 15, 17, 20],
            color: ['#00A878']
        }
    ];

    var chart2 = document.getElementById('echart_line');
    var barChart2 = echarts.init(chart2);
    var option2 = {
        grid: {
            top: '6',
            right: '0',
            bottom: '17',
            left: '25',
        },
        xAxis: {
            data: ['2014', '2015', '2016', '2017', '2018'],
            axisLine: {
                lineStyle: {
                    color: '#eaeaea'
                }
            },
            axisLabel: {
                fontSize: 10,
                color: '#000'
            }
        },
        tooltip: {
            show: true,
            showContent: true,
            alwaysShowContent: false,
            triggerOn: 'mousemove',
            trigger: 'axis',
            axisPointer:
            {
                label: {
                    show: false,
                },
            }
        },
        yAxis: {
            splitLine: {
                lineStyle: {
                    color: 'none'
                }
            },
            axisLine: {
                lineStyle: {
                    color: '#eaeaea'
                }
            },
            axisLabel: {
                fontSize: 10,
                color: '#000'
            }
        },
        series: chartdata2,
    };
    barChart2.setOption(option2);



    /* Bar chart */

    /* Chart data*/
    var chartdata = [
        {
            name: 'Mobile',
            type: 'bar',
            data: [25, 20, 30, 35, 30, 40]
        },

        {
            name: 'Laptop',
            type: 'bar',
            data: [20, 25, 35, 30, 40, 20]
        },
        
        {
            name: 'Computer',
            type: 'bar',
            data: [10, 20, 25, 40, 10, 25]
        }
    ];


    var chart = document.getElementById('echart_bar');
    var barChart = echarts.init(chart);

    var option = {
        grid: {
            top: '6',
            right: '0',
            bottom: '17',
            left: '25',
        },
        bar:{
        	horizontal: true
        },
        xAxis: {
            data: ['2015', '2016', '2017', '2018', '2019'],

            axisLabel: {
                fontSize: 10,
                color: '#000'
            }
        },
        tooltip: {
            show: true,
            showContent: true,
            alwaysShowContent: false,
            triggerOn: 'mousemove',
            trigger: 'axis',
            axisPointer:
            {
                label: {
                    show: false,
                }
            }
        },
        yAxis: {
            axisLabel: {
                fontSize: 10,
                color: '#000'
            }
        },
        series: chartdata,
        color: ['#FF952B', '#0BCF84', '#0BABCF']
    };

    barChart.setOption(option);


    /* Bar Graph */
    var chart = document.getElementById('echart_graph_line');
    var barChart = echarts.init(chart);

    barChart.setOption({
        title: {
            text: "Graph title",
            subtext: "Graph Sub-text"
        },
        tooltip: {
            trigger: "axis"
        },
        legend: {
            data: ["sales", "purchases"]
        },
        toolbox: {
            show: !1
        },
        calculable: !1,
        xAxis: [{
            type: "category",
            data: ["2014", "2015", "2016", "2017", "2018", "2019"]
        }],
        yAxis: [{
            type: "value"
        }],
        series: [{
            name: "sales",
            type: "bar",
            data: [27, 60, 43, 29, 31, 82],
            markPoint: {
                data: [{
                    type: "max",
                    name: "???"
                }, {
                    type: "min",
                    name: "???"
                }]
            },
            markLine: {
                data: [{
                    type: "average",
                    name: "???"
                }]
            }
        }, {
            name: "purchases",
            type: "bar",
            data: [41, 51, 53, 16, 41, 76],
            markPoint: {
                data: [{
                    name: "sales",
                    value: 182.2,
                    xAxis: 7,
                    yAxis: 183
                }, {
                    name: "purchases",
                    value: 2.3,
                    xAxis: 11,
                    yAxis: 3
                }]
            },
            markLine: {
                data: [{
                    type: "average",
                    name: "???"
                }]
            }
        }],
        color: ['#760BCF', '#CF0B7F']

    });

    /* Pie Chart */
    var chart = document.getElementById('echart_pie');
    var barChart = echarts.init(chart);

    barChart.setOption({
        tooltip: {
            trigger: "item",
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            x: "center",
            y: "bottom",
            data: ["Direct Access", "E-mail Marketing", "Union Ad", "Video Ads", "Search Engine"]
        },

        calculable: !0,
        series: [{
            name: "Chart Data",
            type: "pie",
            radius: "55%",
            center: ["50%", "48%"],
            data: [{
                value: 10,
                name: "Direct Access"
            }, {
                value: 20,
                name: "E-mail Marketing"
            }, {
                value: 15,
                name: "Union Ad"
            }, {
                value: 25,
                name: "Video Ads"
            }, {
                value: 40,
                name: "Search Engine"
            }]
        }],
        color: ['#8ad4eb', '#00dfce', '#fcbe06', '#fd625e', '#1c7b99']
    });

    /* line chart */
    var chart = document.getElementById('echart_area_line');
    var lineChart = echarts.init(chart);

    lineChart.setOption({
        title: {
            text: "Line Graph",
            subtext: "Subtitle"
        },
        tooltip: {
            trigger: "axis"
        },
        legend: {
            x: 220,
            y: 40,
            data: ["Intent", "Pre-order", "Deal"]
        },
        toolbox: {
            show: !0,
            feature: {
                magicType: {
                    show: !0,
                    title: {
                        line: "Line",
                        bar: "Bar",
                        stack: "Stack",
                        tiled: "Tiled"
                    },
                    type: ["line", "bar", "stack", "tiled"]
                },
                restore: {
                    show: !0,
                    title: "Restore"
                },
                saveAsImage: {
                    show: !0,
                    title: "Save Image"
                }
            }
        },
        calculable: !0,
        xAxis: [{
            type: "category",
            boundaryGap: !1,
            data: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        }],
        yAxis: [{
            type: "value"
        }],
        series: [{
            name: "Deal",
            type: "line",
            smooth: !0,
            itemStyle: {
                normal: {
                    areaStyle: {
                        type: "default"
                    }
                }
            },
            data: [0, 13, 20, 55, 270, 880, 720]
        }, {
            name: "Pre-order",
            type: "line",
            smooth: !0,
            itemStyle: {
                normal: {
                    areaStyle: {
                        type: "default"
                    }
                }
            },
            data: [30, 400, 435, 792, 391, 31, 11]
        }, {
            name: "Intent",
            type: "line",
            smooth: !0,
            itemStyle: {
                normal: {
                    areaStyle: {
                        type: "default"
                    }
                }
            },
            data: [600, 900, 400, 50, 200, 300, 400]
        }],
        color: ['#ff952b', '#0bcf84', '#0babcf']
    });

    /* Sonar Chart */
    var chart = document.getElementById('echart_sonar');
    var sonarChart = echarts.init(chart);

    sonarChart.setOption({
        title: {
            text: "Budget vs spending",
            subtext: "Subtitle"
        },
        tooltip: {
            trigger: "item"
        },
        legend: {
            orient: "vertical",
            x: "right",
            y: "bottom",
            data: ["Allocated Budget", "Actual Spending"]
        },
        toolbox: {
            show: !0,
            feature: {
                restore: {
                    show: !0,
                    title: "Restore"
                },
                saveAsImage: {
                    show: !0,
                    title: "Save Image"
                }
            }
        },
        polar: [{
            indicator: [{
                text: "Sales",
                max: 6e3
            }, {
                text: "Administration",
                max: 16e3
            }, {
                text: "Information Techology",
                max: 3e4
            }, {
                text: "Customer Support",
                max: 38e3
            }, {
                text: "Development",
                max: 52e3
            }, {
                text: "Marketing",
                max: 25e3
            }]
        }],
        calculable: !0,
        series: [{
            name: "Budget vs spending",
            type: "radar",
            data: [{
                value: [4400, 13e3, 28e3, 30e3, 50e3, 19e3],
                name: "Allocated Budget"
            }, {
                value: [58e2, 10e3, 28e3, 38e3, 47e3, 22e3],
                name: "Actual Spending"
            }]
        }],
        color: ['#ff952b', '#0bcf84']
    });

    /* Donut Chart */
    var chart = document.getElementById('echart_donut');
    var donutChart = echarts.init(chart);

    donutChart.setOption({
        tooltip: {
            trigger: "item",
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        calculable: !0,
        legend: {
            x: "center",
            y: "bottom",
            data: ["Direct Access", "E-mail Marketing", "Union Ad", "Video Ads", "Search Engine"]
        },
        toolbox: {
            show: !0,
            feature: {
                magicType: {
                    show: !0,
                    type: ["pie", "funnel"],
                    option: {
                        funnel: {
                            x: "25%",
                            width: "50%",
                            funnelAlign: "center",
                            max: 1548
                        }
                    }
                },
                restore: {
                    show: !0,
                    title: "Restore"
                },
                saveAsImage: {
                    show: !0,
                    title: "Save Image"
                }
            }
        },
        series: [{
            name: "Access to the resource",
            type: "pie",
            radius: ["35%", "55%"],
            itemStyle: {
                normal: {
                    label: {
                        show: !0
                    },
                    labelLine: {
                        show: !0
                    }
                },
                emphasis: {
                    label: {
                        show: !0,
                        position: "center",
                        textStyle: {
                            fontSize: "14",
                            fontWeight: "normal"
                        }
                    }
                }
            },
            data: [{
                value: 400,
                name: "Direct Access"
            }, {
                value: 200,
                name: "E-mail Marketing"
            }, {
                value: 250,
                name: "Union Ad"
            }, {
                value: 500,
                name: "Video Ads"
            }, {
                value: 1000,
                name: "Search Engine"
            }],
            color: ['#8ad4eb', '#00dfce', '#fcbe06', '#fd625e', '#1c7b99']
        }]
    });

});

