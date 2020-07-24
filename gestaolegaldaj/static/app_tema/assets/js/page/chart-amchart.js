'use strict';
$(function () {
  barChart();
  curveChart();
  lineChart();
  radarChart();
  pieChart();
  waterfallChart();
  ganttChart();
  candleStickChart();
});

function barChart() {
  // Themes begin
  am4core.useTheme(am4themes_animated);
  // Themes end

// Create chart instance
var chart = am4core.create("barChart", am4charts.XYChart);

//Add data
chart.data = [{
 "year": 2010,
 "income": 33.5,
 "expenses": 17.2
},{
 "year": 2011,
 "income": 36.2,
 "expenses": 21.5
},{
 "year": 2012,
 "income": 30.1,
 "expenses": 20.1
},{
 "year": 2013,
 "income": 39.5,
 "expenses": 23.2
},{
 "year": 2014,
 "income": 29.1,
 "expenses": 12.3
}];

//Create axes
var categoryAxis = chart.yAxes.push(new am4charts.CategoryAxis());
categoryAxis.dataFields.category = "year";
categoryAxis.numberFormatter.numberFormat = "#";
categoryAxis.renderer.inversed = true;
categoryAxis.renderer.grid.template.location = 0;
categoryAxis.renderer.cellStartLocation = 0.1;
categoryAxis.renderer.cellEndLocation = 0.9;

var  valueAxis = chart.xAxes.push(new am4charts.ValueAxis()); 
valueAxis.renderer.opposite = true;

//Create series
function createSeries(field, name) {
 var series = chart.series.push(new am4charts.ColumnSeries());
 series.dataFields.valueX = field;
 series.dataFields.categoryY = "year";
 series.name = name;
 series.columns.template.tooltipText = "{name}: [bold]{valueX}[/]";
 series.columns.template.height = am4core.percent(100);
 series.sequencedInterpolation = true;

 var valueLabel = series.bullets.push(new am4charts.LabelBullet());
 valueLabel.label.text = "{valueX}";
 valueLabel.label.horizontalCenter = "left";
 valueLabel.label.dx = 10;
 valueLabel.label.hideOversized = false;
 valueLabel.label.truncate = false;

 var categoryLabel = series.bullets.push(new am4charts.LabelBullet());
 categoryLabel.label.text = "{name}";
 categoryLabel.label.horizontalCenter = "right";
 categoryLabel.label.dx = -10;
 categoryLabel.label.fill = am4core.color("#fff");
 categoryLabel.label.hideOversized = false;
 categoryLabel.label.truncate = false;
}

createSeries("income", "Income");
createSeries("expenses", "Expenses");
}
function curveChart() {
	// Themes begin
	am4core.useTheme(am4themes_animated);
	// Themes end

	var chart = am4core.create("curveChart", am4charts.XYChart);
	chart.hiddenState.properties.opacity = 0; // this makes initial fade in effect

	chart.data = [{
	  "country": "2010",
	  "value": 1035
	}, {
	  "country": "2011",
	  "value": 2832
	}, {
	  "country": "2012",
	  "value": 1809
	}, {
	  "country": "2013",
	  "value": 3332
	}, {
	  "country": "2014",
	  "value": 1012
	}, {
	  "country": "2015",
	  "value": -1304
	}, {
	  "country": "2016",
	  "value": -777
	}, {
	  "country": "2017",
	  "value": 1111
	}, {
	  "country": "2018",
	  "value": 1665
	}];


	var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
	categoryAxis.renderer.grid.template.location = 0;
	categoryAxis.dataFields.category = "country";
	categoryAxis.renderer.minGridDistance = 40;

	var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());

	var series = chart.series.push(new am4charts.CurvedColumnSeries());
	series.dataFields.categoryX = "country";
	series.dataFields.valueY = "value";
	series.tooltipText = "{valueY.value}"
	series.columns.template.strokeOpacity = 0;

	series.columns.template.fillOpacity = 0.75;

	var hoverState = series.columns.template.states.create("hover");
	hoverState.properties.fillOpacity = 1;
	hoverState.properties.tension = 0.4;

	chart.cursor = new am4charts.XYCursor();

	// Add distinctive colors for each column using adapter
	series.columns.template.adapter.add("fill", function(fill, target) {
	  return chart.colors.getIndex(target.dataItem.index);
	});

	chart.scrollbarX = new am4core.Scrollbar();

}

