import L from 'leaflet';

var map = new L.Map('efa__map').setView([12.3, 123.4], 10);

var tiles = new L.TileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(map);
