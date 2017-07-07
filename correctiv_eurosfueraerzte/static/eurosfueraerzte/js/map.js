import L from 'leaflet';

const initializeMap = ({ center }) => {
  var map = new L.Map('efa__map').setView(center, 10);
  var tiles = new L.TileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(map);
}

export { initializeMap }
