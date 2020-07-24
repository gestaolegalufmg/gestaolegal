"use strict";

var sparkline_values = [115, 145, 325, 105, 225, 495, 345, 525, 385, 215, 425, 425, 235, 235, 475, 565],
  sparkline_values_bar = [9, 8, 5, 9, 6, 9, 7, 6, 5, 7, 6, 8, 8, 9, 8, 5, 9, 6, 9, 7, 6, 5],
  sparkline_pie = [50, 30, 20];

$('.sparkline-inline').sparkline(sparkline_values, {
  type: 'line',
  width: '100%',
  height: '200',
  lineWidth: 3,
  lineColor: 'rgba(252,182,22)',
  fillColor: 'rgba(252,182,22,.2)',
  highlightSpotColor: 'rgba(252,182,22,.1)',
  highlightLineColor: 'rgba(252,182,22,.1)',
  spotRadius: 0,
});

$('.sparkline-line').sparkline(sparkline_values, {
  type: 'line',
  width: '100%',
  height: '200',
  lineWidth: 2,
  lineColor: 'rgba(226,95,255)',
  fillColor: 'transparent',
  highlightSpotColor: 'rgba(226,95,255,.1)',
  highlightLineColor: 'rgba(226,95,255,.1)',
  spotRadius: 0,
});

$(".sparkline-bar").sparkline(sparkline_values_bar, {
  type: 'bar',
  width: '100%',
  height: '200',
  barColor: 'rgb(170,32,214)',
  barWidth: 20
});

$(".sparkline-pie").sparkline(sparkline_pie, {
  type: 'pie',
  width: 'auto',
  height: '200',
  barWidth: 20
});