function lineChart() {
  // Themes begin
  am4core.useTheme(am4themes_animated);
  // Themes end

  // Create chart instance
  var chart = am4core.create("lineChart", am4charts.XYChart);

  // Add data
  chart.data = [{
    "date": "2012-08-12",
    "value": 40
  }, {
    "date": "2012-08-13",
    "value": 30
  }, {
    "date": "2012-08-14",
    "value": 20
  }, {
    "date": "2012-08-15",
    "value": 25
  }, {
    "date": "2012-08-16",
    "value": 35
  }, {
    "date": "2012-08-17",
    "value": 15
  }, {
    "date": "2012-08-18",
    "value": 13
  }, {
    "date": "2012-08-19",
    "value": 19
  }, {
    "date": "2012-08-20",
    "value": 10
  }, {
    "date": "2012-08-28",
    "value": 13
  }, {
    "date": "2012-08-29",
    "value": 31
  }, {
    "date": "2012-08-30",
    "value": 28
  }, {
    "date": "2012-08-31",
    "value": 22
  }, {
    "date": "2012-09-01",
    "value": 10
  }, {
    "date": "2012-09-02",
    "value": 10
  }, {
    "date": "2012-09-03",
    "value": 20
  }, {
    "date": "2012-09-04",
    "value": 21
  }, {
    "date": "2012-09-05",
    "value": 15
  }, {
    "date": "2012-09-06",
    "value": 10
  }, {
    "date": "2012-09-07",
    "value": 12
  }, {
    "date": "2012-09-08",
    "value": 11
  }, {
    "date": "2012-09-09",
    "value": 33
  }, {
    "date": "2012-09-10",
    "value": 34
  }, {
    "date": "2012-09-11",
    "value": 36
  }, {
    "date": "2012-09-12",
    "value": 21
  }, {
    "date": "2012-09-13",
    "value": 20
  }, {
    "date": "2012-10-14",
    "value": 21
  }, {
    "date": "2012-10-15",
    "value": 45
  }, {
    "date": "2012-10-16",
    "value": 45
  }, {
    "date": "2012-10-17",
    "value": 62
  }, {
    "date": "2012-10-18",
    "value": 61
  }, {
    "date": "2012-10-19",
    "value": 63
  }, {
    "date": "2012-10-20",
    "value": 63
  }, {
    "date": "2012-10-21",
    "value": 22
  }, {
    "date": "2012-10-22",
    "value": 23
  }, {
    "date": "2012-10-23",
    "value": 15
  }, {
    "date": "2012-10-24",
    "value": 24
  }, {
    "date": "2012-10-25",
    "value": 19
  }, {
    "date": "2012-10-26",
    "value": 31
  }, {
    "date": "2012-10-27",
    "value": 56
  }, {
    "date": "2012-10-28",
    "value": 77
  }, {
    "date": "2012-10-29",
    "value": 50
  }, {
    "date": "2012-10-30",
    "value": 83
  }];

  // Create axes
  var dateAxis = chart.xAxes.push(new am4charts.DateAxis());
  var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());

  // Create series
  var series = chart.series.push(new am4charts.LineSeries());
  series.dataFields.valueY = "value";
  series.dataFields.dateX = "date";
  series.tooltipText = "{value}"
  series.strokeWidth = 2;
  series.minBulletDistance = 15;

  // Drop-shaped tooltips
  series.tooltip.background.cornerRadius = 20;
  series.tooltip.background.strokeOpacity = 0;
  series.tooltip.pointerOrientation = "vertical";
  series.tooltip.label.minWidth = 40;
  series.tooltip.label.minHeight = 40;
  series.tooltip.label.textAlign = "middle";
  series.tooltip.label.textValign = "middle";

  // Make bullets grow on hover
  var bullet = series.bullets.push(new am4charts.CircleBullet());
  bullet.circle.strokeWidth = 2;
  bullet.circle.radius = 4;
  bullet.circle.fill = am4core.color("#fff");

  var bullethover = bullet.states.create("hover");
  bullethover.properties.scale = 1.3;

  // Make a panning cursor
  chart.cursor = new am4charts.XYCursor();
  chart.cursor.behavior = "panXY";
  chart.cursor.xAxis = dateAxis;
  chart.cursor.snapToSeries = series;

  // Create vertical scrollbar and place it before the value axis
  chart.scrollbarY = new am4core.Scrollbar();
  chart.scrollbarY.parent = chart.leftAxesContainer;
  chart.scrollbarY.toBack();

  // Create a horizontal scrollbar with previe and place it underneath the date axis
  chart.scrollbarX = new am4charts.XYChartScrollbar();
  chart.scrollbarX.series.push(series);
  chart.scrollbarX.parent = chart.bottomAxesContainer;

  chart.events.on("ready", function () {
    dateAxis.zoom({ start: 0.90, end: 1 });
  });

}

