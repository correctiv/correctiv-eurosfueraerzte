import { Map, tileLayer, marker, icon, markerLayer } from 'leaflet';
import markerClusterGroup from 'leaflet.markercluster';

const CONTAINER = 'efa__map';
const ICON_URL = '/static/eurosfueraerzte/img/map-marker.svg';
const TILES_URL = 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}@2x.png';
const TILES_ATTRIBUTION = `
  © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>,
  © <a href="https://carto.com/attribution">CARTO</a>`;

const initializeMap = ({ center, places }) => {
  const map = new Map(CONTAINER, {
    center: center,
    scrollWheelZoom: false,
    zoom: 15,
    minZoom: 13
  });

  const tiles = tileLayer(TILES_URL, {
    attribution: TILES_ATTRIBUTION
  });

  const markers = L.markerClusterGroup({
    singleMarkerMode: false,
    maxClusterRadius: 40
  });

  // TODO: Initialize with JSON (to be passed through from initialization)
  places.forEach(c => {
    markers.addLayer(marker(c.geo, {
      title: c.name,
      icon: icon({
        iconUrl: ICON_URL,
        iconSize: [20, 30],
        iconAnchor: [10, 5]
      })
    }).bindPopup(`<a href="${c.url}">${c.name}</a>`));
  });

  map.addLayer(tiles)
  map.addLayer(markers)
}

export { initializeMap }
