"use strict";

// initialize map
var map = new GMaps({
  div: '#map',
  lat: 23.031741,
  lng: 72.518850,
  zoom: 8
});

// draw route between 'origin' to 'destination'
map.drawRoute({
	origin: [23.031741, 72.518850],
    destination: [23.030240, 72.522498],
  travelMode: 'driving',
  strokeColor: '#131540',
  strokeOpacity: 0.6,
  strokeWeight: 6
});