function radarChart(){
	// Themes begin
	am4core.useTheme(am4themes_animated);
	// Themes end
	  
	// Create chart instance
	var chart = am4core.create("radarChart", am4charts.RadarChart);
	chart.scrollbarX = new am4core.Scrollbar();

	var data = [];

	for(var i = 0; i < 20; i++){
	  data.push({category: i, value:Math.round(Math.random() * 100)});
	}

	chart.data = data;
	chart.radius = am4core.percent(100);
	chart.innerRadius = am4core.percent(50);

	// Create axes
	var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
	categoryAxis.dataFields.category = "category";
	categoryAxis.renderer.grid.template.location = 0;
	categoryAxis.renderer.minGridDistance = 30;
	categoryAxis.tooltip.disabled = true;
	categoryAxis.renderer.minHeight = 110;
	categoryAxis.renderer.grid.template.disabled = true;
	//categoryAxis.renderer.labels.template.disabled = true;
	let labelTemplate = categoryAxis.renderer.labels.template;
	labelTemplate.radius = am4core.percent(-60);
	labelTemplate.location = 0.5;
	labelTemplate.relativeRotation = 90;

	var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
	valueAxis.renderer.grid.template.disabled = true;
	valueAxis.renderer.labels.template.disabled = true;
	valueAxis.tooltip.disabled = true;

	// Create series
	var series = chart.series.push(new am4charts.RadarColumnSeries());
	series.sequencedInterpolation = true;
	series.dataFields.valueY = "value";
	series.dataFields.categoryX = "category";
	series.columns.template.strokeWidth = 0;
	series.tooltipText = "{valueY}";
	series.columns.template.radarColumn.cornerRadius = 10;
	series.columns.template.radarColumn.innerCornerRadius = 0;

	series.tooltip.pointerOrientation = "vertical";

	// on hover, make corner radiuses bigger
	let hoverState = series.columns.template.radarColumn.states.create("hover");
	hoverState.properties.cornerRadius = 0;
	hoverState.properties.fillOpacity = 1;


	series.columns.template.adapter.add("fill", function(fill, target) {
	  return chart.colors.getIndex(target.dataItem.index);
	})

	// Cursor
	chart.cursor = new am4charts.RadarCursor();
	chart.cursor.innerRadius = am4core.percent(50);
	chart.cursor.lineY.disabled = true;

}
function donutChart() {
// Create chart instance
var chart = am4core.create("donutChart", am4charts.PieChart);

// Add data
chart.data = [{
  "country": "Lithuania",
  "litres": 550.8
}, {
  "country": "Czech Republic",
  "litres": 330.8
}, {
  "country": "Ireland",
  "litres": 210.2
},{
  "country": "The Netherlands",
  "litres": 51,
  "hidden": true
}];

// Add and configure Series
var pieSeries = chart.series.push(new am4charts.PieSeries());
pieSeries.dataFields.value = "litres";
pieSeries.dataFields.category = "country";
pieSeries.dataFields.hidden = "hidden";

// Let's cut a hole in our Pie chart the size of 40% the radius
chart.innerRadius = am4core.percent(40);

// Disable ticks and labels
pieSeries.labels.template.disabled = true;
pieSeries.ticks.template.disabled = true;

// Add a legend
chart.legend = new am4charts.Legend();
chart.legend.position = "bottom";

pieSeries.colors.list = [
	  am4core.color("#30D4EE"),
	  am4core.color("#C1FC2E"),
	  am4core.color("#FC692E"),
	  am4core.color("#FF9671"),
	  am4core.color("#FFC75F"),
	  am4core.color("#F9F871"),
	];
}

