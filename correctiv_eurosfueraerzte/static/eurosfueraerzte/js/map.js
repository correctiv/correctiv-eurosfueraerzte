import L from 'leaflet';

const CONTAINER = 'efa__map'
const TILES_URL = 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}@2x.png'
const TILES_ATTRIBUTION = `
  © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>,
  © <a href="https://carto.com/attribution">CARTO</a>`

const initializeMap = ({ center }) => {
  var map = new L.Map(CONTAINER, {
    center: center,
    scrollWheelZoom: false,
    zoom: 10
  });

  new L.TileLayer(TILES_URL, {
    attribution: TILES_ATTRIBUTION,
    maxZoom: 18
  }).addTo(map);
}

export { initializeMap }
