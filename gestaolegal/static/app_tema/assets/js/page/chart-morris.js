'use strict';
$(function () {
    getMorris('line', 'line_chart');
    getMorris('bar', 'bar_chart');
    getMorris('area', 'area_chart');
    getMorris('donut', 'donut_chart');
});


function getMorris(type, element) {
    if (type === 'line') {
        Morris.Line({
            element: element,
            data: [{
                period: '2010',
                iphone: 60,
                ipad: 80,
            }, {
                period: '2011',
                iphone: 180,
                ipad: 200
            }, {
                period: '2012',
                iphone: 50,
                ipad: 80
            }, {
                period: '2013',
                iphone: 150,
                ipad: 220
            }, {
                period: '2014',
                iphone: 150,
                ipad: 75
            }, {
                period: '2015',
                iphone: 130,
                ipad: 100
            }, {
                period: '2016',
                iphone: 130,
                ipad: 200
            }, {
                period: '2017',
                iphone: 185,
                ipad: 125
            }, {
                period: '2018',
                iphone: 70,
                ipad: 101
            },
            {
                period: '2019',
                iphone: 220,
                ipad: 190
            }
            ],
            xkey: 'period',
            ykeys: ['iphone', 'ipad'],
            labels: ['iPhone', 'iPad'],
            pointSize: 3,
            fillOpacity: 0,
            pointStrokeColors: ['#0023FF', '#FF00EC'],
            behaveLikeLine: true,
            gridLineColor: '#e0e0e0',
            lineWidth: 2,
            hideHover: 'auto',
            lineColors: ['#0023FF', '#FF00EC', '#FFAA00'],
            resize: true,
        });
    } else if (type === 'bar') {
    	 Morris.Bar({
    		    element: element,
    		    data: [{
                    x: '2006 Q1',
                    y: 100,
                    z: 70
                },{
                    x: '2004 Q1',
                    y: 55,
                    z: 70
                },{
                    x: '2008 Q1',
                    y: 50,
                    z: 100
                },{
                    x: '2009 Q1',
                    y: 40,
                    z: 80
                },{
                    x: '2010 Q1',
                    y: 50,
                    z: 60
                },{
                    x: '2011 Q1',
                    y: 55,
                    z: 70
                }, {
                    x: '2012 Q1',
                    y: 70,
                    z: 55
                }, {
                    x: '2013 Q1',
                    y: 75,
                    z: 70
                }, {
                    x: '2014 Q2',
                    y: 90,
                    z: 85
                }, {
                    x: '2015 Q3',
                    y: 70,
                    z: 75
                }, {
                    x: '2016 Q4',
                    y: 40,
                    z: 75
                }, {
                    x: '2017 Q4',
                    y: 30,
                    z: 50
                }, {
                    x: '2018 Q4',
                    y: 80,
                    z: 40
                }, {
                    x: '2019 Q4',
                    y: 70,
                    z: 30
                }],
                xkey: 'x',
                ykeys: ['y', 'z'],
                labels: ['Y', 'Z'],
                barColors: ['#FFB602', '#2CD393'],
    		    hideHover: 'auto',
    		    stacked: true
    		  });

    } else if (type === 'area') {
        Morris.Area({
            element: element,
            data: [
                { w: '2013', x: 10, y: 10},
                { w: '2014', x: 65, y: 19},
                { w: '2015', x: 10, y: 65},
                { w: '2016', x: 50, y: 11},
                { w: '2017', x: 11, y: 50},
                { w: '2018', x: 65, y: 11},
                { w: '2019', x: 10, y: 50}
            ],
            xkey: 'w',
            ykeys: ['x', 'y'],
            labels: ['X', 'Y'],
            pointSize: 0,
            lineWidth: 0,
            resize: true,
            fillOpacity: 0.8,
            behaveLikeLine: true,
            gridLineColor: '#e0e0e0',
            hideHover: 'auto',
            lineColors: ['rgb(10, 85, 148)', 'rgb(148, 10, 75)']
        });
    } else if (type === 'donut') {
        Morris.Donut({
            element: element,
            data: [{
                label: 'Chrome',
                value: 40
            }, {
                label: 'Firefox',
                value: 20
            }, {
                label: 'Safari',
                value: 25
            }, {
                label: 'Opera',
                value: 10
            },
            {
                label: 'Other',
                value: 5
            }],
            colors: ['rgb(254, 251, 91)', 'rgb(91, 254, 249)', 'rgb(210, 141, 209)', 'rgb(249, 136, 136)', 'rgb(75, 192, 192)'],
            formatter: function (y) {
                return y + '%'
            }
        });
    }
}