function pieChart() {

	// Themes begin
	am4core.useTheme(am4themes_animated);
	// Themes end

	var chart = am4core.create("pieChart", am4charts.PieChart3D);
	chart.hiddenState.properties.opacity = 0; // this creates initial fade-in

	chart.data = [
	  {
	    country: "America",
	    litres: 501.9
	  },
	  {
	    country: "Ireland",
	    litres: 201.1
	  },
	  {
	    country: "Germany",
	    litres: 165.8
	  },
	  {
	    country: "Australia",
	    litres: 139.9
	  },
	  {
	    country: "Canada",
	    litres: 128.3
	  }
	];

	chart.innerRadius = am4core.percent(40);
	chart.depth = 120;

	chart.legend = new am4charts.Legend();

	var series = chart.series.push(new am4charts.PieSeries3D());
	series.dataFields.value = "litres";
	series.dataFields.depthValue = "litres";
	series.dataFields.category = "country";
	series.slices.template.cornerRadius = 5;
	series.colors.step = 3;
}

function waterfallChart() {

	// Themes begin
	am4core.useTheme(am4themes_animated);
	// Themes end

	var chart = am4core.create("waterfallChart", am4charts.XYChart);
	chart.hiddenState.properties.opacity = 0; // this makes initial fade in effect

	// using math in the data instead of final values just to illustrate the idea of Waterfall chart
	// a separate data field for step series is added because we don't need last step (notice, the last data item doesn't have stepValue)
	chart.data = [ {
	  category: "Net revenue",
	  value: 9316,
	  open: 0,
	  stepValue: 9316,
	  color: chart.colors.getIndex( 14 ),
	  displayValue: 9316
	}, {
	  category: "Cost of sales",
	  value: 9316 - 2386,
	  open: 9316,
	  stepValue: 9316 - 2386,
	  color: chart.colors.getIndex( 9 ),
	  displayValue: 2386
	}, {
	  category: "Operating expenses",
	  value: 9316 - 2386 - 1233,
	  open: 9316 - 2386,
	  stepValue: 9316 - 2386 - 1233,
	  color: chart.colors.getIndex( 10 ),
	  displayValue: 1233
	}, {
	  category: "Amortisation",
	  value: 9316 - 2386 - 1233 - 313,
	  open: 9316 - 2386 - 1233,
	  stepValue: 9316 - 2386 - 1233 - 313,
	  color: chart.colors.getIndex( 11 ),
	  displayValue: 313
	}, {
	  category: "Income from equity",
	  value: 9316 - 2386 - 1233 - 313 + 1575,
	  open: 9316 - 2386 - 1233 - 313,
	  stepValue: 9316 - 2386 - 1233 - 313 + 1575,
	  color: chart.colors.getIndex( 17 ),
	  displayValue: 1575
	}, {
	  category: "Operating income",
	  value: 9316 - 2386 - 1233 - 313 + 1575,
	  open: 0,
	  color: chart.colors.getIndex( 18 ),
	  displayValue: 9316 - 2386 - 1233 - 313 + 1575
	} ];

	var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
	categoryAxis.dataFields.category = "category";
	categoryAxis.renderer.minGridDistance = 40;

	var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());

	var columnSeries = chart.series.push(new am4charts.ColumnSeries());
	columnSeries.dataFields.categoryX = "category";
	columnSeries.dataFields.valueY = "value";
	columnSeries.dataFields.openValueY = "open";
	columnSeries.fillOpacity = 0.8;
	columnSeries.sequencedInterpolation = true;
	columnSeries.interpolationDuration = 1500;

	var columnTemplate = columnSeries.columns.template;
	columnTemplate.strokeOpacity = 0;
	columnTemplate.propertyFields.fill = "color";

	var label = columnTemplate.createChild(am4core.Label);
	label.text = "{displayValue.formatNumber('$#,## a')}";
	label.align = "center";
	label.valign = "middle";


	var stepSeries = chart.series.push(new am4charts.StepLineSeries());
	stepSeries.dataFields.categoryX = "category";
	stepSeries.dataFields.valueY = "stepValue";
	stepSeries.noRisers = true;
	stepSeries.stroke = new am4core.InterfaceColorSet().getFor("alternativeBackground");
	stepSeries.strokeDasharray = "3,3";
	stepSeries.interpolationDuration = 2000;
	stepSeries.sequencedInterpolation = true;

	// because column width is 80%, we modify start/end locations so that step would start with column and end with next column
	stepSeries.startLocation = 0.1;
	stepSeries.endLocation = 1.1;

	chart.cursor = new am4charts.XYCursor();
	chart.cursor.behavior = "none";

}
function ganttChart() {
	// Themes begin
	am4core.useTheme(am4themes_animated);
	// Themes end

	var chart = am4core.create("ganttChart", am4charts.XYChart);
	chart.hiddenState.properties.opacity = 0; // this creates initial fade-in

	chart.paddingRight = 30;
	chart.dateFormatter.inputDateFormat = "yyyy-MM-dd HH:mm";

	var colorSet = new am4core.ColorSet();
	colorSet.saturation = 0.4;

	chart.data = [ {
	  "category": "Module #1",
	  "start": "2016-01-01",
	  "end": "2016-01-14",
	  "color": colorSet.getIndex(0).brighten(0),
	  "task": "Gathering requirements"
	}, {
	  "category": "Module #1",
	  "start": "2016-01-16",
	  "end": "2016-01-27",
	  "color": colorSet.getIndex(0).brighten(0.4),
	  "task": "Producing specifications"
	}, {
	  "category": "Module #1",
	  "start": "2016-02-05",
	  "end": "2016-04-18",
	  "color": colorSet.getIndex(0).brighten(0.8),
	  "task": "Development"
	}, {
	  "category": "Module #1",
	  "start": "2016-04-18",
	  "end": "2016-04-30",
	  "color": colorSet.getIndex(0).brighten(1.2),
	  "task": "Testing and QA"
	}, {
	  "category": "Module #2",
	  "start": "2016-01-08",
	  "end": "2016-01-10",
	  "color": colorSet.getIndex(2).brighten(0),
	  "task": "Gathering requirements"
	}, {
	  "category": "Module #2",
	  "start": "2016-01-12",
	  "end": "2016-01-15",
	  "color": colorSet.getIndex(2).brighten(0.4),
	  "task": "Producing specifications"
	}, {
	  "category": "Module #2",
	  "start": "2016-01-16",
	  "end": "2016-02-05",
	  "color": colorSet.getIndex(2).brighten(0.8),
	  "task": "Development"
	}, {
	  "category": "Module #2",
	  "start": "2016-02-10",
	  "end": "2016-02-18",
	  "color": colorSet.getIndex(2).brighten(1.2),
	  "task": "Testing and QA"
	}, {
	  "category": "Module #3",
	  "start": "2016-01-02",
	  "end": "2016-01-08",
	  "color": colorSet.getIndex(4).brighten(0),
	  "task": "Gathering requirements"
	}, {
	  "category": "Module #3",
	  "start": "2016-01-08",
	  "end": "2016-01-16",
	  "color": colorSet.getIndex(4).brighten(0.4),
	  "task": "Producing specifications"
	}, {
	  "category": "Module #3",
	  "start": "2016-01-19",
	  "end": "2016-03-01",
	  "color": colorSet.getIndex(4).brighten(0.8),
	  "task": "Development"
	}, {
	  "category": "Module #3",
	  "start": "2016-03-12",
	  "end": "2016-04-05",
	  "color": colorSet.getIndex(4).brighten(1.2),
	  "task": "Testing and QA"
	}, {
	  "category": "Module #4",
	  "start": "2016-01-01",
	  "end": "2016-01-19",
	  "color": colorSet.getIndex(6).brighten(0),
	  "task": "Gathering requirements"
	}, {
	  "category": "Module #4",
	  "start": "2016-01-19",
	  "end": "2016-02-03",
	  "color": colorSet.getIndex(6).brighten(0.4),
	  "task": "Producing specifications"
	}, {
	  "category": "Module #4",
	  "start": "2016-03-20",
	  "end": "2016-04-25",
	  "color": colorSet.getIndex(6).brighten(0.8),
	  "task": "Development"
	}, {
	  "category": "Module #4",
	  "start": "2016-04-27",
	  "end": "2016-05-15",
	  "color": colorSet.getIndex(6).brighten(1.2),
	  "task": "Testing and QA"
	}, {
	  "category": "Module #5",
	  "start": "2016-01-01",
	  "end": "2016-01-12",
	  "color": colorSet.getIndex(8).brighten(0),
	  "task": "Gathering requirements"
	}, {
	  "category": "Module #5",
	  "start": "2016-01-12",
	  "end": "2016-01-19",
	  "color": colorSet.getIndex(8).brighten(0.4),
	  "task": "Producing specifications"
	}, {
	  "category": "Module #5",
	  "start": "2016-01-19",
	  "end": "2016-03-01",
	  "color": colorSet.getIndex(8).brighten(0.8),
	  "task": "Development"
	}, {
	  "category": "Module #5",
	  "start": "2016-03-08",
	  "end": "2016-03-30",
	  "color": colorSet.getIndex(8).brighten(1.2),
	  "task": "Testing and QA"
	} ];

	chart.dateFormatter.dateFormat = "yyyy-MM-dd";
	chart.dateFormatter.inputDateFormat = "yyyy-MM-dd";

	var categoryAxis = chart.yAxes.push(new am4charts.CategoryAxis());
	categoryAxis.dataFields.category = "category";
	categoryAxis.renderer.grid.template.location = 0;
	categoryAxis.renderer.inversed = true;

	var dateAxis = chart.xAxes.push(new am4charts.DateAxis());
	dateAxis.renderer.minGridDistance = 70;
	dateAxis.baseInterval = { count: 1, timeUnit: "day" };
	// dateAxis.max = new Date(2018, 0, 1, 24, 0, 0, 0).getTime();
	//dateAxis.strictMinMax = true;
	dateAxis.renderer.tooltipLocation = 0;

	var series1 = chart.series.push(new am4charts.ColumnSeries());
	series1.columns.template.height = am4core.percent(70);
	series1.columns.template.tooltipText = "{task}: [bold]{openDateX}[/] - [bold]{dateX}[/]";

	series1.dataFields.openDateX = "start";
	series1.dataFields.dateX = "end";
	series1.dataFields.categoryY = "category";
	series1.columns.template.propertyFields.fill = "color"; // get color from data
	series1.columns.template.propertyFields.stroke = "color";
	series1.columns.template.strokeOpacity = 1;

	chart.scrollbarX = new am4core.Scrollbar();
}
function candleStickChart(){

	// Themes begin
	am4core.useTheme(am4themes_animated);
	// Themes end

	var chart = am4core.create("candleStickChart", am4charts.XYChart);
	chart.paddingRight = 20;

	chart.dateFormatter.inputDateFormat = "yyyy-MM-dd";

	var dateAxis = chart.xAxes.push(new am4charts.DateAxis());
	dateAxis.renderer.grid.template.location = 0;

	var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
	valueAxis.tooltip.disabled = true;

	var series = chart.series.push(new am4charts.CandlestickSeries());
	series.dataFields.dateX = "date";
	series.dataFields.valueY = "close";
	series.dataFields.openValueY = "open";
	series.dataFields.lowValueY = "low";
	series.dataFields.highValueY = "high";
	series.simplifiedProcessing = true;
	series.tooltipText = "Open:${openValueY.value}\nLow:${lowValueY.value}\nHigh:${highValueY.value}\nClose:${valueY.value}";

	chart.cursor = new am4charts.XYCursor();

	// a separate series for scrollbar
	var lineSeries = chart.series.push(new am4charts.LineSeries());
	lineSeries.dataFields.dateX = "date";
	lineSeries.dataFields.valueY = "close";
	// need to set on default state, as initially series is "show"
	lineSeries.defaultState.properties.visible = false;

	// hide from legend too (in case there is one)
	lineSeries.hiddenInLegend = true;
	lineSeries.fillOpacity = 0.5;
	lineSeries.strokeOpacity = 0.5;

	var scrollbarX = new am4charts.XYChartScrollbar();
	scrollbarX.series.push(lineSeries);
	chart.scrollbarX = scrollbarX;

	chart.data = [ {
	    "date": "2011-08-01",
	    "open": "136.65",
	    "high": "136.96",
	    "low": "134.15",
	    "close": "136.49"
	  }, {
	    "date": "2011-08-02",
	    "open": "135.26",
	    "high": "135.95",
	    "low": "131.50",
	    "close": "131.85"
	  }, {
	    "date": "2011-08-05",
	    "open": "132.90",
	    "high": "135.27",
	    "low": "128.30",
	    "close": "135.25"
	  }, {
	    "date": "2011-08-06",
	    "open": "134.94",
	    "high": "137.24",
	    "low": "132.63",
	    "close": "135.03"
	  }, {
	    "date": "2011-08-07",
	    "open": "136.76",
	    "high": "136.86",
	    "low": "132.00",
	    "close": "134.01"
	  }, {
	    "date": "2011-08-08",
	    "open": "131.11",
	    "high": "133.00",
	    "low": "125.09",
	    "close": "126.39"
	  }, {
	    "date": "2011-08-09",
	    "open": "123.12",
	    "high": "127.75",
	    "low": "120.30",
	    "close": "125.00"
	  }, {
	    "date": "2011-08-12",
	    "open": "128.32",
	    "high": "129.35",
	    "low": "126.50",
	    "close": "127.79"
	  }, {
	    "date": "2011-08-13",
	    "open": "128.29",
	    "high": "128.30",
	    "low": "123.71",
	    "close": "124.03"
	  }, {
	    "date": "2011-08-14",
	    "open": "122.74",
	    "high": "124.86",
	    "low": "119.65",
	    "close": "119.90"
	  }, {
	    "date": "2011-08-15",
	    "open": "117.01",
	    "high": "118.50",
	    "low": "111.62",
	    "close": "117.05"
	  }, {
	    "date": "2011-08-16",
	    "open": "122.01",
	    "high": "123.50",
	    "low": "119.82",
	    "close": "122.06"
	  }, {
	    "date": "2011-08-19",
	    "open": "123.96",
	    "high": "124.50",
	    "low": "120.50",
	    "close": "122.22"
	  }, {
	    "date": "2011-08-20",
	    "open": "122.21",
	    "high": "128.96",
	    "low": "121.00",
	    "close": "127.57"
	  }, {
	    "date": "2011-08-21",
	    "open": "131.22",
	    "high": "132.75",
	    "low": "130.33",
	    "close": "132.51"
	  }, {
	    "date": "2011-08-22",
	    "open": "133.09",
	    "high": "133.34",
	    "low": "129.76",
	    "close": "131.07"
	  }, {
	    "date": "2011-08-23",
	    "open": "130.53",
	    "high": "135.37",
	    "low": "129.81",
	    "close": "135.30"
	  }, {
	    "date": "2011-08-26",
	    "open": "133.39",
	    "high": "134.66",
	    "low": "132.10",
	    "close": "132.25"
	  }, {
	    "date": "2011-08-27",
	    "open": "130.99",
	    "high": "132.41",
	    "low": "126.63",
	    "close": "126.82"
	  }, {
	    "date": "2011-08-28",
	    "open": "129.88",
	    "high": "134.18",
	    "low": "129.54",
	    "close": "134.08"
	  }, {
	    "date": "2011-08-29",
	    "open": "132.67",
	    "high": "138.25",
	    "low": "132.30",
	    "close": "136.25"
	  }, {
	    "date": "2011-08-30",
	    "open": "139.49",
	    "high": "139.65",
	    "low": "137.41",
	    "close": "138.48"
	  }, {
	    "date": "2011-09-03",
	    "open": "139.94",
	    "high": "145.73",
	    "low": "139.84",
	    "close": "144.16"
	  }, {
	    "date": "2011-09-04",
	    "open": "144.97",
	    "high": "145.84",
	    "low": "136.10",
	    "close": "136.76"
	  }, {
	    "date": "2011-09-05",
	    "open": "135.56",
	    "high": "137.57",
	    "low": "132.71",
	    "close": "135.01"
	  }, {
	    "date": "2011-09-06",
	    "open": "132.01",
	    "high": "132.30",
	    "low": "130.00",
	    "close": "131.77"
	  }, {
	    "date": "2011-09-09",
	    "open": "136.99",
	    "high": "138.04",
	    "low": "133.95",
	    "close": "136.71"
	  }, {
	    "date": "2011-09-10",
	    "open": "137.90",
	    "high": "138.30",
	    "low": "133.75",
	    "close": "135.49"
	  }, {
	    "date": "2011-09-11",
	    "open": "135.99",
	    "high": "139.40",
	    "low": "135.75",
	    "close": "136.85"
	  }, {
	    "date": "2011-09-12",
	    "open": "138.83",
	    "high": "139.00",
	    "low": "136.65",
	    "close": "137.20"
	  }, {
	    "date": "2011-09-13",
	    "open": "136.57",
	    "high": "138.98",
	    "low": "136.20",
	    "close": "138.81"
	  }, {
	    "date": "2011-09-16",
	    "open": "138.99",
	    "high": "140.59",
	    "low": "137.60",
	    "close": "138.41"
	  }, {
	    "date": "2011-09-17",
	    "open": "139.06",
	    "high": "142.85",
	    "low": "137.83",
	    "close": "140.92"
	  }, {
	    "date": "2011-09-18",
	    "open": "143.02",
	    "high": "143.16",
	    "low": "139.40",
	    "close": "140.77"
	  }, {
	    "date": "2011-09-19",
	    "open": "140.15",
	    "high": "141.79",
	    "low": "139.32",
	    "close": "140.31"
	  }, {
	    "date": "2011-09-20",
	    "open": "141.14",
	    "high": "144.65",
	    "low": "140.31",
	    "close": "144.15"
	  }, {
	    "date": "2011-09-23",
	    "open": "146.73",
	    "high": "149.85",
	    "low": "146.65",
	    "close": "148.28"
	  }, {
	    "date": "2011-09-24",
	    "open": "146.84",
	    "high": "153.22",
	    "low": "146.82",
	    "close": "153.18"
	  }, {
	    "date": "2011-09-25",
	    "open": "154.47",
	    "high": "155.00",
	    "low": "151.25",
	    "close": "152.77"
	  }, {
	    "date": "2011-09-26",
	    "open": "153.77",
	    "high": "154.52",
	    "low": "152.32",
	    "close": "154.50"
	  }, {
	    "date": "2011-09-27",
	    "open": "153.44",
	    "high": "154.60",
	    "low": "152.75",
	    "close": "153.47"
	  }, {
	    "date": "2011-09-30",
	    "open": "154.63",
	    "high": "157.41",
	    "low": "152.93",
	    "close": "156.34"
	  }, {
	    "date": "2011-10-01",
	    "open": "156.55",
	    "high": "158.59",
	    "low": "155.89",
	    "close": "158.45"
	  }, {
	    "date": "2011-10-02",
	    "open": "157.78",
	    "high": "159.18",
	    "low": "157.01",
	    "close": "157.92"
	  }, {
	    "date": "2011-10-03",
	    "open": "158.00",
	    "high": "158.08",
	    "low": "153.50",
	    "close": "156.24"
	  }, {
	    "date": "2011-10-04",
	    "open": "158.37",
	    "high": "161.58",
	    "low": "157.70",
	    "close": "161.45"
	  }, {
	    "date": "2011-10-07",
	    "open": "163.49",
	    "high": "167.91",
	    "low": "162.97",
	    "close": "167.91"
	  }, {
	    "date": "2011-10-08",
	    "open": "170.20",
	    "high": "171.11",
	    "low": "166.68",
	    "close": "167.86"
	  }, {
	    "date": "2011-10-09",
	    "open": "167.55",
	    "high": "167.88",
	    "low": "165.60",
	    "close": "166.79"
	  }, {
	    "date": "2011-10-10",
	    "open": "169.49",
	    "high": "171.88",
	    "low": "153.21",
	    "close": "162.23"
	  }, {
	    "date": "2011-10-11",
	    "open": "163.01",
	    "high": "167.28",
	    "low": "161.80",
	    "close": "167.25"
	  }, {
	    "date": "2011-10-14",
	    "open": "167.98",
	    "high": "169.57",
	    "low": "163.50",
	    "close": "166.98"
	  }, {
	    "date": "2011-10-15",
	    "open": "165.54",
	    "high": "170.18",
	    "low": "165.15",
	    "close": "169.58"
	  }, {
	    "date": "2011-10-16",
	    "open": "172.69",
	    "high": "173.04",
	    "low": "169.18",
	    "close": "172.75"
	  }];

}
